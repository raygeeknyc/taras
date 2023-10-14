#!/usr/bin/python3

import logging
_LOGGING_LEVEL = logging.DEBUG
_LOGGING_LEVEL = logging.INFO
POLLING_DELAY_SECS = 0.1

import array
from collections import deque
import io
import json
import multiprocessing
from multiprocessingloghandler import ParentMultiProcessingLogHandler, ChildMultiProcessingLogHandler
import os
import queue
import signal
import spacy
import sys
import time
import threading
from vosk import Model, KaldiRecognizer

ENTITY_LABELS = ['PROPN']

SAMPLE_RATE = 44100


shutdown = False
def interrupt_handler(sig, frame):
    global shutdown_requestor
    global shutdown

    print('You pressed Ctrl+C!')
    shutdown = True
    shutdown_requestor()

class SpeechRecognizer(multiprocessing.Process):
    nlp = spacy.load("en_core_web_sm")

    def tag_speech(phrase:str) -> list:
        full_tokens = SpeechRecognizer.nlp(phrase.strip().lower())
        tagged_tokens = [(token.text, token.pos_) for token in full_tokens]
        return tagged_tokens

    def chunk_names(tokens:list) -> list:
        chunked_tokens = []
        entity_pos = None
        name = []
        for token in tokens:
            if token[1] in ENTITY_LABELS:
                if not entity_pos:
                    entity_pos = token[1]
                name.append(token[0])
            else:
                if name:
                    chunked_tokens.append((' '.join(name), entity_pos))
                    name = []
                chunked_tokens.append((token[0], token[1]))
                entity_pos = None
        if name:
            chunked_tokens.append((' '.join(name), entity_pos))
        return chunked_tokens

    def __init__(self, injector, speech_transcript, log_queue, logging_level):
        multiprocessing.Process.__init__(self)
        self._log_queue = log_queue
        self._logging_level = logging_level
        self.is_ready = multiprocessing.Event()
        self.is_ready.clear()
        self._exit = multiprocessing.Event()
        self._exit.clear()
        self._transcript = speech_transcript
        self._injections = injector
        self._stop_capturing = False
        self._stop_recognizing = False
        self._audio_packet_queue = queue.Queue()
        self.model = KaldiRecognizer(Model(lang="en-us"), SAMPLE_RATE)

    def _initLogging(self):
        handler = ChildMultiProcessingLogHandler(self._log_queue)
        logging.getLogger(str(os.getpid())).addHandler(handler)
        logging.getLogger(str(os.getpid())).setLevel(self._logging_level)

    def shutdown(self):
        logging.info("background received shutdown")
        self._exit.set()

    def run(self):
        self._initLogging()
        import sounddevice as sd  # pyaudio has problems in multiprocesses, this works around that
        self.sd = sd
        logging.debug("recognizer process active")
        self._capturer = threading.Thread(target=self._captureSound)
        self._recognizer = threading.Thread(target=self._recognizeSpeech)
        self._accepter = threading.Thread(target=self._acceptSpeechInjection)
        self._recognizer.start()
        self._capturer.start()
        self._accepter.start()
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        self.is_ready.set()
        logging.debug('speechrecognizer waiting for stop()')
        self._exit.wait()  # block until stop() is invoked
        logging.debug('speechrecognizer saw stop()')
        self._stopCapturing()
        self._stopRecognizing()
        self._capturer.join()
        self._recognizer.join()
        self._accepter.join()
        logging.debug("recognizer process terminating")
        sys.exit(0)

    def _stopCapturing(self):
        logging.debug("setting stop_capturing")
        self._stop_capturing = True
    
    def _stopRecognizing(self):
        logging.debug("setting stop_recognizing")
        self._stop_recognizing = True
    
    def _audioPacketCallback(self, indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            logging.warning('capture: %s' % status)
        self._audio_packet_queue.put(bytes(indata))

    def _captureSound(self):
        logging.info("starting capture thread")
        with self.sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize = 8000, device=None,
            dtype="int16", channels=1, callback=self._audioPacketCallback):

            while not self._stop_capturing:
                pass
        logging.info("capture thread terminated")

    def _interpretSpeech(self, speech:str):
        tagged_tokens = SpeechRecognizer.tag_speech(speech)
        tagged_chunks = SpeechRecognizer.chunk_names(tagged_tokens)
        logging.debug(tagged_chunks)
        self._transcript.put(tagged_chunks)

    def _acceptSpeechInjection(self):
        logging.info("starting injection thread")
        while not self._stop_recognizing:
            try:
                injected = self._injections.get(block=False)
                logging.debug("Injected speech: '{}'".format(injected))
                if injected:
                    self._interpretSpeech(injected)
            except queue.Empty:
                pass
            except Exception:
                logging.exception('Exception accepting injected speech')
        logging.info("injection thread terminated")

    def _recognizeSpeech(self):
        logging.info("starting recognizer thread")
        while not self._stop_recognizing:
            packet = self._audio_packet_queue.get()
            if self.model.AcceptWaveform(packet):
                phrase = json.loads(self.model.Result())['text']
                self._interpretSpeech(phrase)
            else:
                snippet=json.loads(self.model.PartialResult())['partial']
                logging.debug(str(snippet)+'...')
        logging.info("recognizer thread terminated")
 

def main(unused):
    global shutdown_requestor
    global shutdown

    shutdown_requestor = None

    log_stream = sys.stderr
    log_queue = multiprocessing.Queue(100)
    handler = ParentMultiProcessingLogHandler(logging.StreamHandler(log_stream), log_queue)
    logging.getLogger('').addHandler(handler)
    logging.getLogger('').setLevel(_LOGGING_LEVEL)

    parsed_speech = multiprocessing.Queue()
    injector = multiprocessing.Queue()
    recognition_worker = SpeechRecognizer(injector, parsed_speech, log_queue, logging.getLogger('').getEffectiveLevel())
    logging.debug("Starting speech recognition")
    recognition_worker.start()
    shutdown_requestor = recognition_worker.shutdown
    
    logging.debug("Waiting for speech recognizer to be ready")
    recognition_worker.is_ready.wait()
    signal.signal(signal.SIGINT, interrupt_handler)
    logging.debug("Waiting in main process")
    print("Listening, CTRL-C to exit")
    try:
        _phrase = 'What does John Doe do in the morning'
        injector.put(_phrase)
        while not shutdown:
            try:
                speech = parsed_speech.get(block=False)
                print("heard: {}".format(speech))
            except queue.Empty:
                pass
    except Exception as e:
        logging.exception("unexpected error running SpeechRecognizer")
    finally:
        logging.info("client terminating")
        logging.info("joining SpeechRecognizer to wait for exit")
        recognition_worker.join()

if __name__ == '__main__':
    print('running standalone recognizer')
    main(sys.argv)
    print('exiting')

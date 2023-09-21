#!/usr/bin/python3

import logging
_LOGGING_LEVEL = logging.DEBUG
POLLING_DELAY_SECS = 0.1

import array
from collections import deque
import io
import json
import multiprocessing
from multiprocessingloghandler import ParentMultiProcessingLogHandler, ChildMultiProcessingLogHandler
from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.tree import Tree
import os
import queue
import signal
import sys
import time
import threading
from vosk import Model, KaldiRecognizer

PERSON_LABEL = 'PERSON'

SAMPLE_RATE = 44100


def interrupt_handler(sig, frame):
    global shutdown_requestor

    print('You pressed Ctrl+C!')
    shutdown_requestor()

class SpeechRecognizer(multiprocessing.Process):

    def tag_speech(phrase:str) -> list:
        tagged_tokens = pos_tag(word_tokenize(phrase.strip()))
        return tagged_tokens

    def chunk_names(tokens:list) -> list:
        chunked_tokens = []
        chunks = ne_chunk(tokens)
        for chunk in chunks:
            logging.debug('chunk: {}: {}'.format(type(chunk),str(chunk)))
            if type(chunk) == Tree:
                name = ''
                for chunk_leaf in chunk.leaves():
                    name += chunk_leaf[0] + ' ' 
                name = name.strip()
                chunked_tokens.append((name,chunk.label()))
            else:
                chunked_tokens.append(chunk)
        return chunked_tokens

    def __init__(self, transcript, log_queue, logging_level):
        multiprocessing.Process.__init__(self)
        self._log_queue = log_queue
        self._logging_level = logging_level
        self.is_ready = multiprocessing.Event()
        self.is_ready.clear()
        self._exit = multiprocessing.Event()
        self._exit.clear()
        self._transcript, _ = transcript
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
        self._capturer = threading.Thread(target=self.captureSound)
        self._recognizer = threading.Thread(target=self.recognizeSpeech)
        self._recognizer.start()
        self._capturer.start()
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        self.is_ready.set()
        logging.debug('speechrecognizer waiting for stop()')
        self._exit.wait()  # block until stop() is invoked
        logging.debug('speechrecognizer saw stop()')
        self._stopCapturing()
        self._stopRecognizing()
        self._capturer.join()
        self._recognizer.join()
        self._transcript.close()
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

    def captureSound(self):
        logging.info("starting capture thread")
        with self.sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize = 8000, device=None,
            dtype="int16", channels=1, callback=self._audioPacketCallback):

            while not self._stop_capturing:
                pass
        logging.info("stopped capturing")

    def recognizeSpeech(self):
        logging.info("starting recognizer thread")
        phrase = 'What does John Doe do in the morning'
        tagged_tokens = SpeechRecognizer.tag_speech(phrase)
        tagged_chunks = SpeechRecognizer.chunk_names(tagged_tokens)
        logging.debug(tagged_chunks)
        self._transcript.send(tagged_chunks)
        while not self._stop_recognizing:
            packet = self._audio_packet_queue.get()
            if self.model.AcceptWaveform(packet):
                phrase = json.loads(self.model.Result())['text']
                tagged_tokens = SpeechRecognizer.tag_speech(phrase)
                tagged_chunks = SpeechRecognizer.chunk_names(tagged_tokens)
                logging.debug(tagged_chunks)
                self._transcript.send(tagged_chunks)
            else:
                snippet=json.loads(self.model.PartialResult())['partial']
                logging.debug(str(snippet)+'...')
        logging.info("stopped recognizing")
 

def main(unused):
    global shutdown_requestor

    shutdown_requestor = None

    log_stream = sys.stderr
    log_queue = multiprocessing.Queue(100)
    handler = ParentMultiProcessingLogHandler(logging.StreamHandler(log_stream), log_queue)
    logging.getLogger('').addHandler(handler)
    logging.getLogger('').setLevel(_LOGGING_LEVEL)

    transcript = multiprocessing.Pipe()
    recognition_worker = SpeechRecognizer(transcript, log_queue, logging.getLogger('').getEffectiveLevel())
    logging.debug("Starting speech recognition")
    recognition_worker.start()
    unused, parsed_speech = transcript
    unused.close()
    shutdown_requestor = recognition_worker.shutdown
    
    logging.debug("Waiting for speech recognizer to be ready")
    recognition_worker.is_ready.wait()
    signal.signal(signal.SIGINT, interrupt_handler)
    logging.debug("Waiting in main process")
    try:
        while True:
            try:
                speech = parsed_speech.recv()
                print("heard: {}".format(speech))
            except EOFError:
                break
    except Exception as e:
        logging.exception("unexpected error running SpeechRecognizer")
    finally:
        logging.info("joining SpeechRecognizer to wait for exit")
        recognition_worker.join()

if __name__ == '__main__':
    print('running standalone recognizer')
    main(sys.argv)
    print('exiting')

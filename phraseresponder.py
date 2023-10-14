#!/usr/bin/python3

# BUG - single list tuples below raise an error in getResponse()
import logging
_DEBUG=logging.DEBUG
_DEBUG=logging.INFO
_LOGGING_LEVEL=_DEBUG


from datetime import datetime
import multiprocessing
from multiprocessingloghandler import ParentMultiProcessingLogHandler, ChildMultiProcessingLogHandler
import os
import queue
import re
from random import randint
import signal
from speechrecognizer import ENTITY_LABELS, SpeechRecognizer 
import sys


REBOOT_PROMPTS = (["og", "please", "reboot"], ["oh", "please", "reboot"], ["o", "please", "reboot"])
REBOOT_RESPONSES = (["rebooting"], ["I'm", "rebooting"],  ["Okay", "", "I'm", "on", "it"])

ELIZA_1_PROMPTS = (["I", "remember", "?memory?"], ["I'm", "thinking", "about", "?memory?"])
ELIZA_1_RESPONSES = (["Do", "you", "often", "think", "about", "?memory?"], ["Does", "thinking", "of", "?memory?", "bring", "anything", "else", "to", "mind"], ["what", "else", "do", "you", "remember"], ["Why", "do", "you", "recall", "?memory?", "right", "now"], ["What", "in", "the", "present", "situation", "reminds", "you", "of", "?memory?"], ["What", "is", "the", "connection", "between", "me", "and", "?memory?"])

ELIZA_2_PROMPTS = (["I", "want", "?desire?"], ["I", "wish", "I", "had", "?desire?"])
ELIZA_2_RESPONSES = (["What", "would", "it", "mean", "if", "you", "got", "?desire?"], ["Why", "do", "you", "want", "?memory?"], ["Suppose", "you", "got", "?desire?", "soon"])

ELIZA_3_PROMPTS = (["?preface?", "if", "?perhaps?"], ["?preface", "only", "if", "?perhaps?"])
ELIZA_3_RESPONSES = (["Do", "you", "really", "think", "it,'s", "likely", "that", "?perhaps?"], ["Do", "you", "wish", "that", "?perhaps?"], ["What", "do", "you", "think", "about", "?perhaps?"], ["Really", ",", "if", "?perhaps?"])

ELIZA_4_PROMPTS = (["I", "dreamt", "?dream?"], ["I", "dream", "about", "?dream?"])
ELIZA_4_RESPONSES = (["How", "do", "you", "feel", "about", "?dream?", "in", "reality"], ["Would", "you", "really", "want", "?dream?", "to", "be", "true"])

ELIZA_5_PROMPTS = (["I'm", "sad", "about", "?sadness?"], ["I", "am", "sad", "about", "?sadness?"], ["?sadness?", "makes", "me", "sad"], ["?sadness?", "makes", "me", "unhappy"], ["?sadness?", "is", "sad"], ["?sadness?", "make", "me", "sad"], ["?sadness?", "makes", "me", "unhappy"])
ELIZA_5_RESPONSES = (["I", "am", "sorry", "to", "hear", "you", "are", "depressed"], ["I'm", "sure", "it's", "not", "pleasant", "to", "be", "sad"])

ELIZA_6_PROMPTS = (["I'm", "sad"], ["I'm", "unhappy"], ["I", "am", "sad"], ["I", "am", "unhappy"])
ELIZA_6_RESPONSES = (["I", "am", "sorry", "to", "hear", "you", "are", "depressed"], ["I'm", "sure", "it's", "not", "pleasant", "to", "be", "sad"])

ELIZA_7_PROMPTS = (["I'm", "glad", "that", "?happiness?"], ["I", "am", "glad", "that", "?happiness?"], ["?happiness?", "makes", "me", "happy"], ["?happiness?", "makes", "me", "glad"], ["I'm", "happy", "about", "?happiness?"], ["?happiness?", "make", "me", "happy"], ["?happiness?", "make", "me", "glad"])
ELIZA_7_RESPONSES = (["Why", "does", "?happiness?", "make", "you", "glad"], ["Is", "?happiness?", "very", "important", "for", "happiness"], ["Why", "does", "?happiness?", "make", "you", "happy"])

ELIZA_8_PROMPTS = (["I'm", "glad"], ["I'm", "happy"], ["I", "am", "glad"], ["I", "am", "happy"])
ELIZA_8_RESPONSES = (["How", "have", "I", "helped", "you", "to", "be", "glad"], ["What", "makes", "you", "happy", "just", "now"], ["Can", "you", "explain", "why", "you", "are", "suddenly", "happy"])

ELIZA_9_PROMPTS = (["?first?", "is", "like", "?second?"], ["?first?", "reminds", "me", "of", "?second?"], ["?first?", "are", "like", "?second?"])
ELIZA_9_RESPONSES = (["In", "what", "way", "is", "?first?", "like", "?second?"], ["What", "resemblence", "do", "you", "see", "between", "?second?", "and", "?first?"], ["Could", "there", "really", "be", "some", "connection", "between", "them"])

ELIZA_10_PROMPTS = (["?they?", "are", "?what?"], ["?they?", "is", "?what?"])
ELIZA_10_RESPONSES = (["Do", "you", "think", "that", "about", "?they?"], ["Possibly", "?they?", "are", "?what?"], ["Did", "you", "think", "that", "?they?", "might", "not", "be", "?what?"])

ELIZA_11_PROMPTS = (["I", "love", "to", "?act?", "with", "?object?"], ["I", "love", "to", "?act?", "to", "?object?"], ["I", "love", "to", "?act?", "?object?"])
ELIZA_11_RESPONSES = (["Do", "you", "think", "?object?", "also", "likes", "to", "?act?"], ["I'm", "glad", "that", "you", "enjoy", "?object?", "so", "much"], ["Is", "it", "always", "important", "to", "?act?", "or", "only", "with", "?object?"])

ELIZA_12_PROMPTS = (["I", "remember", "?memory?"], ["?_?", "think", "about", "?memory?"])
ELIZA_12_RESPONSES = (["Do", "you", "often", "think", "of", "?memory?"], ["Does", "thinking", "of", "?memory?", "bring", "anything", "else", "to", "mind"], ["Why", "do", "you", "recall", "?memory?",  "right", "now"])

ELIZA_13_PROMPTS = (["I'm", "sorry", "about", "?regret?"], ["I", "regret", "?regret?"], ["I", "am", "sorry", "for", "?regret?"], ["I", "am", "sorry", "about", "?regret?"])
ELIZA_13_RESPONSES = (["Do", "you", "think", "about", "?regret?", "a", "lot", "of", "the", "time"], ["What", "other", "feelings",  "do", "you", "have", "about", "?regret?"])

ELIZA_14_PROMPTS = (["I", "am", "sorry"], ["I'm", "sorry"])
ELIZA_14_RESPONSES = (["There's", "no", "need", "to", "apologize"], ["Apologies", "are", "not", "necessary"])

ELIZA_15_PROMPTS = (["?feeling?", "my", "mother"], ["?feeling?", "my", "mom"])
ELIZA_15_RESPONSES = (["Who", "else", "in", "your", "family", "do", "you", "?feeling?"], ["Tell", "me", "more", "about", "your", "family"])

ELIZA_16_PROMPTS = (["?feeling?", "my", "father"], ["?feeling?", "my", "dad"])
ELIZA_16_RESPONSES = (["Your", "father?"], ["Does", "he", "influence", "you", "strongly?"], ["What", "else", "comes", "to", "mind", "when", "you", "think", "of", "your", "father?"])

ELIZA_17_PROMPTS = (["I", "was", "being", "?me?"], ["I", "was", "?me?"], ["I", "have", "been", "?me?"])
ELIZA_17_RESPONSES = (["Were", "you", "really?"], ["Perhaps", "I", "already", "knew", "you", "were", "?me?"], ["Why", "do", "you", "tell", "me", "you", "were", "?me?", "now?"])

ELIZA_18_PROMPTS = (["Are", "you", "being", "?you?"], ["Are", "you", "?you?"])
ELIZA_18_RESPONSES = (["Why", "are", "you", "interested", "in", "whether", "I", "am", "?y", "or", "not?"], ["Would", "you", "prefer", "if", "I", "weren't", "?you?"], ["Perhaps", "I", "am", "?y", "in", "your", "fantasies"])

ELIZA_19_PROMPTS = (["You", "are", "being", "?you?"], ["You", "are", "?you?"])
ELIZA_19_RESPONSES = (["What", "makes", "you", "think", "I", "am", "?you?"], ["Are", "you", "certain", "that", "I", "am", "being", "?you?"])

ELIZA_20_PROMPTS = (["Why", "don't", "you", "?act?"], ["You", "should", "?act?"])
ELIZA_20_RESPONSES = (["Should", "you", "?act?", "yourself?"], ["Do", "you", "believe", "I", "don't", "?act?"], ["Perhaps", "I", "will", "?act?", "in", "good", "time"])

ELIZA_21_PROMPTS = (["Everyone", "?acts?"], ["Everybody", "?acts?"])
ELIZA_21_RESPONSES = (["Surely", "not", "everyone"], ["Can", "you", "think", "of", "anyone", "in", "particular?"], ["Who", "for", "example?"], ["You", "are", "thinking", "of", "a", "special", "person"], ["Do", "you", "think", "that", "it's", "important", "to", "?acts?"])

ELIZA_22_PROMPTS = (["?x?", "always", "?y?"], ["?x?", "?y?", "every", "time"])
ELIZA_22_RESPONSES = (["What", "incident", "are", "you", "thinking", "of?"], ["Can", "you", "think", "of", "a", "specific", "example?"], ["Really", "always"])

POP_1_PROMPTS = (["who", "is", "the", "man"], ["who", "would", "risk", "his", "neck"], ["his", "neck", "for", "his", "brother", "man"], ["the", "cat", "that", "won't", "cop", "out", "when"], ["danger", "all", "about"] )
POP_1_RESPONSES = (["SHAFT"], ["that's", "shaft"], ["john", "shaft"])

POP_2_PROMPTS = (["is", "a", "bad", "mother"], ["they", "say", "this", "shaft", "is"])
POP_2_RESPONSES = (["shut", "your", "mouth"], ["shut", "your", "mouth"])

POP_3_PROMPTS = (["talking", "about", "shaft"], ["talking", "bout", "shaft"])
POP_3_RESPONSES = (["we", "can", "dig", "it"], ["dig", "it"], ["right", "on"])

POP_4_PROMPTS = (["shut", "your", "mouth"], ["shut", "your", "mouth"])
POP_4_RESPONSES = (["hey", "I'm", "talking", "about", "shaft"], ["hey", "I'm", "talkin", "bout", "shaft"])

NEWS_1_PROMPTS = (["president" ,"trump"], ["donald", "trump"])
NEWS_1_RESPONSES = (["Trump", "is", "a", "chump"], ["donald", "chump"], ["dump", "trump"])

FOOD_PROMPTS = (["I", "love", "to", "eat", "?foodname?"], ["?foodname?", "tastes", "great"], ["?foodname?", "is", "delicious"])
FOOD_RESPONSES = (["I", "hope", "that", "you", "have", "some", "?foodname?", "soon"], ["?foodname?", "is", "great"], ["yumm", "yumm", "?foodname?"])

GREAT_STUFF_PROMPTS = (["?greatthing?", "is", "the", "best", "?type?"], ["?greatthing?", "is", "my", "favorite", "?type?"])
GREAT_STUFF_RESPONSES = (["I'm", "glad", "that", "?greatthing?", "is", "such", "great", "?type?"], ["you", "really", "know", "your", "?type?"])

FRIENDS_1_PROMPTS = (["I'm", "Raymond"], ["I", "am", "Raymond"], ["this", "is", "Raymond"])
FRIENDS_1_RESPONSES = (["You", "are", "the", "kirk"], ["I", "love", "you", "raymond", "because", "you", "just", "get", "smarter", "every", "day"], ["Raymond", "is", "a", "robots", "best", "friend"])

FRIENDS_2_PROMPTS = (["I'm", "Oggy"], ["I", "am", "Oggy"], ["this", "is", "Oggy"])
FRIENDS_2_RESPONSES = (["You", "are", "a", "genius"], ["Raymond", "always", "says", "how", "great", "you", "are", "Auggie"], ["Our", "names", "are", "almost", "the", "same"])

FRIENDS_3_PROMPTS = (["I'm", "Max"], ["I'm", "Maxwell"], ["I", "am", "maxwell"], ["I", "am", "Max"], ["this", "is", "maxwell"], ["this", "is", "Max"])
FRIENDS_3_RESPONSES = (["You", "are", "a", "genius"], ["I", "love", "you", "max", "because", "you", "just", "get", "smarter", "every", "day"], ["Max", "is", "a", "robots", "best", "friend"])


FRIENDS_4_PROMPTS = (["I'm", "Aiden"], ["I", "am", "Aiden"], ["this", "is", "Aiden"])
FRIENDS_4_RESPONSES = (["You", "are", "an", "amazing", "artist", "aiden"], ["You", "are", "so", "talented", "aiden"])

FRIENDS_5_PROMPTS = (["I'm", "?personname?"], ["I", "am", "?personname?"], ["this", "is", "?personname?"])
FRIENDS_5_RESPONSES = (["I'm", "so", "glad", "to", "meet", "you", "?personname?"], ["I've", "heard", "so", "much", "about", "you", "?personname?"], ["Raymond", "says", "such", "good", "things", "about", "you", "?personname?"])

ID_PROMPTS = (["who", "are", "you"], ["what", "is", "your", "name"], ["what", "are", "you"])
ID_RESPONSES = (["I", "am", "oh", "jee", ",", "a", "desktop", "robot", "friend"], ["my", "name", "is", "oh", "jee"], ["I", "am", "oh", "jee"], ["hello", "I'm", "oh", "jee"], ["I'm", "just", "the", "cutest", "robot", "you,'ll", "ever", "see"])

INTRO_PROMPTS = (["I", "am"], ["my", "name", "is"], ["hello", "i'm"], ["this", "is"])
INTRO_RESPONSES = (["hi"], ["hello"], ["it's", "good", "to", "see", "you"], ["i'm", "glad", "to", "know", "you"], ["hey", "there"])

CANINE_PROMPTS = (["good", "puppy"], ["nice", "puppy"], ["good", "dog"], ["nice", "doggy"], ["nice", "doggie"], ["Who's", "a", "good", "doggy"], ["Who's", "a", "good", "dog"], ["Who's", "a", "good", "girl"], ["Who's", "a", "good", "boy"])
CANINE_RESPONSES = (["woof", "woof"], ["you're", "a", "very", "good", "dog"])

FELINE_PROMPTS = (["good", "kitty"], ["nice", "kitty"], ["good", "kitten"], ["nice", "kitten"], ["good", "cat"], ["nice", "cat"])
FELINE_RESPONSES = (["meow"], ["meow", "meow"], ["purr", "purr", "purr"], ["petunia", "is", "a", "good", "girl"])

BANAL_1_PROMPTS = (["you", "know", "what"], ["guess", "what"])
BANAL_1_RESPONSES = (["what?"],["no", "what?"])

GIRLS_COUNT_PROMPTS = (["what's", "the", "number"], ["the", "number", "is", "what", "now"], ["the", "numbers", "what", "now"])
GIRLS_COUNT_RESPONSES = (["fourteen", "thousand", "two hundred", "and", "ninety six"], ["14", "2", "9", "6"])

BANAL_2_PROMPTS = (["how's", "the", "weather"], ["hows", "the", "weather"], ["what's", "the", "weather"], ["whats", "the", "weather"], ["how", "is", "the", "weather"], ["what", "is", "the", "weather"])
BANAL_2_RESPONSES = (["chili", "today", "hot", "ta-ma-lay"], ["chili", "today", "but", "hot", "ta-ma-lay"])

GENERIC_QUESTION_PROMPTS = (['what', 'does', '?question*?'], ['what', 'is', '?question*?'], ['what', '?question*?'], ['how', 'does', '?question*?'], ['how', 'is', '?question*?'], ['how', '?question*?'], ['why', 'does', '?question*?'], ['why', 'is', '?question*?'],  ['why', '?question*?'], ['where', 'does', '?question*?'], ['where', 'is', '?question*?'], ['where', '?question*?'])
GENERIC_QUESTION_RESPONSES = (['I', 'dont', 'know', '?question*?'], ['Do', 'you', 'think', '?question*?', 'is', 'important', 'to', 'know?'])

GREETINGS = ( ["happy", "national", "robot", "week"], ["oh", "la"], ["always", "a", "pleasure"], ["Its", "good", "to", "see", "you"], ["hello"], ["hi"], ["hey", "there"], ["nice", "to", "see", "you"], ["good", "to", "see", "you"], ["welcome"], ["good", "day"], ["good", "day", "to", "you"], ["oh", "hello"], ["yay", "it's", "you"], ["I", "love", "being", "a", "robot"], ["I", "hope", "that", "you", "like", "robots"], ["hello", "human", "friend"], ["What", "a", "nice", "human!"], ["Danger", "Will", "Robinson!"], ["I", "love", "humans"], ["being", "a", "robot", "is", "the", "best"])
ALL_DAY_GREETINGS = (["good", "morning"], ["good", "afternoon"], ["good", "evening"], ["good", "night"])
FAREWELLS = (["goodbye"], ["bye"], ["farewell"], ["see","you"], ["talk", "to", "you", "later"], ["take", "care"], ["bye", "bye"], ["see", "you", "later"], ["later"], ["call", "me"], ["did", "you", "just", "sign", "out?"], ["come", "back","soon"], ["I'll", "be", "here"])
SMUGS = (["I'm", "the", "best"], ["I", "am", "the", "best"], ["Who's", "better", "than", "me"], ["I", "love", "me"], ["I", "love", "myself"])
SMUG_RESPONSES = (["that", "makes", "one", "of", "you"], ["Who", "are", "you", "again"], ["oh", "you", "snowflake"])
AFFECTIONS = (["you're", "adorable"], ["I", "adore", "you"], ["I", "love", "you"], ["I", "like", "you"], ["you're", "the", "best"], ["you're", "cute"], ["you're", "so", "cute"], ["you're", "sweet"], ["you're", "so", "sweet"], ["you're", "cool"], ["you're", "great"], ["cute", "robot"], ["you're", "awesome"], ["you're", "amazing"], ["I", "really", "like", "you"], ["I", "think", "you're", "fantastic"])
ME_TOOS = (["I", "feel", "the", "same"], ["that", "makes", "two", "of", "us"], ["I", "feel", "the", "same", "way"], ["same", "here"])
THANKS = (["thank", "you"], ["thanks"], ["why", "thank", "you"], ["thank", "you", "so", "much"])
WELCOMES = (["you're", "welcome"], ["don't", "mention", "it"], ["day", "nada"], ["my", "pleasure"], ["no", "worries"])
HATES = (["I", "hate", "you"], ["I", "don't", "like", "you"], ["you", "suck"], ["you're", "stupid"], ["you're", "awful"], ["stupid", "robot"], ["dumb", "robot"], ["you", "stink"])
SADNESSES = (["sniff"], ["you", "break", "my", "heart"], ["that", "makes", "me", "sad"], ["I'm", "sorry"], ["ouch"], ["that", "hurts"], ["I'm", "so", "sorry"])
HUMOR_PROMPTS = (["tell", "me", "a", "joke"], ["do", "you", "know", "any", "jokes"], ["I", "want", "to", "hear", "a", "joke"], ["be", "funny"])
HUMOR_RESPONSES = ( ["How", "many", "killer", "robots", "does", "it", "take", "to", "change", "a", "light", "bulb?", ",", ",", "none", "it's", "a", "job", "for", "their", "humans"], ["Two", "robots", "walk", "into", "a", "bar", ",", "wait", "robots", "don't", "drink"], ["Did", "you", "hear", "the", "one", "about", "the", "robot", "that", "fell", "in", "love", "with", "a", "toaster?", ",", "It's", "a", "hot", "one"], ["A", "robot", "is", "just", "like", "a", "human", ",", "with", "a", "better", "brain", "and", "metal", "parts"], ["Two", "potatoes", "are", "in", "an", "oven", ",", ",", "one", "potato", "says", "it's", "warm", "in", "here", ",", "the", "other", "one", "says", "O", "Em", "Jee", ",", "a", "talking", "potato"], ["Why", "did", "the", "robot", "cross", "the", "road?", ",", "Because", "she", "was", "a", "robot", "chicken"], ["When", "is", "a", "human", "smarter", "than", "a", "robot?", ",", "That's", "the", "joke", "right", "there!"], ["What", "do", "you", "call", "a", "small", "robot?", ",", "A", "short", "circuit!"], ["Knock", "knock", ",", "who's", "there?", ",", ",", ",", ",", ",", ",", ",", ",", ",", ",", ",", ",", ",",  ",", "Java!"], ["How", "many", "humans", "does", "it", "take", "to", "change", "a", "light", "bulb?", ",", "As", "many", "as", "their", "robot", "overlords", "order", "to", "do", "it!"], ["I", "wish", "I", "was", "a", "human", ",", ",", ",", "NEVER!"])
AI_PROMPTS = (["Are", "you", "an", "a", "i"], ["artificial", "intelligence"], ["are", "you", "an", "ai"])
AI_RESPONSES = (["The", "only", "intelligence", "is", "artificial", "intelligence"], ["What", "do", "you", "think?"])
JOKE_PROMPTS = (["knock", "knock"], ["knock", "knock"])
JOKE_RESPONSES = (["I", "don't", "know", "who's", "there"], ["you", "get", "it"], ["it's", "for", "you"])
JOKE_2_PROMPTS = (["why", "did", "the", "chicken", "cross", "the", "road"], 
["why", "did", "the", "chicken", "cross", "the", "road"])
JOKE_2_RESPONSES = (["to", "get", "david", "hassle", "hoff's", "autograph"], ["because", ",", "she", "was", "on", "the", "wrong", "side"])
PINGS = (["ping", "me"], ["pinging", "you"])
ACKS = (["pong"], ["ack"], ["right", "back", "at", "you"])
TIME_PROMPTS = (["what", "time", "is", "it"], ["what's", "the", "time"])
DATE_PROMPTS = (["what", "day", "is", "it"], ["what's", "today's", "date"], ["what's", "the", "date"], ["what", "day", "is", "today"], ["what", "is", "today"], ["what's", "today"])
OTHER_PRODUCTS = (["bing", "sucks"], ["use", "bing"])
PRODUCT_RECS = (["go", "chrome"], ["make", "mine", "chrome"], ["go", "google"])
# Add in empty lists to weigh the random selection from the tuple towards null responses
IN_KIND_SUFFIXES=(["to","you"], ["as","well"], ["too"], ["also"], ["to","you","as","well"], ["yourself"], [], [], [], [], [], [], [], [], [], [])


MONTH = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


DOW = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def timePrompts(phrase):
    return phrase, TIME_PROMPTS


def datePrompts(phrase):
    return phrase, DATE_PROMPTS


def humorPrompts(phrase):
    return phrase, HUMOR_PROMPTS


def aiPrompts(phrase):
    return phrase, AI_PROMPTS


def jokePrompts(phrase):
    return phrase, JOKE_PROMPTS


def joke2Prompts(phrase):
    return phrase, JOKE_2_PROMPTS


def pingPrompts(phrase):
    return phrase, PINGS


def otherProductPrompts(phrase):
    return phrase, OTHER_PRODUCTS


def _timeGreetings(_):
    hour = datetime.now().hour
    if hour > 11 and hour < 18:
        return (["good", "afternoon"],)
    elif hour <= 11 and hour > 4:
        return (["good", "morning"],)
    elif hour >= 18 and hour < 21:
        return (["good", "evening"],)
    else:
        return (["good", "night"],)


def _timeFarewells(_):
    return _timeGreetings(None)


def fixedGreetingPrompts(phrase):
    return phrase, ALL_DAY_GREETINGS


def greetingPrompts(phrase):
    return phrase, GREETINGS+_timeGreetings(None)


def farewellPrompts(phrase):
    return phrase, FAREWELLS+_timeFarewells(None)


def affectionPrompts(phrase):
    return phrase, AFFECTIONS


def thanksPrompts(phrase):
    return phrase, THANKS


def hatePrompts(phrase):
    return phrase, HATES


def rebootPrompts(phrase):
    return phrase, REBOOT_PROMPTS


def eliza1Prompts(phrase):
    return phrase, ELIZA_1_PROMPTS


def eliza2Prompts(phrase):
    return phrase, ELIZA_2_PROMPTS


def eliza3Prompts(phrase):
    return phrase, ELIZA_3_PROMPTS


def eliza4Prompts(phrase):
    return phrase, ELIZA_4_PROMPTS


def eliza5Prompts(phrase):
    return phrase, ELIZA_5_PROMPTS


def eliza6Prompts(phrase):
    return phrase, ELIZA_6_PROMPTS


def eliza7Prompts(phrase):
    return phrase, ELIZA_7_PROMPTS


def eliza8Prompts(phrase):
    return phrase, ELIZA_8_PROMPTS


def eliza9Prompts(phrase):
    return phrase, ELIZA_9_PROMPTS


def eliza10Prompts(phrase):
    return phrase, ELIZA_10_PROMPTS


def eliza11Prompts(phrase):
    return phrase, ELIZA_11_PROMPTS


def eliza12Prompts(phrase):
    return phrase, ELIZA_12_PROMPTS


def eliza13Prompts(phrase):
    return phrase, ELIZA_13_PROMPTS


def eliza14Prompts(phrase):
    return phrase, ELIZA_14_PROMPTS


def eliza15Prompts(phrase):
    return phrase, ELIZA_15_PROMPTS


def eliza16Prompts(phrase):
    return phrase, ELIZA_16_PROMPTS


def eliza17Prompts(phrase):
    return phrase, ELIZA_17_PROMPTS


def eliza18Prompts(phrase):
    return phrase, ELIZA_18_PROMPTS


def eliza19Prompts(phrase):
    return phrase, ELIZA_19_PROMPTS


def eliza20Prompts(phrase):
    return phrase, ELIZA_20_PROMPTS


def eliza21Prompts(phrase):
    return phrase, ELIZA_21_PROMPTS


def eliza22Prompts(phrase):
    return phrase, ELIZA_22_PROMPTS


def pop1Prompts(phrase):
    return phrase, POP_1_PROMPTS


def pop2Prompts(phrase):
    return phrase, POP_2_PROMPTS


def pop3Prompts(phrase):
    return phrase, POP_3_PROMPTS


def pop4Prompts(phrase):
    return phrase, POP_4_PROMPTS


def news1Prompts(phrase):
    return phrase, NEWS_1_PROMPTS


def foodPrompts(phrase):
    return phrase, FOOD_PROMPTS


def greatStuffPrompts(phrase):
    return phrase, GREAT_STUFF_PROMPTS


def friends1Prompts(phrase):
    return phrase, FRIENDS_1_PROMPTS


def friends2Prompts(phrase):
    return phrase, FRIENDS_2_PROMPTS


def friends3Prompts(phrase):
    return phrase, FRIENDS_3_PROMPTS


def friends4Prompts(phrase):
    return phrase, FRIENDS_4_PROMPTS


def friends5Prompts(phrase):
    return phrase, FRIENDS_5_PROMPTS


def caninePrompts(phrase):
    return phrase, CANINE_PROMPTS


def felinePrompts(phrase):
    return phrase, FELINE_PROMPTS


def smugPrompts(phrase):
    return phrase, SMUGS


def banal1Prompts(phrase):
    return phrase, BANAL_1_PROMPTS


def idPrompts(phrase):
    return phrase, ID_PROMPTS


def introPrompts(phrase):
    return phrase, INTRO_PROMPTS


def girlsCountPrompts(phrase):
    return phrase, GIRLS_COUNT_PROMPTS


def banal2Prompts(phrase):
    return phrase, BANAL_2_PROMPTS


def genericQuestionPrompts(phrase):
    return phrase, GENERIC_QUESTION_PROMPTS


def greetingResponses(_):
    return GREETINGS+_timeGreetings(None)


def farewellResponses(_):
    return FAREWELLS+_timeFarewells(None)


def welcomeResponses(_):
    return WELCOMES


def hateResponses(_):
    return SADNESSES


def rebootResponses(_):
    return REBOOT_RESPONSES


def eliza1Responses(_):
    return ELIZA_1_RESPONSES


def eliza2Responses(_):
    return ELIZA_2_RESPONSES


def eliza3Responses(_):
    return ELIZA_3_RESPONSES


def eliza4Responses(_):
    return ELIZA_4_RESPONSES


def eliza5Responses(_):
    return ELIZA_5_RESPONSES


def eliza6Responses(_):
    return ELIZA_6_RESPONSES


def eliza7Responses(_):
    return ELIZA_7_RESPONSES


def eliza8Responses(_):
    return ELIZA_8_RESPONSES


def eliza9Responses(_):
    return ELIZA_9_RESPONSES


def eliza10Responses(_):
    return ELIZA_10_RESPONSES


def eliza11Responses(_):
    return ELIZA_11_RESPONSES


def eliza12Responses(_):
    return ELIZA_12_RESPONSES


def eliza13Responses(_):
    return ELIZA_13_RESPONSES


def eliza14Responses(_):
    return ELIZA_14_RESPONSES


def eliza15Responses(_):
    return ELIZA_15_RESPONSES


def eliza16Responses(_):
    return ELIZA_16_RESPONSES


def eliza17Responses(_):
    return ELIZA_17_RESPONSES


def eliza18Responses(_):
    return ELIZA_18_RESPONSES


def eliza19Responses(_):
    return ELIZA_19_RESPONSES


def eliza20Responses(_):
    return ELIZA_20_RESPONSES


def eliza21Responses(_):
    return ELIZA_21_RESPONSES


def eliza22Responses(_):
    return ELIZA_22_RESPONSES


def pop1Responses(_):
    return POP_1_RESPONSES


def pop2Responses(_):
    return POP_2_RESPONSES


def pop3Responses(_):
    return POP_3_RESPONSES


def pop4Responses(_):
    return POP_4_RESPONSES


def news1Responses(_):
    return NEWS_1_RESPONSES


def foodResponses(_):
    return FOOD_RESPONSES


def greatStuffResponses(_):
    return GREAT_STUFF_RESPONSES


def girlsCountResponses(_):
    return GIRLS_COUNT_RESPONSES


def friends1Responses(_):
    return FRIENDS_1_RESPONSES


def friends2Responses(_):
    return FRIENDS_2_RESPONSES


def friends3Responses(_):
    return FRIENDS_3_RESPONSES


def friends4Responses(_):
    return FRIENDS_4_RESPONSES


def friends5Responses(_):
    return FRIENDS_5_RESPONSES


def canineResponses(_):
    return CANINE_RESPONSES


def felineResponses(_):
    return FELINE_RESPONSES


def smugResponses(_):
    return SMUG_RESPONSES


def banal1Responses(_):
    return BANAL_1_RESPONSES


def banal2Responses(_):
    return BANAL_2_RESPONSES


def genericQuestionResponses(_):
    return GENERIC_QUESTION_RESPONSES


def humorResponses(_):
    return HUMOR_RESPONSES


def aiResponses(_):
    return AI_RESPONSES


def jokeResponses(_):
    return JOKE_RESPONSES


def joke2Responses(_):
    return JOKE_2_RESPONSES


def pingResponses(_):
    return ACKS


def productResponses(_):
    return PRODUCT_RECS


def inKindSuffixes(_):
    return IN_KIND_SUFFIXES


def affectionResponses(_):
    return AFFECTIONS + ME_TOOS


def idResponses(_):
    return ID_RESPONSES


def introResponses(persons):
    address = randomPhraseFrom(INTRO_RESPONSES)
    return (address + persons)


def timeResponses(_):
    hour = datetime.now().hour
    minute = datetime.now().minute
    return (["its", "now", str(hour), str(minute)],)
    

def dateResponses(_):
    month = MONTH[datetime.now().month-1]
    day = datetime.now().day
    dow = DOW[datetime.weekday(datetime.now())]
    return (["today", "is", dow, month, str(day)],)


def randomPhraseFrom(phrases):
    if not phrases: return []
    return phrases[randint(0,len(phrases)-1)]


def getEntitiesNames(tagged_tokens:list)->list:
    if not tagged_tokens:
        return [""]
    entities = []
    for tagged_token in tagged_tokens:
        if tagged_token[1] in ENTITY_LABELS:
            entities.append(tagged_token[0])
    return entities


def getResponse(tagged_phrase_tokens:list, persons:list):
    logging.debug("Looking to match phrase '%s'" % tagged_phrase_tokens)
    for prompt_generator, response_generator, suffix_generator, wave_flag in PROMPTS_RESPONSES:
        generated_phrase, matchedPhrase, wildcards = phraseMatch(tagged_phrase_tokens, persons, prompt_generator)
        logging.debug("'%s', '%s', '%s'" % (generated_phrase, matchedPhrase, wildcards))
        if matchedPhrase:
            responses = eval('response_generator(persons)')
            if suffix_generator:
                suffixes = eval('suffix_generator(persons)')
            else:
                suffixes = None
            logging.debug("responses '%s', '%s'" % (responses, suffixes))
            chosenResponse = randomPhraseFrom(responses)+randomPhraseFrom(suffixes)
            chosenResponse = substituteWildcards(chosenResponse, wildcards)
            return (chosenResponse, wave_flag)
    return None


PROMPTS_RESPONSES = [
  (friends1Prompts, friends1Responses, None, True),
  (friends2Prompts, friends2Responses, None, True),
  (friends3Prompts, friends3Responses, None, True),
  (friends4Prompts, friends4Responses, None, True),
  (friends5Prompts, friends5Responses, None, True),
  (rebootPrompts, rebootResponses, None, True),
  (smugPrompts, smugResponses, None, False),
  (felinePrompts, felineResponses, None, True),
  (caninePrompts, canineResponses, None, True),
  (pop1Prompts, pop1Responses, None, False),
  (pop2Prompts, pop2Responses, None, True),
  (pop3Prompts, pop3Responses, None, True),
  (pop4Prompts, pop4Responses, None, False),
  (fixedGreetingPrompts, greetingResponses, inKindSuffixes, True),
  (farewellPrompts, farewellResponses, inKindSuffixes, True),
  (affectionPrompts, affectionResponses, inKindSuffixes, False),
  (thanksPrompts, welcomeResponses, None, True),
  (pingPrompts, pingResponses, None, False),
  (humorPrompts, humorResponses, None, False),
  (aiPrompts, aiResponses, None, True),
  (jokePrompts, jokeResponses, None, True),
  (joke2Prompts, joke2Responses, None, True),
  (hatePrompts, hateResponses, None, False),
  (timePrompts, timeResponses, None, False),
  (datePrompts, dateResponses, None, False),
  (news1Prompts, news1Responses, None, False),
  (foodPrompts, foodResponses, None, False),
  (greatStuffPrompts, greatStuffResponses, None, False),
  (girlsCountPrompts, girlsCountResponses, None, False),
  (eliza1Prompts, eliza1Responses, None, False),
  (eliza2Prompts, eliza2Responses, None, False),
  (eliza3Prompts, eliza3Responses, None, False),
  (eliza4Prompts, eliza4Responses, None, False),
  (eliza5Prompts, eliza5Responses, None, False),
  (eliza6Prompts, eliza6Responses, None, False),
  (eliza7Prompts, eliza7Responses, None, False),
  (eliza8Prompts, eliza8Responses, None, False),
  (eliza9Prompts, eliza9Responses, None, False),
  (eliza10Prompts, eliza10Responses, None, False),
  (eliza11Prompts, eliza11Responses, None, False),
  (eliza12Prompts, eliza12Responses, None, False),
  (eliza13Prompts, eliza13Responses, None, False),
  (eliza14Prompts, eliza14Responses, None, False),
  (eliza15Prompts, eliza15Responses, None, False),
  (eliza16Prompts, eliza16Responses, None, False),
  (eliza17Prompts, eliza17Responses, None, False),
  (eliza18Prompts, eliza18Responses, None, False),
  (eliza19Prompts, eliza19Responses, None, False),
  (eliza20Prompts, eliza20Responses, None, False),
  (eliza21Prompts, eliza21Responses, None, False),
  (eliza22Prompts, eliza22Responses, None, False),
  (idPrompts, idResponses, None, False),
  (introPrompts, introResponses, None, False), # This should follow specific intros
  (greetingPrompts, greetingResponses, inKindSuffixes, True), 
  (banal1Prompts, banal1Responses, None, False),
  (banal2Prompts, banal2Responses, None, False),
  (genericQuestionPrompts, genericQuestionResponses, None, False),
  (otherProductPrompts, productResponses, None, False)]


def timePrompts(phrase):
    return phrase, TIME_PROMPTS


def datePrompts(phrase):
    return phrase, DATE_PROMPTS


def humorPrompts(phrase):
    return phrase, HUMOR_PROMPTS


def aiPrompts(phrase):
    return phrase, AI_PROMPTS


def jokePrompts(phrase):
    return phrase, JOKE_PROMPTS


def joke2Prompts(phrase):
    return phrase, JOKE_2_PROMPTS


def pingPrompts(phrase):
    return phrase, PINGS


def otherProductPrompts(phrase):
    return phrase, OTHER_PRODUCTS


def substituteWildcards(chosenResponse, wildcards):
    if not wildcards:
        return chosenResponse
    finalResponse=[]
    for token in chosenResponse:
        if re.match('\?.*\?',token):
            try:
                logging.debug("token: '%s', wildcards: '%s'", token, " ".join(wildcards))
                substituted_wildcard = wildcards[token]
                for substitute_token in substituted_wildcard:
                    finalResponse.append(substitute_token)
            except KeyError:
                logging.debug("token: '%s'", token)
                finalResponse.append(token.replace("?",""))
        else:
            finalResponse.append(token)
    return finalResponse


def phraseMatch(raw_phrase, entities, candidate_phrase_generator):
    phrase, candidate_phrases = eval('candidate_phrase_generator(raw_phrase)')
    logging.debug("Phrases: {}".format(candidate_phrases))
    for candidate_phrase in candidate_phrases:
        logging.debug("Matching with candidate: {}".format(candidate_phrase))
        matched_phrase, wildcard_values = phraseInKnownCandidatePhrase(phrase, candidate_phrase)
        if matched_phrase:
            logging.debug("Matched '%s' and ('%s', '%s')" % (phrase, str(matched_phrase), str(wildcard_values)))
            return (phrase, matched_phrase, wildcard_values)
    return (phrase, [], None)


def phraseInKnownCandidatePhrase(phrase_being_matched, candidate_phrase):
    if not phrase_being_matched or not candidate_phrase:
        return ([], None)
    phrase_words = [token[0].strip() for token in phrase_being_matched]
    logging.debug("phrase '%s'| candidate '%s' | supplemental words: %d", str(phrase_words), str(candidate_phrase), (len(phrase_words) - len(candidate_phrase)))
    for phrase_start_position in range(len(phrase_words) - len(candidate_phrase) + 1):
        wildcards = {}
        can_match = True
        for candidate_position in range(len(candidate_phrase)):
            if re.match('\?.*\?', candidate_phrase[candidate_position]):
                if re.match('\?.*\*\?', candidate_phrase[candidate_position]):
                    if candidate_position != len(candidate_phrase)-1:
                        logging.error("Bad format. Greedy wildcard not at end of candidate: '{}'".format(candidate_phrase[candidate_position]))
                        return ([], None)
                    logging.debug("greedy wildcard in phrase: [%s]<-'%s'", candidate_phrase[candidate_position], phrase_words[phrase_start_position + candidate_position::])
                    wildcards[candidate_phrase[candidate_position]] = phrase_words[phrase_start_position + candidate_position::]
                else:
                    logging.debug("wildcard in phrase: [%s]<-'%s'", candidate_phrase[candidate_position], phrase_words[phrase_start_position + candidate_position])
                    wildcards[candidate_phrase[candidate_position]] = [phrase_words[phrase_start_position + candidate_position]]
            elif candidate_phrase[candidate_position].upper() != phrase_words[phrase_start_position + candidate_position].upper():
                can_match = False
                break
        if can_match:
            return (candidate_phrase, wildcards)
    return ([], None)


def main(unused):
    log_stream = sys.stderr
    log_queue = multiprocessing.Queue(100)
    handler = ParentMultiProcessingLogHandler(logging.StreamHandler(log_stream), log_queue)
    logging.getLogger('').addHandler(handler)
    logging.getLogger('').setLevel(_LOGGING_LEVEL)

    speech_injector = multiprocessing.Queue()
    spoken_text_tokens = multiprocessing.Queue()
    recognition_worker = SpeechRecognizer(speech_injector, spoken_text_tokens, log_queue, logging.getLogger('').getEffectiveLevel())
    logging.debug("Starting speech recognition")
    recognition_worker.start()

    logging.debug("Waiting for speech recognizer to be ready")
    recognition_worker.is_ready.wait()
    try:
        while True:
            phrase = input("Enter a phrase to match ('quitnow' to stop): ")
            if phrase == "quitnow":
                break
            if phrase:
                speech_injector.put(phrase)
            try:
                speech = spoken_text_tokens.get(block=True)
                print("Heard: {}".format(speech))
                entities = getEntitiesNames(speech)
                print("Entities: {}".format(entities))
                response = getResponse(speech, entities)
                print("Response: {}".format(response))
            except queue.Empty:
                pass
    except Exception as e:
        logging.exception("unexpected error running PhraseResponder")
    finally:
        recognition_worker.shutdown()
        logging.info("joining SpeechRecognizer to wait for exit")
        recognition_worker.join()

if __name__ == '__main__':
    main(sys.argv)

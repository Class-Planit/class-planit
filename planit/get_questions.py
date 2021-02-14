# Run in python console
import nltk; nltk.download('stopwords')
import re
import numpy as np
import pandas as pd
from pprint import pprint
from .models import *

# spacy for lemmatization
import spacy

# Plotting tools
import pyLDAvis
import pyLDAvis.gensim  # don't skip this
import matplotlib.pyplot as plt
from textblob import TextBlob

# Enable logging for gensim - optional
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.ERROR)

import warnings
warnings.filterwarnings("ignore",category=DeprecationWarning)

# NLTK Stop words
from nltk.corpus import stopwords
stop_words = stopwords.words('english')
stop_words.extend(['from', 'subject', 're', 'edu', 'use'])
import spacy
import en_core_web_sm
nlp = en_core_web_sm.load()
from gensim.summarization.summarizer import summarize 
from gensim.summarization import keywords 
from sklearn.metrics import pairwise_distances_argmin
import nltk
from nltk import tokenize


line = ['Civil War', '1861- 1865" Civil War "Union (North vs. Confederacy (South) Jefferson Davis- President of the Confederacy Abraham Lincoln- President of the United States" "1861- 1865" Civil War War between the North and the South']


def generate_multichoice(line):
    pass


def generate_vocab_match(line):
    pass


def generate_vocab_match(line):
    pass


def generate_spelling(line):
    pass


def generate_true_false(line):
    pass


def generate_short_answer(line):
    pass


def generate_questions_text(line):
    pass


def generate_questions_topic(topic):
    topic = topicInformation.objects.get(id=topic)
    term = topic.item
    description = topic.description.all()
    matched_desriptions = topicDescription.objects.filter(id__in=description)
    results = []
    for item in matched_desriptions:
        description = item.description
        if term in description:
            new_description = description.replace(term, '_____________ ')
            quest = new_description, term
            results.append(quest)
        else:
            pass

    return(results)

def get_db_questions(lesson_id):
    pass
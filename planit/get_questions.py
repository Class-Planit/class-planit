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


def generate_questions_topic(topic_lists):
    word_bank = []
    descriptions = []
    for topic in topic_lists:
        term = topic.item
        word_bank.append(term)
        lower_term = term.lower()
        word_bank.append(lower_term)
        description = topic.description.all()
        for item in description:
            item_id = item.id
            descriptions.append(item_id)

    matched_desriptions = topicDescription.objects.filter(id__in=descriptions)
    results = []
    for word in word_bank:
        for item in matched_desriptions:
            item_id = item.id
            topic_match = topicInformation.objects.filter(description=item_id).first()
            topic_item = topic_match.item
            description = item.description
            if word in description:
                new_description = description.replace(word, '_____________ ')
                if word == topic_item:
                    quest = new_description, topic_item, None
                elif word.lower() == topic_item.lower():
                    quest = new_description, topic_item, None
                else:
                    quest = new_description, word, topic_item

                results.append(quest)
            else:
                pass
        
    return(results)

def get_db_questions(lesson_id):
    pass
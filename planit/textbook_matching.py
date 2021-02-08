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

from sklearn.metrics import pairwise_distances_argmin


def grouper(iterable):
    prev = None
    group = []
    for item in iterable:
        if not prev or item - prev <= 15:
            group.append(item)
        else:
            yield group
            group = [item]
        prev = item
    if group:
        yield group

def match_textbook_lines(text, class_id, lesson_id):

    classroom_profile = classroom.objects.get(id=class_id)
    standard_set = classroom_profile.standards_set
    class_objectives = lessonObjective.objects.get(id=lesson_id)
    teacher_input = class_objectives.teacher_objective

    blob = TextBlob(teacher_input)
    blob_result = blob.noun_phrases
    result_full = []
    for term in blob_result:
        if term in result_full:
            pass
        else:
            result_full.append(term)

    subject = class_objectives.subject
    grade_list = classroom_profile.grade_level.all()
    get_textbooks = textBookTitle.objects.filter(grade_level__in=grade_list, standards_set=standard_set, subject=subject)

    get_textlines = textBookBackground.objects.filter(textbook__in=get_textbooks)

    for x in text:
        text = x.item
        result_one = text.lower()
        result_full.append(result_one)

   
    return_list = []
    counters = []
    
    print(result_full)
    for line in get_textlines:
        text = line.line_text
        word_count = 0
        for word in result_full:
            if word in text.lower():
                word_count = word_count + 1
                if word_count >= 1:

                    result = word, line, line.line_counter
                    counters.append(line.line_counter)
                    return_list.append(result)

    if counters:
        clusters = dict(enumerate(grouper(counters), 1))
    
        top_num = 0
        results = None
        for x, y in clusters.items():
            y_Length = len(y)
            if y_Length > top_num:
                top_num = y_Length
                results = y
            else:
                pass

        get_textbooks = textBookBackground.objects.filter(line_counter__in=results)
        text = []
        for item in get_textbooks:
            text.append(item.line_text)

        return(text)



    



    
# Run in python console
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

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

count_vect = CountVectorizer()

def label_activities(activity):
    mi = 0
    blooms = 0
    total = 0
    verbs_list = []
    path3 = 'planit/files/Multiple Intelligences and Bloom’s Verbs - Sheet5.csv'
    path4 = 'planit/files/work_product.csv'
    #this is for the mi and blooms level assignment
    with open(path3) as f:
        for line in f:
            line = line.split(',')
            verbs = line[2]
            x = line[3]
            y = line[4]
            for item in verbs.split():
                if item in activity:
                    mi = int(x)
                    blooms = int(y)   
                    total = total + 1    
                    result = item
                    verbs_list.append(result)

    work_list = []
    #this is the workproduct 
    with open(path4) as f:
        for line in f:
            line = line.split(',')
            work_product = line[1]
            for item in work_product.split():
                if item.lower() in activity:
                    if item.lower() not in work_list:
                        work_list.append(item.lower())


    if mi == 0:
        mi = 1

    

    if blooms == 0:
        blooms = 1

    
    if verbs_list:
        results = mi, blooms, verbs_list
    else:
        results = mi, blooms, None

    if work_list:
        work_list = ', '.join([str(i) for i in work_list])
    else:
        work_list = None
    final = results, work_list
    return(final)



def label_activities_analytics(lesson_id):
    class_objectives = lessonObjective.objects.get(id=lesson_id)
    matched_activities = selectedActivity.objects.filter(lesson_overview=class_objectives)
    class_standards = class_objectives.objectives_standards.all()
    matched_standards = singleStandard.objects.filter(id__in=class_standards)
    
    stan_list = []
    for stan in matched_standards:
        stan_text = stan.standard_objective
        stan_list.append(stan_text)


    mi_list = []
    bl_list = []
    activity_list = []
    for activity in matched_activities:
        activity_text = activity.lesson_text
        act_mi = int(activity.mi)
        act_bl = int(activity.bloom)
        mi_list.append(act_mi)
        bl_list.append(act_bl)
        activity_list.append(activity_text)

    mi_list.sort() 
    bl_list.sort()

    mi_high = (mi_list[-1]/5) * 100 
    bl_high = (bl_list[-1]/6) * 100 
    mi_count = len(mi_list)
    bl_count = len(bl_list)

    mi_length = len(set(str(mi_count)))
    bl_length = len(set(str(bl_count)))

    unique_count = int(mi_length) + int(bl_length)

    total_count = mi_count + bl_count

    diff_count = (unique_count/total_count) * 100

    Document1 = ''.join([str(i) for i in activity_list])
    Document2 = ''.join([str(i) for i in stan_list])
    corpus = [Document1,Document2]

    X_train_counts = count_vect.fit_transform(corpus)
    vectorizer = TfidfVectorizer()
    trsfm=vectorizer.fit_transform(corpus)
    result = cosine_similarity(trsfm[0:1], trsfm)
    result = result[0][1] * 100
    final = mi_high, bl_high, diff_count, result
    return(final)
    
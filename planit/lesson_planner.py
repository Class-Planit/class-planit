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



def label_activities(activity):
    mi = 0
    blooms = 0
    total = 0
    verbs_list = []
    path3 = 'planit/files/Multiple Intelligences and Bloom’s Verbs - Sheet5.csv'
    path4 = 'planit/files/work_product.csv'
    with open(path3) as f:
        for line in f:
            line = line.split(',')
            verbs = line[2]
            x = line[3]
            y = line[4]
            for item in verbs.split():
                if item in activity:
                    mi = mi + int(x)
                    blooms = blooms + int(y)   
                    total = total + 1    
                    result = item
                    verbs_list.append(result)

    work_list = []
    with open(path4) as f:
        for line in f:
            line = line.split(',')
            work_product = line[1]
            for item in work_product.split():
                if item.lower() in activity:
                    print(item.lower())
                    work_list.append(item.lower())

    mi_results = mi/total
    if mi_results == 0:
        mi_results = 100
    else:
        mi_results = 100 * mi_results
    
    blooms = blooms/total
    if blooms == 0:
        blooms = 100
    else:
        blooms = 100 * blooms
    
    if verbs_list:
        results = mi_results, blooms, verbs_list
    else:
        results = mi_results, blooms, None

    if work_list:
        work_list = ''.join([str(i) for i in work_list])
    else:
        work_list = None
    final = results, work_list
    return(final)
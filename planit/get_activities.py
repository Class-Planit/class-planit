from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from django.db.models import Q, Sum
import pandas as pd 
from .models import *

import numpy.random
import numpy as np
from serpapi import GoogleSearch
import re
from itertools import chain
import nltk
from nltk import pos_tag, word_tokenize
from nltk.corpus import wordnet 
from nltk.tokenize import WordPunctTokenizer
import wikipedia
from youtube_search import YoutubeSearch
nltk.download('stopwords')
nltk.download('wordnet')
from nltk.stem import PorterStemmer
from nltk.stem import LancasterStemmer
from nltk.stem.wordnet import WordNetLemmatizer
import bs4
from textblob import TextBlob
import requests
from decouple import config, Csv
from rake_nltk import Rake
import re
from collections import Counter
import requests
from bs4 import BeautifulSoup
#test comment 
from nltk.corpus import stopwords
stop_words = stopwords.words('english')
import re
import inflect
stop_words.extend(['The', 'students', 'learn'])
count_vect = CountVectorizer()
porter = PorterStemmer()
lancaster=LancasterStemmer()
from textblob import TextBlob
wikipedia.set_rate_limiting(True)
engine = inflect.engine()
import spacy
import pyinflect
nlp = spacy.load('en_core_web_sm')
import random
from .get_key_terms import *

stop_words = ['i', "'", "'" '!', '.', ':', ',', '[', ']', '(', ')', '?', "'see", "see", 'x', '...',  'student', 'learn', 'objective', 'students', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"]

TAG_RE = re.compile(r'<[^>]+>')


def identify_topic(activity, lesson_id):
    activity = activity.lower()
    class_objectives = lessonObjective.objects.get(id=lesson_id)
    matched_activities = selectedActivity.objects.filter(lesson_overview=class_objectives)
    class_standards = class_objectives.objectives_standards.all()
    matched_standards = singleStandard.objects.filter(id__in=class_standards)
    subject = class_objectives.subject
    c_match = class_objectives.lesson_classroom_id
    class_match = classroom.objects.filter(id=c_match).first()
    g_level = class_match.grade_level.all()
    grade_level = gradeLevel.objects.filter(id__in=g_level)
    topic_matches = topicInformation.objects.filter(subject=subject, grade_level__in=grade_level)
    
    topic_list = []
    for topic in topic_matches:
        topic_term = topic.item
        topic_term = topic_term.lower()
        if topic_term in activity:

            topic_list.append(topic.id)

    return(topic_list)

def label_activities(activity, lesson_id):
    
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
                    if result not in verbs_list:
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

    
    

    if work_list:
        work_list = ', '.join([str(i) for i in work_list])
    else:
        work_list = None
    
    if verbs_list:
        pass
    else:
        verbs_list = None

    final = mi, blooms, verbs_list, work_list
    return(final)

   

def label_activities_analytics_small(lesson_id):
    class_objectives = lessonObjective.objects.get(id=lesson_id)
    matched_activities = selectedActivity.objects.filter(lesson_overview=class_objectives)
    class_standards = class_objectives.objectives_standards.all()
    matched_standards = singleStandard.objects.filter(id__in=class_standards)
    
    stan_list = []
    for stan in matched_standards:
        stan_text = stan.standard_objective
        stan_list.append(stan_text)

    if matched_activities:
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
        if len(Document2) and len(Document1) >= 4:
            corpus = [Document1,Document2]

            X_train_counts = count_vect.fit_transform(corpus)
            vectorizer = TfidfVectorizer()
            trsfm=vectorizer.fit_transform(corpus)
            result = cosine_similarity(trsfm[0:1], trsfm)
            result = result[0][1] * 100
            one = {'name': 'Retention Rate', 'progress': mi_high, 'color': 'bg-warning', 'div': 'showRateDiff()'}
            two = {'name': 'Depth of Understanding', 'progress': bl_high, 'color': 'bg-info', 'div': 'showDepthDiff()'}
            three = {'name': 'Differentiation', 'progress': diff_count, 'color': 'bg-success', 'div': 'showDivDiff()'}
            four = {'name': 'Standards Alignment', 'progress': result, 'color': 'bg-danger', 'div': 'showStanDiff()'}
            final = one, two, three, four

            return(final)
    
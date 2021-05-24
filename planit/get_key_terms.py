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
from .get_openai import *
stop_words = ['i', "'", "'" '!', '.', ':', ',', '[', ']', '(', ')', '?', "'see", "see", 'x', '...',  'student', 'learn', 'objective', 'students', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"]

TAG_RE = re.compile(r'<[^>]+>')



def create_terms(key_term_list, lesson_id, matched_grade, user_id, standard_set):

    lesson_match = lessonObjective.objects.get(id=lesson_id)
    user_profile = User.objects.get(id=user_id)
    subject = lesson_match.subject
    m_topics = lesson_match.objectives_topics.all()
    matched_topics = topicInformation.objects.filter(id__in=m_topics)

    
    for item in key_term_list:
        if len(item[0]) >= 3:
            topic_term = topicInformation.objects.filter(subject=subject, standard_set=standard_set, grade_level=matched_grade, item=item[0]).first()
            if topic_term:
                pass
            else:
                topic_term = topicInformation.objects.create(subject=subject, standard_set=standard_set, grade_level=matched_grade, item=item[0])
                topic_term.created_by = user_profile
                topic_term.save()


            description_create, created = topicDescription.objects.get_or_create(description=item[1], topic_id=topic_term.id,  is_admin = False, created_by = user_profile)
            topic_term.description.add(description_create)
            topic_t = topic_term.topic_type.all()
            tt_matches = topicTypes.objects.filter(id__in=topic_t)
            tt_results = []
            for tt in tt_matches:
                tt_result = tt.item
                tt_results.append(tt_result)
            if tt_results:
                pass
            else:
                result = openai_tes(user_id, topic_term, matched_topics)

            lesson_match.objectives_topics.add(topic_term)

    print('done')


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

wikipedia.set_rate_limiting(True)
engine = inflect.engine()
import spacy
import pyinflect
nlp = spacy.load('en_core_web_sm')
import random
from .get_openai import *
stop_words = ['i', "'", "'" '!', '.', ':', ',', '[', ']', '(', ')', '?', "'see", "see", 'x', '...',  'student', 'learn', 'objective', 'students', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"]

TAG_RE = re.compile(r'<[^>]+>')

def build_standard_list(lesson_id):
    lesson_match = lessonObjective.objects.get(id=lesson_id)
    a_matches = lesson_match.objectives_standards.all()
    obj_matches = singleStandard.objects.filter(id__in=a_matches)
    o_list = []
    for item in obj_matches:
        result = str(item)
        o_list.append(result)

    obj_full = ', '.join(o_list)
    return(obj_full)



def build_term_list(lesson_id):
    lesson_match = lessonObjective.objects.get(id=lesson_id)
    a_matches = lesson_match.objectives_topics.all()
    act_matches = topicInformation.objects.filter(id__in=a_matches)
    
    term_list = []
    for item in act_matches:
        desc_list = item.description.all()
        d_list = []
        for desp in desc_list:
            desc = desp.description
            d_list.append(desc)
        d_results = ', '.join(d_list)
        result = (item.item, str(d_results))
        term_list.append(result)
    
    return(term_list)


def build_term_list_pdf(lesson_id):
    lesson_match = lessonObjective.objects.get(id=lesson_id)
    a_matches = lesson_match.objectives_topics.all()
    act_matches = topicInformation.objects.filter(id__in=a_matches)
    
    term_list = []
    for item in act_matches:
        desc_list = item.description.all()
        d_list = []
        for desp in desc_list:
            desc = desp.description
            d_list.append(desc)
        d_results = ', '.join(d_list)
        result = {'item': item.item, 'Description': d_results}
        
        term_list.append(result)
    
    return(term_list)

def combine_topics(matched_topics):
    
    for one in matched_topics:
        if one.id:
            desc_full = []
            term_one = one.item
            one_desc_matches = one.description.all()
            one_Topics = topicDescription.objects.filter(id__in=one_desc_matches)
            for oi in one_Topics:
                if oi.id not in desc_full:
                    desc_full.append(oi.id)
            for two in matched_topics:
                term_two = two.item
                if term_one.lower() == term_two.lower():
                    if one.id != two.id: 
                        desc_matches = two.description.all()
                        for desc in desc_matches:
                            if desc.id not in desc_full:
                                desc_full.append(desc.id)

                            desc.delete()
                            two.delete()

            one_desc_matches = one.description.clear()
            for item in desc_full:
                one_desc = topicDescription.objects.filter(id=item)
                for desc in one_desc:
                    one_desc_matches = one.description.add(desc)
            




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
                desc_m = topic_term.description.all()
                for desc in desc_m:
                    if desc.is_admin:
                        topic_term.description.remove(desc)
                    else:
                        topic_term.description.remove(desc)
                        desc.delete()
                        
            else:
                topic_term = topicInformation.objects.create(subject=subject, standard_set=standard_set, grade_level=matched_grade, item=item[0])
                topic_term.created_by = user_profile
                topic_term.save()

            desc_check = topicDescription.objects.filter(description=item[1], topic_id=topic_term.id,  is_admin = False, created_by = user_profile)
            if desc_check:
                description_create = topicDescription.objects.filter(description=item[1], topic_id=topic_term.id,  is_admin = False, created_by = user_profile).first()
                other_desc = desc_check.exclude(id=description_create.id)
                other_desc.delete()
            else:
                description_create, created = topicDescription.objects.get_or_create(description=item[1], topic_id=topic_term.id,  is_admin = False, created_by = user_profile)
            
            topic_term.description.add(description_create)
            list_one = []
            list_two = []
            for desc in topic_term.description.all():
                list_one.append(desc)
                list_two.append(desc)



            for desc1 in list_one:
                for desc2 in list_two:
                    if desc1.id == desc2.id:
                        pass
                    else:
                        
                        is_dup = check_duplicate_strings(desc1.description, desc2.description)
                        if is_dup:
                            topic_term.description.remove(desc2)
                            desc2.delete()

            topic_t = topic_term.topic_type.all()
            tt_matches = topicTypes.objects.filter(id__in=topic_t)
            tt_results = []
            for tt in tt_matches:
                tt_result = tt.item
                tt_results.append(tt_result)
            if tt_results:
                pass
            else:
                result = openai_term_labels(user_id, topic_term, subject, matched_grade)
                result = result.strip("'")
                if result:
                    tt_new, created = topicTypes.objects.get_or_create(item=result)
                    add_tt = topic_term.topic_type.add(tt_new)

            lesson_match.objectives_topics.add(topic_term)

    combine_terms = combine_topics(matched_topics)
    print('done')

def string_word_count(string):
    string_split = string.split()
    word_lengths = []
    for word in string_split:
        count = len(word)
        word_lengths.append(str(count))
    

    word_num = ''.join(word_lengths)

    word_num = int(word_num)
    return(word_num)

def check_duplicate_strings(string1, string2):
    string1_split = string_word_count(string1)
    string2_split = string_word_count(string2)


    if string1_split == string2_split:
        is_duplicate = True
    else:
        is_duplicate = False

    return(is_duplicate)

import os
import openai
from decouple import config, Csv
from .models import *
import json
import requests
import re
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
from .tasks import *
from spacy.language import Language
from .get_wikipedia import *
Language.factories['tok2vec']

openai.api_key = config('OPENAI_API_KEY') 


def clean_sentences(sent):

    sentences = tokenize.sent_tokenize(sent)
    result = ' '.join(sentences[:3])
    return(result)



def get_desciption_summary(item, full_desc):
    full_sentence = f'term: {item} description: {full_desc}'
    if len(full_sentence)  > 4:
        response = openai.Completion.create(
                    engine="curie",
                    prompt=full_sentence,
                    temperature=0.3,
                    max_tokens=80,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0,
                    stop=["\n"]
                    )
        results = response['choices'][0]

        print('---------')
        print('get_desciption_summary', results['text'])
        print('---------')
        final = clean_sentences(results['text'])
        return(final)

def get_description_string(topic_id, user_id):
    user_profile = User.objects.get(id=user_id)
    match_topic = topicInformation.objects.get(id=topic_id)
    d_list = match_topic.description.all()
    personal_descriptions = topicDescription.objects.filter(id__in=d_list, is_admin=False, created_by=user_profile)
    if personal_descriptions:
        description_matches = personal_descriptions
    else:
        description_matches = topicDescription.objects.filter(id__in=d_list, is_admin=True)

    all_d = []
    for item in description_matches:
        line = item.description
        if line is not None:
            all_d.append(line)

    if all_d:
        final = ';; '.join(all_d)
    else:
        final = '--'
    return(final)
    


def openai_term_labels(user_id, topic_term, subject, grade):

    admin_subjects = ['Physical Education', 'Health Education', 'Spanish Language', 'Science', 'Social Studies', 'Mathematics', 'English', 'Venture']
    
    default_subject = 'default'

    for item in admin_subjects:
        if subject.subject_title == item:
            default_subject = subject.subject_title

    if grade is None:
        grade_label = 'Eight'
    else:
        grade_label = grade.grade_labels

    path3 = f'planit/files/%s/%s/examples.csv' % (default_subject, grade_label)


    description = get_description_string(topic_term.id, user_id)
    wording = f'term: {topic_term.item} description: {description}'
    #this is for the mi and blooms level assignment

    
    try:
        with open(path3) as f:

            examples = []
            labels = []
            for line in f:
                line = line.split(',')
                
                example_wording = [line[0], line[1]]
                examples.append(example_wording)
                labels.append(line[1])



            response = openai.Classification.create(
                        search_model="ada", 
                        model="curie",
                        examples=examples,
                        query=wording,
                        labels=labels)
            print('---------')
            print('openai', response['label'].upper())
            print('---------')
            return(response['label'].upper())
    except:
        return('KT')


    
def build_on_activtity(act_string):
    prompt = "%s." % (act_string)
    response = openai.Completion.create(
        engine="davinci",
        prompt=prompt,
        temperature=0.3,
        max_tokens=64,
        top_p=1,
        frequency_penalty=0.5,
        presence_penalty=0
        )


    result = response['choices'][0]
    return(result['text'])


   



def activity_score(sentence):
    pass

def get_single_types_activity(topic_list):
    word_list = []
    for topic in topic_list:

        word = topic.item
        topic_types = topic.topic_type.all()
        t_matches = topicTypes.objects.filter(id__in=topic_types)
        for tt in t_matches:
            topic_t = tt.item

            all_templates = LearningDemonstrationTemplate.objects.filter(topic_type=tt)

            for temp in all_templates:
                result =  temp.content
                sentence  = result.replace(topic_t, word)
                result = sentence, word, topic_t, 'single', temp.id
            
                word_list.append(result)


    return(word_list)


def get_activity_mask(topic_list):
    pass
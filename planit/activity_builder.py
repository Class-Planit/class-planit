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

stop_words = ['i', "'", "'" '!', '.', ':', ',', '[', ']', '(', ')', '?', "'see", "see", 'x', '...',  'student', 'learn', 'objective', 'students', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"]

TAG_RE = re.compile(r'<[^>]+>')


#this is the first step in generating Term Recs
def generate_term_recs(teacher_input, class_id, lesson_id, user_id):
    
    #this function creates relevant key terms based on objective, standard, activities, and already selected key terms
    user_profile = User.objects.get(id=user_id)
    class_objectives = lessonObjective.objects.get(id=lesson_id)
    classroom_profile = classroom.objects.get(id=class_id)
    subject = class_objectives.subject
    grade_list = classroom_profile.grade_level.all()
    standard_set = classroom_profile.standards_set
    
    
    current_rec_list, created = reccomendedTopics.objects.get_or_create(matched_lesson=class_objectives)
    removed_t = current_rec_list.removed_topics.all()
    #demonstrations of knowledge are parts of an activity that says what we want students to know 
    #by the end of the activity ie "identify importance of teh Emancipation Proclaimation"
    demo_ks = class_objectives.objectives_demonstration.all()

    #removes topics are terms that the teacher has indicated aren't relevant 
    removed_topics = topicInformation.objects.filter(id__in=removed_t)
 
    #creates a new model object where we will save the recomended topics so that we don't have to continously 
    #generate new key terms if some are already there
    create_topic_matches, created = matchedTopics.objects.get_or_create(lesson_overview=class_objectives)

    topic_matches = class_objectives.objectives_topics.all()
    selected_standard = class_objectives.objectives_standards.all()
    m_stand = singleStandard.objects.filter(id__in=selected_standard)
    stand_result = []
    for stand in m_stand:
        stand_result.append(stand.competency)

    stand_full = ' '.join([str(i) for i in stand_result])

    topics = topicInformation.objects.filter(id__in=topic_matches)

    topic_count = topics.count()
    
    results_list = []
    topic_ids = []
    for item in topics: 
        result = item.item
        item_id = item.id 
        results_list.append(result)
        topic_ids.append(item_id)

    teacher_input_full = ' '.join([teacher_input, stand_full])
    standards_nouns = get_sentence_nouns(teacher_input_full)
    terms_full = ' '.join(standards_nouns)
    teacher_input_stem = stemSentence(terms_full.lower())
    tokens_without_sw = [word for word in teacher_input_stem.split() if not word in stop_words]
    
    

    get_objective_matches = get_topic_matches(class_objectives, topic_count, grade_list, subject, standard_set, lesson_id, user_id)

    matched_activities = selectedActivity.objects.filter(lesson_overview=class_objectives, is_selected=True)

    #step two check other topics


    #step three check wikipedia 

    #step two check other topics
    matched_topics = match_objectives(get_objective_matches, tokens_without_sw, topic_ids)



    not_selected_topics = []
    
    for item in matched_topics:  
        if item[0] in removed_t:
            pass
        else:    
            if item[0] not in not_selected_topics:
                not_selected_topics.append(item)

    

    get_more_topics = build_wiki_topic_list(topics, lesson_id, user_profile, standards_nouns)
    for topic_item in get_more_topics:
        if topic_item in removed_t:
            not_selected_topics.remove(topic_item)
        else:
            not_selected_topics.append(topic_item)


    not_selected_topics.sort(key=lambda x: x[1], reverse=True)
    topic_list = not_selected_topics[:10]     


    final_list = []
    for top in topic_list:
        
        top_id = top[0]
        top_match = topicInformation.objects.get(id=top_id)
        descriptions = get_description_string(top_match.id, user_id)
        result = {'id': top_match.id, 'term': top_match.item, 'descriptions': descriptions} 

        if result not in final_list:
            update_recs = current_rec_list.rec_topics.add(top_match)
            final_list.append(result)


    return(final_list)


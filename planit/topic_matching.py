from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import lda


from django.db.models import Q, Sum
import pandas as pd 
from .models import *
import numpy.random
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
import bs4
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

stop_words.extend(['The', 'students', 'learn'])
count_vect = CountVectorizer()
porter = PorterStemmer()
lancaster=LancasterStemmer()

wikipedia.set_rate_limiting(True)

stop_words = ['i', 'student', 'learn', 'objective', 'students', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"]


def stemSentence(sentence):
    token_words=word_tokenize(sentence)
    token_words
    stem_sentence=[]
    for word in token_words:
        stem_sentence.append(porter.stem(word))
        stem_sentence.append(" ")
    return "".join(stem_sentence)

def match_topics(teacher_input, class_id, lesson_id):
     
        classroom_profile = classroom.objects.get(id=class_id)
       
        grade_list = classroom_profile.grade_level.all()
        standard_set = classroom_profile.standards_set
        
        class_objectives = lessonObjective.objects.get(id=lesson_id)
        topic_matches = class_objectives.objectives_topics.all()
       
        topics = topicInformation.objects.filter(id__in=topic_matches)
        results_list = []
        for item in topics: 
            result = item.description
            results_list.append(result)
       
        subject = class_objectives.subject
        grade_standards = []
        teacher_input = teacher_input + str(results_list)
        teacher_input = teacher_input.lower()
        teacher_input = stemSentence(teacher_input)
        
        for grade in grade_list:
                
                obj = topicInformation.objects.filter(subject=subject, standard_set=standard_set, grade_level=grade)
                

                if obj:

                    objectives_list = []
                    for topic in obj:
                            descriptions = topic.description.all()
                            desc_list = []
                            for item in descriptions:
                                result = item.description
                                desc_list.append(result)
                            result = topic.id, (desc_list, topic.item) 
                            objectives_list.append(result) 
                    
                    prediction = []
                    for standard_full in objectives_list:
                            standard_full_join = ''.join([str(i) for i in standard_full[1]]).lower()
                            standard_full_joined = stemSentence(standard_full_join)

                            text_tokens = word_tokenize(teacher_input)
                            tokens_without_sw = [word for word in text_tokens if not word in stop_words]
                            if any(word in standard_full_joined for word in tokens_without_sw):

                                prediction.append(standard_full)
       
                    
                    return(prediction[:30])
                else:
                    return(None)


def match_textbook(teacher_input, class_id, lesson_id):
        classroom_profile = classroom.objects.get(id=class_id)
        grade_list = classroom_profile.grade_level.all()
        standard_set = classroom_profile.standards_set
        class_objectives = lessonObjective.objects.get(id=lesson_id)
        topic_matches = class_objectives.objectives_topics.all()
        topics = topicInformation.objects.filter(id__in=topic_matches)
        subject = class_objectives.subject
        title_list = []
        for grade in grade_list:
            matched_textbooks = textBookTitle.objects.filter(subject=subject, standards_set=standard_set, grade_level=grade)
            for item in matched_textbooks:
                result = item.id 
                title_list.append(result)

        results_list = []
        for item in topics: 
            result = item.description
            results_list.append(result)
       
        
        grade_standards = []
        teacher_input = teacher_input + str(results_list)

        obj = textBookBackground.objects.filter(textbook__in=title_list)

        objectives_list = []
        for topic in obj:
                result = topic.header, topic.line_text
                objectives_list.append(result) 
    
        prediction = []
        for standard_full in objectives_list:
                standard_full_joined = ''.join([str(i) for i in standard_full[1]])

                Document1 = teacher_input
                Document2 = standard_full_joined
                corpus = [Document1,Document2]
                X_train_counts = count_vect.fit_transform(corpus)
                vectorizer = TfidfVectorizer()
                trsfm=vectorizer.fit_transform(corpus)
                result = cosine_similarity(trsfm[0:1], trsfm)
                result = result[0][1]
                total = standard_full[0], result
                prediction.append(total)
        prediction.sort(key=lambda x: x[1], reverse=True)
        
        if prediction:
            for item in prediction:
                if item[1] >= .25:
                    
                    results = prediction
                    grade_standards.append(item)

        return(grade_standards)




def get_lessons(lesson_id):
    lesson_match = lessonObjective.objects.get(id=lesson_id)
    topic_matches = lesson_match.objectives_topics.all()
    topic_list = topicInformation.objects.filter(id__in=topic_matches)
    teacher_objective = lesson_match.teacher_objective
    topic_results = []
    for item in topic_list:
        replacement = item.item
        topic_types = item.topic_type.all()
        for tt in topic_types:

            masked_info = tt.item
            result = masked_info.upper()
            lesson_templates = lessonTemplates.objects.filter(components=tt)
            for template in lesson_templates:
                wording = template.wording
                lesson = wording.replace(result, replacement)  
                topic_results.append(lesson)
    
    return(topic_results)


def get_website_data(link):

    url = link
    res = requests.get(url)
    html_page = res.content
    soup = BeautifulSoup(html_page, 'html.parser')
    text = soup.find_all(text=True)

    output = ''
    blacklist = [
        '[document]',
        'noscript',
        'header',
        'html',
        'meta',
        'head', 
        'input',
        'script',
        # there may be more elements you don't want, such as "style", etc.
    ]

    for t in text:
        if t.parent.name not in blacklist:
            output += '{} '.format(t)

    print(output)




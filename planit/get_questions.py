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

import pytextrank
nlp.add_pipe("textrank")


stop_words = ['i', "'", "'" '!', '.', ':', ',', '[', ']', '(', ')', '?', "'see", "see", 'x', '...',  'student', 'learn', 'objective', 'students', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"]

TAG_RE = re.compile(r'<[^>]+>')


def remove_tags(text):
    return TAG_RE.sub('', text)

def stemSentence(sentence):
    token_words=word_tokenize(sentence)
    token_words
    stem_sentence=[]
    for word in token_words:
        stem_sentence.append(porter.stem(word))
        stem_sentence.append(" ")
    return "".join(stem_sentence)

def get_objective_title(objective, stem):
    objective_lowered = objective.lower()
    text_tokens = word_tokenize(objective_lowered)
    final = []

    for term in text_tokens:
        if any(word in term for word in stem):
            result = term

            final.append(result)
    updated_final = ' '.join([str(i) for i in final])

    return(updated_final)

def get_keywords(text):
        my_words = 'Use'
        r = Rake() # Uses stopwords for english from NLTK, and all puntuation characters.
        r.extract_keywords_from_text(text)
        keywords = r.get_ranked_phrases() # To get keyword phrases ranked highest to lowest.
        
        remove_list = ['Use', 'students', 'learn']
        cleaned_list = []
        for word in keywords:
                word_split = word.split()
                
                word_count = len(word_split)
                
                if word_count < 3:
                        if word in remove_list:
                                pass
                        else:
                                cleaned_list.append(word)        
        return(cleaned_list[:10])


def check_matches_topics(item_one, item_two):
    text_split = item_one.lower()
    standard_split = item_two.lower()
    if text_split in standard_split:
        return(True)
    else:
        return(False)


def get_word_banks(result):
    sent = ' '.join(result)
    doc = nlp(sent)
    word_list = []
    for phrase in doc._.phrases:
        words = phrase.text, phrase.rank, phrase.count
        word_list.append(words)

    sent_blob = TextBlob(sent)
    sent_tagger = sent_blob.pos_tags
    return(sent_tagger, word_list)
    
def true_false_statements(descriptions, topic):
    pass
        


def find_mc_incorrects(descriptions, topic):
    pos_tag_list = ('NNP', 'NNS', 'JJ', 'NN', 'VBZ' )
    word_list = topic[2]
    text_blob = word_list[0]
    text_rankings = word_list[1]
    final_list = []
    for item in text_rankings:
        sent_blob = TextBlob(item[0])
        sent_tagger = sent_blob.pos_tags
        for y in sent_tagger:
            pos_type = y[1]
            pos_term = y[0]
            replacements = []
            for line in descriptions:
                for pos_option in line[2][0]:
                    if pos_option[1] in pos_tag_list:
                        if pos_type == pos_option[1]:
                            if pos_type[0] == pos_option[0]:
                                pass
                            else:
                                if pos_option[0] not in topic[1]:
                                    if pos_option[0] not in stop_words:
                                        if len(pos_option[0]) >= 4:
                                            if pos_option[0] not in replacements:
                                                replacements.append(pos_option[0])

            random.shuffle(replacements)
            if len(replacements) >= 3:
                results = pos_term, replacements[0], replacements[1], replacements[2]
                final_list.append(results)
    

    return(final_list)


def get_question_text(lesson_id, user_profile):
    class_objectives = lessonObjective.objects.get(id=lesson_id)
    subject = class_objectives.subject

    topic_matches = class_objectives.objectives_topics.all()
    topics = topicInformation.objects.filter(id__in=topic_matches)
    
    descriptions = []
    for item in topics:
        term = item.item
        desc_list = item.description.all()
        all_topics = topicDescription.objects.filter(id__in=desc_list, is_admin=False, created_by=user_profile)
        for top in all_topics:
            result = term, top.description
            word_banks = get_word_banks(result)
            final = term, top.description, word_banks, 'topic', item
            descriptions.append(final)

    for topic in topics: 
        term = topic.item
        text_lines = topic.text_index.all()
        textlines = textBookBackground.objects.filter(id__in=text_lines)
        for item in textlines:
            result = term, item.line_text
            word_banks = get_word_banks(result)
            final = term, item.line_text, word_banks, 'textbook', item
            descriptions.append(final)

    
    question_results = []
    all_topic_lines = []
    for topic in descriptions: 
        remove_list = ['illustrations', 'cartoon', 'Figure', 'they', 'those', 'Name ', 'Circle ', 'Education.com ', 'The McGraw-Hill', 'Review ']
        if any(word in topic[1] for word in remove_list):
            pass
        else:
            check_match = check_matches_topics(topic[0], topic[1])
            if check_match:
                sentence = topic[1]
                Answer = topic[0]
                Question = sentence.replace(Answer, '_________')
                question_type = questionType.objects.filter(item='fill_in_the_blank').first()
                if 'textbook' in topic[3]:
                    new_question, created = topicQuestion.objects.get_or_create(subject	= subject, linked_text=topic[4], question_type = question_type, lesson_overview=class_objectives, Question = Question, Correct = Answer, is_admin = False)
                else:
                    new_question, created = topicQuestion.objects.get_or_create(subject	= subject, linked_topic=topic[4], question_type = question_type, lesson_overview=class_objectives, Question = Question, Correct = Answer, is_admin = False)
                
                if new_question not in all_topic_lines:
                    all_topic_lines.append(new_question.id)

                get_statement = true_false_statements(descriptions, topic)
                get_incorrects =  find_mc_incorrects(descriptions, topic)   
                if get_statement:
                    Answer = topic[0]
                    Question = topic[1]
                    
                    question_type = questionType.objects.filter(item='true_false').first()
                    new_question, created = topicQuestion.objects.get_or_create(subject	= subject, question_type = question_type, Question = Question, Correct = Answer, lesson_overview=class_objectives, item=topic[0], is_admin = False)
                    if new_question not in all_topic_lines:
                        all_topic_lines.append(new_question.id)

                if get_incorrects:
                    for line in get_incorrects[:2]:
                        Answer = line[0]
                        in_one = line[1]
                        in_two = line[2]
                        in_three = line[3]
                        sentence = topic[1]
                        Question = sentence.replace(Answer, '_________')
                        question_type = questionType.objects.filter(item='multi_choice').first()
                        if 'textbook' in topic[3]: 
                            new_question, created = topicQuestion.objects.get_or_create(subject	= subject, linked_text=topic[4], question_type = question_type, Question = Question, Correct = Answer, lesson_overview=class_objectives,  item=topic[0], Incorrect_One=in_one, Incorrect_Two=in_two, Incorrect_Three=in_three, is_admin = False)
                        else:
                            new_question, created = topicQuestion.objects.get_or_create(subject	= subject, linked_topic=topic[4], question_type = question_type, Question = Question, Correct = Answer, lesson_overview=class_objectives,  item=topic[0], Incorrect_One=in_one, Incorrect_Two=in_two, Incorrect_Three=in_three, is_admin = False)

                        if new_question not in all_topic_lines:
                            all_topic_lines.append(new_question.id)
   
            else:
                questions = ['What ', 'Where ', 'How ', 'When ', 'Which ']
                for quest in questions:
                    if quest in topic[1]:
                        is_question = True
                    else:
                        is_question = False

                if is_question:
                    Question = topic[1]
                    question_type = questionType.objects.filter(item='short_answer').first()
                    if 'textbook' in topic[3]:
                        new_question, created = topicQuestion.objects.get_or_create(subject	= subject, lesson_overview=class_objectives, question_type = question_type, linked_text=topic[4], Question = Question, Correct = None, is_admin = False)
                    else:
                        new_question, created = topicQuestion.objects.get_or_create(subject	= subject, lesson_overview=class_objectives, linked_topic=topic[4], question_type = question_type, Question = Question, Correct = None, is_admin = False)
                    if new_question not in all_topic_lines:
                        all_topic_lines.append(new_question.id)
                else:
                    Answer = topic[0]
                    Question = topic[1]
                    
                    question_type = questionType.objects.filter(item='short_answer').first()
                    if 'textbook' in topic[3]:
                        new_question, created = topicQuestion.objects.get_or_create(subject	= subject, lesson_overview=class_objectives, linked_text=topic[4], question_type = question_type, Question = Question, Correct = Answer, is_admin = False)
                    else:
                        new_question, created = topicQuestion.objects.get_or_create(subject	= subject, lesson_overview=class_objectives, linked_topic=topic[4], question_type = question_type, Question = Question, Correct = Answer, is_admin = False)
                    if new_question not in all_topic_lines:
                        all_topic_lines.append(new_question.id)


    return(all_topic_lines)



def match_lesson_questions(teacher_input, class_id, lesson_id):
        classroom_profile = classroom.objects.get(id=class_id)
       
        grade_list = classroom_profile.grade_level.all()
        standard_set = classroom_profile.standards_set
        
        class_objectives = lessonObjective.objects.get(id=lesson_id)
        topic_matches = class_objectives.objectives_topics.all()
       
        topics = topicInformation.objects.filter(id__in=topic_matches)
        topic_count = topics.count()
        results_list = []
        for item in topics: 
            result = item.item
            results_list.append(result)
       
        subject = class_objectives.subject
        grade_standards = []
        teacher_input_full = teacher_input + str(results_list)

        teacher_input_stem = teacher_input_full.lower()
        teacher_input_stem = stemSentence(teacher_input_stem)
        text_tokens = word_tokenize(teacher_input_stem)
        tokens_without_sw = [word for word in text_tokens if not word in stop_words]

        objective_title = get_objective_title(teacher_input, tokens_without_sw)
        if class_objectives.objective_title:
            pass
        else:
            class_objectives.objective_title = objective_title
            class_objectives.save()

        for grade in grade_list:
                
                obj = topicQuestion.objects.filter(subject=subject, standard_set=standard_set, grade_level=grade)
                
                if obj:

                    objectives_list = []
                    for topic in obj:
                            question = topic.Question
                            c_answer = topic.Correct
                            quest_list = question, c_answer
                            result = topic.id, quest_list
                            objectives_list.append(result) 
                    

                    prediction = []
                    for standard_full in objectives_list:
                            
                            standard_full_join = ''.join([str(i) for i in standard_full]).lower()
                            Document1 = ''.join([str(i) for i in teacher_input_full])
                            Document2 = standard_full_join
                            check_matched = check_matches_topics(Document2, Document1)
                            if check_matched:

                                corpus = [Document1,Document2]

                                X_train_counts = count_vect.fit_transform(corpus)
                                vectorizer = TfidfVectorizer()
                                trsfm=vectorizer.fit_transform(corpus)
                                result = cosine_similarity(trsfm[0:1], trsfm)
                                result = result[0][1]
                                total = standard_full, result
                                prediction.append(total)
                    prediction.sort(key=lambda x: x[1], reverse=True)
                    return(prediction[:20])
                else:
                    return(None)


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
from .tasks import *
from spacy.language import Language

Language.factories['tok2vec']

stop_words = ['i', "'", "'" '!', '.', ':', ',', '[', ']', '(', ')', '?', "'see", "see", 'x', '...',  'student', 'learn', 'objective', 'students', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"]

TAG_RE = re.compile(r'<[^>]+>')


def get_new_lesson(demo_wording, topic_list,  lesson_id, user_id):
    user_profile = User.objects.get(id=user_id)

    lesson_match = lessonObjective.objects.get(id=lesson_id)
    topic_results = []
    for topic in topic_list:
        tt_list = topic.topic_type.all()
        for item in tt_list:
            topic_results.append(item) 

    lesson_templates = lessonTemplates.objects.filter(components__in=topic_results)

    lesson_list = []
    for temp in lesson_templates:
        lesson_wording = temp.wording
        verb = temp.verb
        work_product = temp.work_product
        bloom = temp.bloom
        mi = temp.mi
        new_wording = lesson_wording.replace('DEMO_KS', demo_wording)
     
        new, created = selectedActivity.objects.get_or_create(created_by=user_profile , template_id=temp.id , lesson_overview = lesson_match, lesson_text = new_wording, verb = verb, work_product = work_product, bloom = bloom, mi = mi, is_admin = False)
        lesson_list.append(new)

    return(lesson_list)


def get_multiple_types_activity(topic_list):
    word_list = []
    for topic in topic_list:
        words = topic.item
        word_list.append(words)

    words_list_full = ' '.join([str(i) for i in word_list])
    words_list_full = words_list_full.split()

    wordfreq = []
    for w in words_list_full:
        if w not in stop_words:
            result = w, words_list_full.count(w)
            wordfreq.append(result)

    wordfreq.sort(key=lambda x: x[1], reverse=True)

    wording_list = []
    if wordfreq:
        if wordfreq[0][1] > 1:
            result = wordfreq[0][0]
            sent_blob = TextBlob(result)
            sent_tagger = sent_blob.pos_tags

            for y in sent_tagger:
                if 'NN' in y[1]:
                    wording = 'describe the parts of the ' +  y[0]
                    wording_list.append(wording)
        


    return(wording_list)

    



def get_plural_types_activity(topic_list):
    word_list = []
    for topic in topic_list:
        words = topic.item
        word_list.append(words)

    words_list_full = ' '.join([str(i) for i in word_list])
    words_list_full = words_list_full.split()

    wordfreq = []
    for w in words_list_full:
        result = w, words_list_full.count(w)
        wordfreq.append(result)

    wordfreq.sort(key=lambda x: x[1], reverse=True)

    wording_list = []

    if wordfreq[0][1] > 1:
        plural = engine.plural(wordfreq[0][0])
        if plural:
            wording = 'characterize the types of ' +  plural
            wording_list.append(wording)
        


    return(wording_list)


#Show students examples of <<DEMONSTRATION>>. <<GROUPING>> Instruct students to <<VERB>> by <<DEMONSTRATION>> <<WORK_PRODUCT>>
def get_lessons(topic_list, demo_ks, lesson_id, user_id):
    topic_results = []
    full_result = []
    topic_ids = []
    for item in topic_list:
        
        topic_types = item.topic_type.all()
        

        topic_items = []
        for tt in topic_types:
            masked_info = tt.item
            topic_id = tt.id
            topic_ids.append(topic_id)
            topic_items.append(masked_info)
            topic_results.append(masked_info)

        replacement = item, topic_items
        full_result.append(replacement)
        
        

    words_list_full = ' '.join([str(i) for i in topic_results])
    words_list_full = words_list_full.split()

    wordfreq = []
    for w in words_list_full:
        result = w, words_list_full.count(w)
        wordfreq.append(result)
    wordfreq.sort(key=lambda x: x[1], reverse=True)
    wordfreq = set(wordfreq)
    
    wording_list = []

    for item in demo_ks:
        wording = item.content
        topic_types = []
        if item.topic_id:
            topic_match = topicInformation.objects.filter(id=item.topic_id).first()
            if topic_match:
                topic_two = topic_match.topic_type.all()
                for topic in topic_two:
                    topic_types.append(topic)

        if wording not in wording_list:
            results = wording, topic_types
            wording_list.append(results)

    for topic_item in wordfreq:
        
        #this is for multiple or the same topic items 
        if topic_item[1] > 1:
            result_list = []
            for item in full_result:
                if topic_item[0] in item[1]:
                    result = item[0]
                    result_list.append(result)

            plural_noun = get_plural_types_activity(result_list)
            for item in plural_noun:
                results = item, result_list
               
                if results not in wording_list:
                    wording_list.append(results) 
            multi_noun = get_multiple_types_activity(result_list)
            for item in multi_noun:
                results = item, result_list
                
                if results not in wording_list:
                    wording_list.append(results) 



        else:
        #this is for single topic items    
            result_list = []
            for item in full_result:
                if topic_item[0] in item[1]:
                    result_one = item[0]
                    result_list.append(result_one)
                    
                    topic_one = result_one.topic_type.all()
                    topic_list = []
                    for item in topic_one:
                        topic_list.append(item)
                    
                    demo_ks_match = LearningDemonstrationTemplate.objects.filter(topic_type__in=topic_one)
                    for demo in demo_ks_match:
                        wording = demo.content

                        topic_two = demo.topic_type.all()

                        for item in topic_two:
                            new_wording = wording.replace(str(item), result_one.item)  
                            result = new_wording, result_list
                          
                            if result not in wording_list:
                                wording_list.append(result) 

  
    for line in wording_list:
        wording = line[0]
        wording_split = wording.split()
        first_word = wording_split[0]
        tokens = nlp(first_word)
        new_verb = tokens[0]._.inflect('VBG')
        new_demo = wording.replace(first_word, new_verb) 
        lesson_full = get_new_lesson(new_demo, line[1], lesson_id, user_id)


    return(wording_list)


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


def group_topic_texts(lesson_id):
    class_objectives = lessonObjective.objects.get(id=lesson_id)

    topic_matches = class_objectives.objectives_topics.all()

    topics = topicInformation.objects.filter(id__in=topic_matches)

    all_topic_lines = []
    for topic in topics:
        
        line_list = topic.text_index.all()

        results = []
        for line in line_list:
            line_index = line.line_counter
            results.append(line_index)
        if results:
            all_topic_lines.append(results)

    topic_line_count = len(all_topic_lines)
    if topic_line_count > 10:
        pass
    else:
        pass
    
    line_ranges = []
    for item in all_topic_lines:
        low = min(item)
        high = max(item)
        difference = high - low 
        if difference > 200:
            high = low + 200 
        ranges = low, high
        line_ranges.append(ranges)

    total_topics = []
    for r_item in line_ranges:
        textlines = textBookBackground.objects.filter(line_counter__range=(r_item[0],r_item[1]))
        related_topics = topicInformation.objects.filter(text_index__in=textlines)
        if related_topics:
            total_topics.extend(related_topics)

    updated_list = []
    for topic in total_topics:
        wording = topic.item
        topic_id = topic.id
        if wording:
            if topic in updated_list:
                pass
            else:
                updated_list.append(topic_id)
        else:
            related_topics = topicInformation.objects.filter(id=topic_id).first()
            related_topics.delete()

    return(updated_list)


def match_objectives(get_objective_matches, tokens_without_sw, topic_ids):
    objective_predictions = []
    for standard_id , standard_full in get_objective_matches:
        Document1 = ' '.join([str(i) for i in tokens_without_sw])
        Document2 = ' '.join([str(i) for i in standard_full])

        Document1 = Document1.replace("'", '')
        Document2 = Document2.replace("'", '')

        corpus = [Document1,Document2]
        
        X_train_counts = count_vect.fit_transform(corpus)
        vectorizer = TfidfVectorizer()
        trsfm=vectorizer.fit_transform(corpus)
        result = cosine_similarity(trsfm[0:1], trsfm)
        result = result[0][1]
        total = standard_id, result
        
        if result >= .20:
            objective_predictions.append(total)
        elif result >= .08:
            if any(word in Document1 for word in Document2):
                total = standard_id, 1
                objective_predictions.append(total)
        elif standard_id in topic_ids:
            total = standard_id, 1
            objective_predictions.append(total)
        else:
            pass
                
    objective_predictions.sort(key=lambda x: x[1], reverse=True)
    full_result = []
    for item in objective_predictions:
        full_result.append(item[0])
    return(full_result)

def get_topic_matches(teacher_input, tokens_without_sw, class_objectives, topic_count, grade_list, subject, standard_set, lesson_id):
    objective_title = get_objective_title(teacher_input, tokens_without_sw)
    if class_objectives.objective_title:
        pass
    else:
        class_objectives.objective_title = objective_title
        class_objectives.save()


    if topic_count > 2:
        get_topic_ids = group_topic_texts(lesson_id)
    else:
        get_topic_ids = []

    objectives_list = []
    for grade in grade_list:
            
        
        obj = topicInformation.objects.filter(subject=subject, standard_set=standard_set, grade_level=grade)
        

        if obj:
            for topic in obj:
                descriptions = topic.description.all()
                desc_list = []
                for item in descriptions:
                    result = item.description
                    desc_list.append(result)
                
                result = topic.id, (desc_list, topic.item) 
                standard_full_join = ' '.join([str(i) for i in result]).lower()
                standard_full_join = stemSentence(standard_full_join)
                standard_full_join_tokens = word_tokenize(standard_full_join)
                standard_without_sw = [word for word in standard_full_join_tokens if not word in stop_words]
                full = topic.id, standard_without_sw
                objectives_list.append(full) 
            
    return(objectives_list)


def match_standard(teacher_input, standard_set, subject, grade_list):
    standards_list = []
    for grade in grade_list:
        obj = singleStandard.objects.filter(subject=subject, standards_set=standard_set, grade_level=grade)
        objectives_list = []
        for standard in obj:
                objective = standard.standard_objective,  standard.competency
                result = standard.id, objective
                standard_full_joined = ' '.join([str(i) for i in result[1] if not i in stopwords.words()])
                text_tokens = word_tokenize(teacher_input)
                tokens_without_sw = [word for word in text_tokens if not word in stopwords.words()]
                full_result = standard.id, tokens_without_sw
                standards_list.append(full_result) 
    return(standards_list)


def get_standard_matches(get_objective_matches, tokens_without_sw):
    prediction = []
    for standard_id, standard_full in get_objective_matches:
        Document1 = ' '.join([str(i) for i in standard_full])
        
        Document2 = ' '.join([str(i) for i in tokens_without_sw]) 
        corpus = [Document1,Document2]
        X_train_counts = count_vect.fit_transform(corpus)
        vectorizer = TfidfVectorizer()
        trsfm=vectorizer.fit_transform(corpus)
        result = cosine_similarity(trsfm[0:1], trsfm)
        result = result[0][1]
        total = standard_id, result
        prediction.append(total)
    prediction.sort(key=lambda x: x[1], reverse=True)
    full_result = []
    for item in prediction[:3]:
        full_result.append(item[0])
    return(full_result)


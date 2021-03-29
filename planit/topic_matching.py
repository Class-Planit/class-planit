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
from .textbook_matching import *
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

stop_words = ['i', "'", "'" '!', '.', ':', ',', '[', ']', '(', ')', '?', "'see", "see", 'x', '...',  'student', 'learn', 'objective', 'students', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"]

TAG_RE = re.compile(r'<[^>]+>')


def levenshtein_ratio_and_distance(s, t, ratio_calc = False):
    """ levenshtein_ratio_and_distance:
        Calculates levenshtein distance between two strings.
        If ratio_calc = True, the function computes the
        levenshtein distance ratio of similarity between two strings
        For all i and j, distance[i,j] will contain the Levenshtein
        distance between the first i characters of s and the
        first j characters of t
    """
    # Initialize matrix of zeros
    rows = len(s)+1
    cols = len(t)+1
    distance = np.zeros((rows,cols),dtype = int)

    # Populate matrix of zeros with the indeces of each character of both strings
    for i in range(1, rows):
        for k in range(1,cols):
            distance[i][0] = i
            distance[0][k] = k

    # Iterate over the matrix to compute the cost of deletions,insertions and/or substitutions    
    for col in range(1, cols):
        for row in range(1, rows):
            if s[row-1] == t[col-1]:
                cost = 0 # If the characters are the same in the two strings in a given position [i,j] then the cost is 0
            else:
                # In order to align the results with those of the Python Levenshtein package, if we choose to calculate the ratio
                # the cost of a substitution is 2. If we calculate just distance, then the cost of a substitution is 1.
                if ratio_calc == True:
                    cost = 2
                else:
                    cost = 1
            distance[row][col] = min(distance[row-1][col] + 1,      # Cost of deletions
                                 distance[row][col-1] + 1,          # Cost of insertions
                                 distance[row-1][col-1] + cost)     # Cost of substitutions
    if ratio_calc == True:
        # Computation of the Levenshtein Distance Ratio
        Ratio = ((len(s)+len(t)) - distance[row][col]) / (len(s)+len(t))
        return Ratio
    else:
        # print(distance) # Uncomment if you want to see the matrix showing how the algorithm computes the cost of deletions,
        # insertions and/or substitutions
        # This is the minimum number of edits needed to convert string a to string b
        return "The strings are {} edits away".format(distance[row][col])



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

def check_matches_topics(teacher_input, standard):
    text_split = teacher_input.lower().split()
    standard_split = standard.lower().split()
   
    if any(word in text_split for word in standard_split):
        return(True)
    else:
        return(False)


def match_topics(teacher_input, class_id, lesson_id):
 
        classroom_profile = classroom.objects.get(id=class_id)
       
        grade_list = classroom_profile.grade_level.all()
        standard_set = classroom_profile.standards_set
        
        class_objectives = lessonObjective.objects.get(id=lesson_id)
        topic_matches = class_objectives.objectives_topics.all()
       
        topics = topicInformation.objects.filter(id__in=topic_matches)
        topic_count = topics.count()
        results_list = []
        topic_ids = []
        for item in topics: 
            result = item.item
            item_id = item.id 
            results_list.append(result)
            topic_ids.append(item_id)


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
        if topic_count > 2:
            get_topic_ids = group_topic_texts(lesson_id)
        else:
            get_topic_ids = []

        for grade in grade_list:
                
                if get_topic_ids:
                     result_list = topicInformation.objects.filter(id__in=get_topic_ids)
                     obj = sorted(chain(topic_matches, result_list), key=lambda instance: instance.id)
                else:
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
                            
                            standard_full_join = ' '.join([str(i) for i in standard_full]).lower()
                            standard_full_join = stemSentence(standard_full_join)
                            standard_full_join_tokens = word_tokenize(standard_full_join)
                            standard_without_sw = [word for word in standard_full_join_tokens if not word in stop_words]

                            Document1 = ' '.join([str(i) for i in tokens_without_sw])
                            Document2 = ' '.join([str(i) for i in standard_without_sw])

                            Document1 = Document1.replace("'", '')
                            Document2 = Document2.replace("'", '')

                            corpus = [Document1,Document2]
                           
                            X_train_counts = count_vect.fit_transform(corpus)
                            vectorizer = TfidfVectorizer()
                            trsfm=vectorizer.fit_transform(corpus)
                            result = cosine_similarity(trsfm[0:1], trsfm)
                            result = result[0][1]
                            total = standard_full, result
                           
                            if result >= .20:
                                prediction.append(total)
                            elif result >= .08:
                                if any(word in Document1 for word in Document2):
                                    total = standard_full, 1
                                    prediction.append(total)
                            elif int(standard_full[0]) in topic_ids:
                                total = standard_full, 1
                                prediction.append(total)
                            else:
                                pass
                                
                    prediction.sort(key=lambda x: x[1], reverse=True)
                    
                    return(prediction)
                else:
                    return(None)


def match_topics_text_uploads(text_query, class_id, lesson_id):
    classroom_profile = classroom.objects.get(id=class_id)
    standard_set = classroom_profile.standards_set
    class_objectives = lessonObjective.objects.get(id=lesson_id)
    subject = class_objectives.subject
    grade_list = classroom_profile.grade_level.all()
    prediction = []
    total_lines = []
    for item in text_query:
        content = item.line_text
        total_lines.append(content)

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
            

            
            for standard_full in objectives_list:
                    
                    standard_full_join = ''.join([str(i) for i in standard_full]).lower()
                    Document1 = ''.join([str(i) for i in total_lines])
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
                        if result >= .15:
                            prediction.append(total)
                        
    prediction.sort(key=lambda x: x[1], reverse=True)

    return(prediction)


def match_lesson_topics(teacher_input, class_id, lesson_id):
    pass


def extra_function():
    classroom_profile = classroom.objects.get(id=class_id)
    standard_set = classroom_profile.standards_set
    class_objectives = lessonObjective.objects.get(id=lesson_id)
    subject = class_objectives.subject
    grade_list = classroom_profile.grade_level.all()
    matched_text = lessonText.objects.filter(matched_lesson=lesson_id).first()
    text = matched_text.activities
    text = remove_tags(text)
    teacher_input_stem = stemSentence(text)
    text_tokens = word_tokenize(teacher_input_stem)

    tokens_without_sw = [word for word in text_tokens if not word in stop_words]
    prediction = []
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
                    result = topic.id, (topic.item, topic.item)
                    objectives_list.append(result) 
            
            
            for standard_full in objectives_list:
                    standard_full_join = ''.join([str(i) for i in standard_full[1]]).lower()
                    standard_full_joined = stemSentence(standard_full_join)
                    
                    Document1 = ''.join([str(i) for i in tokens_without_sw]).lower()
                    Document2 = standard_full_joined
                    corpus = [Document1,Document2]
                    X_train_counts = count_vect.fit_transform(corpus)
                    vectorizer = TfidfVectorizer()
                    trsfm=vectorizer.fit_transform(corpus)
                    result = cosine_similarity(trsfm[0:1], trsfm)
                    result = result[0][1]
                    total = standard_full, result
                    prediction.append(total)
    
    prediction.sort(key=lambda x: x[1], reverse=True)

    return(prediction)




def split_matched_text(teacher_input):
    if teacher_input:
        soup = BeautifulSoup(teacher_input)

        return(soup.text)
    else:
        return(None)

 
def split_matched_terms(teacher_input, class_id, lesson_id):
    
    classroom_profile = classroom.objects.get(id=class_id)
    standard_set = classroom_profile.standards_set
    class_objectives = lessonObjective.objects.get(id=lesson_id)
    subject = class_objectives.subject
    grade_list = classroom_profile.grade_level.all()

    if teacher_input:
        soup = BeautifulSoup(teacher_input)
        lines = soup.findAll('tr')
        topic_lists = []
        for one_line in lines:
            items = one_line.findAll('td')
            if items:
                word = items[0]
                word = word.text
                
                for grade in grade_list: 
                    topic_term, created = topicInformation.objects.get_or_create(subject=subject, standard_set=standard_set, grade_level=grade, item=word)

                    descriptions = items[1]
                    for desc in descriptions:
                        lines = one_line.findAll('p')
                        
                        for item in lines:
                            try:
                                line = item.text
                            
                                if topicInformation.objects.filter(id=topic_term.id, description=line).exists():
                                    pass
                                else:
                                    description_create, created = topicDescription.objects.get_or_create(description=line) 
                                    all_matches = topic_term.description.all()
                                    update_term = topic_term.description.add(description_create)
                            except: 
                                pass


                    topic_lists.append(topic_term)

        for topic in topic_lists:
            update_objective = class_objectives.objectives_topics.add(topic)



def split_matched_activities(teacher_input, class_id, lesson_id, user_id):
    user_profile = User.objects.get(id=user_id)
    classroom_profile = classroom.objects.get(id=class_id)
    standard_set = classroom_profile.standards_set
    class_objectives = lessonObjective.objects.get(id=lesson_id)
    subject = class_objectives.subject
    grade_list = classroom_profile.grade_level.all()
    all_selected = selectedActivity.objects.filter(lesson_overview=class_objectives)
    for item in all_selected:
        item.is_selected = False
        item.save()
    
    if teacher_input:
        soup = BeautifulSoup(teacher_input)

        lines = soup.findAll('li')
        line_2 = soup.findAll('p')
        p_lines = []
        for p in line_2:
            p_lines.append(p.text)
        
        line2 = ''.join([str(i) for i in p_lines])

        for line in lines:
            if len(line.text) >= 2:
                new, created = selectedActivity.objects.get_or_create(lesson_overview=class_objectives, lesson_text=line.text, created_by=user_profile)
                new.is_selected = True 
                new.save()

        if len(line2) >= 2:
            new, created = selectedActivity.objects.get_or_create(lesson_overview=class_objectives, lesson_text=line2, created_by=user_profile)
            new.is_selected = True 
            new.save()

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
                print(obj)
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


def get_new_lesson(demo_wording, topic_list, user_id, lesson_id):
    user_profile = User.objects.get(id=user_id)
    lesson_match = lessonObjective.objects.get(id=lesson_id)
    topic_results = []
    for topic in topic_list:
        tt_list = topic.topic_type.all()
        for item in tt_list:
            topic_results.append(item) 

    lesson_templates = lessonTemplates.objects.filter(components__in=topic_results)

    for temp in lesson_templates:
        lesson_wording = temp.wording
        verb = temp.verb
        work_product = temp.work_product
        bloom = temp.bloom
        mi = temp.mi
        new_wording = lesson_wording.replace('DEMO_KS', demo_wording)
        new, created = selectedActivity.objects.get_or_create(created_by=user_profile , template_id=temp.id , lesson_overview = lesson_match, lesson_text = new_wording, verb = verb, work_product = work_product, bloom = bloom, mi = mi, is_admin = False)


#Show students examples of <<DEMONSTRATION>>. <<GROUPING>> Instruct students to <<VERB>> by <<DEMONSTRATION>> <<WORK_PRODUCT>>
def get_lessons(lesson_id, user_id):
    user_profile = User.objects.get(id=user_id)
    lesson_match = lessonObjective.objects.get(id=lesson_id)
    topic_matches = lesson_match.objectives_topics.all()
    demo_ks = lesson_match.objectives_demonstration.all()
    grouping = 'in groups of two'

    
    topic_list = topicInformation.objects.filter(id__in=topic_matches)
    multi_activity = get_multiple_types_activity(topic_list)
    
    teacher_objective = lesson_match.teacher_objective
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
        lesson_full = get_new_lesson(new_demo, line[1], user_id, lesson_id)

    return(wording_list)


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




def genQuestion(line, main_word):
    main_word = main_word.lower()
    vowels = ['a', 'e', 'i', 'o', 'u', 'A', 'E', 'I', 'O', 'U']
    """
    outputs question from the given text
    """

    if type(line) is str:  # If the passed variable is of type string.
        line = TextBlob(line)  # Create object of type textblob.blob.TextBlob


    bucket = {}  # Create an empty dictionary

    for i, j in enumerate(line.tags):  # line.tags are the parts-of-speach in English
        if j[1] not in bucket:
            bucket[j[1]] = i  # Add all tags to the dictionary or bucket variable


    question = ''  # Create an empty string

    # Create a list of tag-combination

    l1 = ['NNP', 'VBG', 'VBZ', 'IN']
    l2 = ['NNP', 'VBG', 'VBZ']

    l3 = ['PRP', 'VBG', 'VBZ', 'IN']
    l4 = ['PRP', 'VBG', 'VBZ']
    l5 = ['PRP', 'VBG', 'VBD']
    l6 = ['NNP', 'VBG', 'VBD']
    l7 = ['NN', 'VBG', 'VBZ']

    l8 = ['NNP', 'VBZ', 'JJ']
    l9 = ['NNP', 'VBZ', 'NN']

    l10 = ['NNP', 'VBZ']
    l11 = ['PRP', 'VBZ']
    l12 = ['NNP', 'NN', 'IN']
    l13 = ['NN', 'VBZ']

   
    if all(key in  bucket for key in l1): #'NNP', 'VBG', 'VBZ', 'IN' in sentence.
        question = 'What' + ' ' + line.words[bucket['VBZ']] +' '+ line.words[bucket['NNP']]+ ' '+ line.words[bucket['VBG']] + '?'

    
    elif all(key in  bucket for key in l2): #'NNP', 'VBG', 'VBZ' in sentence.
        if line.words[bucket['NNP']][0] in vowels:
            question = 'What' + ' ' + line.words[bucket['VBZ']] +' '+ ' an '+line.words[bucket['NNP']] +' '+ line.words[bucket['VBG']] + '?'
        else:
            question = 'What' + ' ' + line.words[bucket['VBZ']] +' '+ ' a '+line.words[bucket['NNP']] +' '+ line.words[bucket['VBG']] + '?'

    
    elif all(key in  bucket for key in l3): #'PRP', 'VBG', 'VBZ', 'IN' in sentence.
        question = 'What' + ' ' + line.words[bucket['VBZ']] +' '+ line.words[bucket['PRP']]+ ' '+ line.words[bucket['VBG']] + '?'

    
    elif all(key in  bucket for key in l4): #'PRP', 'VBG', 'VBZ' in sentence.
        question = 'What ' + line.words[bucket['PRP']] +' '+  ' does ' + line.words[bucket['VBG']]+ ' '+  line.words[bucket['VBG']] + '?'

    elif all(key in  bucket for key in l7): #'NN', 'VBG', 'VBZ' in sentence.
        if line.words[bucket['NNP']][0] in vowels:
            question = 'What' + ' ' + line.words[bucket['VBZ']] +' '+ ' an '+line.words[bucket['NN']] +' '+ line.words[bucket['VBG']] + '?'
        else:
            question = 'What' + ' ' + line.words[bucket['VBZ']] +' '+ ' a '+line.words[bucket['NN']] +' '+ line.words[bucket['VBG']] + '?'

    elif all(key in bucket for key in l8): #'NNP', 'VBZ', 'JJ' in sentence.
        if line.words[bucket['NNP']][0] in vowels:
            question = 'What' + ' ' + line.words[bucket['VBZ']] + ' ' + ' an '+line.words[bucket['NNP']] + '?'
        else:
            question = 'What' + ' ' + line.words[bucket['VBZ']] + ' ' + ' a '+line.words[bucket['NNP']] + '?'

    elif all(key in bucket for key in l9): #'NNP', 'VBZ', 'NN' in sentence
        if line.words[bucket['NNP']][0] in vowels:
            question = 'What' + ' ' + line.words[bucket['VBZ']] + ' ' + ' an '+line.words[bucket['NNP']] + '?'
        else:
            question = 'What' + ' ' + line.words[bucket['VBZ']] + ' ' + ' a '+line.words[bucket['NNP']] + '?'

    elif all(key in bucket for key in l11): #'PRP', 'VBZ' in sentence.
        if line.words[bucket['PRP']] in ['she','he']:
            question = 'What' + ' does ' + line.words[bucket['PRP']].lower() + ' ' + line.words[bucket['VBZ']].singularize() + '?'

    elif all(key in bucket for key in l10): #'NNP', 'VBZ' in sentence.
        question = 'What' + ' does ' + line.words[bucket['NNP']] + ' ' + line.words[bucket['VBZ']].singularize() + '?'

    elif all(key in bucket for key in l13): #'NN', 'VBZ' in sentence.
        question = 'What' + ' ' + line.words[bucket['VBZ']] + ' ' + line.words[bucket['NN']] + '?'

    if question:
        question_match, create = mainQuestion.objects.get_or_create(question=question, answer=line) 
        quest = str(question_match.question.lower())

        for word in main_word.split():

            if word in quest:

                new_quest = quest.replace(word, main_word)
                question_match.question = new_quest
                question_match.save()

    else:
        question_match = None

    return(question_match)


def find_ks_demos(class_id, lesson_id):
    classroom_profile = classroom.objects.get(id=class_id)
    grade_list = classroom_profile.grade_level.all()
    standard_set = classroom_profile.standards_set
    class_objectives = lessonObjective.objects.get(id=lesson_id)
    topic_matches = class_objectives.objectives_topics.all()
    topics = topicInformation.objects.filter(id__in=topic_matches)
    results_list = []
    topic_list = []
    for item in topics: 
        result = item.description.all()
        for word in result:
            results_list.append(word)
        topic_type = item.topic_type.all()
        for word in topic_type:
            topic_list.append(word)


    matched_list = []
    for topic in topic_list:
        matched_topic = topicTypes.objects.filter(item=topic).first()
        
        if matched_topic:
            matched_templates = LearningDemonstrationTemplate.objects.filter(topic_type=matched_topic)  
            if matched_templates not in matched_list:
                matched_list.append(matched_templates)

    final_results = []
    for item in topics: 
        #the actual topic word 
        topic_word = item.item
        for tt in item.topic_type.all():
            #the type of topic
            topic_t = tt.item
            for group in matched_list:
                for line in group:
                    #these are the items in the demo templates content is the word with the topic type 
                    content = line.content
                    for topic_type in line.topic_type.all():
                        #this is the topic type for the demo template 
                        topic_t_2 = topic_type.item
                        if topic_t in topic_t_2:
                            content = content.replace(topic_t_2, topic_word)
                            if content not in final_results:
                                final_results.append(content)

    
    return(final_results[:4])

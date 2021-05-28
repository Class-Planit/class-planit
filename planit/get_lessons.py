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
import json
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
from .get_activities import *
from .activity_builder import *
stop_words = ['i', "'", "'" '!', '.', ':', ',', '[', ']', '(', ')', '?', "'see", "see", 'x', '...',  'student', 'learn', 'objective', 'students', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"]

TAG_RE = re.compile(r'<[^>]+>')



 
#Show students examples of <<DEMONSTRATION>>. <<GROUPING>> Instruct students to <<VERB>> by <<DEMONSTRATION>> <<WORK_PRODUCT>>
def get_lessons(lesson_id, user_id):
    user_profile = User.objects.get(id=user_id)
    lesson_match = lessonObjective.objects.get(id=lesson_id)
    topic_matches = lesson_match.objectives_topics.all()
    demo_ks = lesson_match.objectives_demonstration.all()
    grouping = 'in groups of two'
    act_match = selectedActivity.objects.filter(lesson_overview = lesson_match, is_selected=True)
    matched_activities = []
    for sent in act_match:
        matched_activities.append(sent.lesson_text)

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

    single_activities = get_single_types_activity(topic_list)

    for line in single_activities:
        if line not in wording_list:
            wording_list.append(line)

   

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
                if item not in wording_list:
                    wording_list.append(item) 

            multi_noun = get_multiple_types_activity(result_list)
            for item in multi_noun:
                if item not in wording_list:
                    wording_list.append(item) 



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
                            result = new_wording, result_one.item, item, 'single'            
                            if result not in wording_list:
                                wording_list.append(result) 

    


    
    run_it = get_activity_mask(topic_list)
    activities_full = []
    temp_ids_list = []
    demo_list_sect = []

    for line in wording_list:
        sentence = line[0]
        topic = line[1]
        t_type = line[2]
        d_type = line[3]

        wording_split = sentence.split()
        first_word = wording_split[0]
        tokens = nlp(first_word)
        new_verb = tokens[0]._.inflect('VBG')
        new_demo = sentence.replace(first_word, new_verb) 
        
        lesson_full = get_new_lesson(new_demo, topic, d_type, t_type, lesson_id, user_profile.id)
        
        for item in lesson_full:
            temp_id = item.template_id
            text_s = item.lesson_text
            text_demo = item.ks_demo
            if text_demo not in demo_list_sect:
                demo_list_sect.append(text_demo)
                if text_s not in matched_activities:
                    if temp_id not in temp_ids_list:
                        temp_ids_list.append(temp_id)
                        activity = {'id': item.id, 'activity': item.lesson_text}
                        activities_full.append(activity)
    
    return(activities_full)

def get_mi_analytics_count(mi_list):
    mi_dict = {'Logical': 0, 'Verbal': 0, 'Musical': 0,  'Visual': 0,  'Movement': 0}
    mi_count = len(mi_list)
    for item in mi_list:
        if item == 1:
            mi_dict['Verbal'] = ((mi_dict['Verbal']  + 1)/mi_count) * 100
        elif item == 2:
            mi_dict['Visual'] = ((mi_dict['Visual']  + 1)/mi_count) * 100
        elif item == 3:
            mi_dict['Musical'] = ((mi_dict['Musical']  + 1)/mi_count) * 100
        elif item == 4:
            mi_dict['Movement'] = ((mi_dict['Movement'] + 1)/mi_count) * 100
        else:
            mi_dict['Logical'] = ((mi_dict['Logical']  + 1)/mi_count) * 100


    return(mi_dict) 

def get_bl_analytics_count(bl_list):
    bl_dict = {'Remember': 0, 'Understand': 0, 'Analyze': 0,  'Evaluate': 0,  'Create': 0}
    bl_count = len(bl_list)
    for item in bl_list:
        if item == 1:
            bl_dict['Remember'] = ((bl_dict['Remember'] + 1)/bl_count) * 100
        elif item == 2:
            bl_dict['Understand'] = ((bl_dict['Understand'] + 1)/bl_count) * 100
        elif item == 3:
            bl_dict['Analyze'] = ((bl_dict['Analyze'] + 1)/bl_count) * 100
        elif item == 4:
            bl_dict['Evaluate'] = ((bl_dict['Evaluate'] + 1)/bl_count) * 100
        else:
            bl_dict['Create'] = ((bl_dict['Create'] + 1)/bl_count) * 100

    return(bl_dict) 

def label_blooms_activities_analytics(lesson_id):
    class_objectives = lessonObjective.objects.get(id=lesson_id)
    matched_activities = selectedActivity.objects.filter(lesson_overview=class_objectives, is_selected=True)
    class_standards = class_objectives.objectives_standards.all()
    matched_standards = singleStandard.objects.filter(id__in=class_standards)
    
    bl_list = []
    bl_names = ('Remember', 'Understand', 'Analyze',  'Evaluate',  'Create')
    for activity in matched_activities:
        act_bl = int(activity.bloom)
        bl_list.append(act_bl)


    bl_list.sort()

    bl_high = (bl_list[-1]/6) * 100 
    bl_count = len(bl_list)


    bl_length = len(set(str(bl_count)))

    colors = ('bg-primary', 'bg-secondary', 'bg-success', 'bg-danger', 'bg-warning')
    bl_names = ('Remember', 'Understand', 'Analyze',  'Evaluate',  'Create')
    bl_Count = [1,2,3,4,5]
    bl_list_full = []
    for item in bl_Count:
        item_count = bl_list.count(item)
        zero_count = item - 1 
        name = bl_names[zero_count]
        color = colors[zero_count]
        avg = item_count/bl_count * 100 
        results = {'name': name, 'count': avg, 'color': color}
        if results not in bl_list_full:
            bl_list_full.append(results)


    return(bl_list_full)



def label_mi_activities_analytics(lesson_id):
    class_objectives = lessonObjective.objects.get(id=lesson_id)
    matched_activities = selectedActivity.objects.filter(lesson_overview=class_objectives, is_selected=True)
    class_standards = class_objectives.objectives_standards.all()
    matched_standards = singleStandard.objects.filter(id__in=class_standards)
    


    mi_list = []

    for activity in matched_activities:
        act_mi = int(activity.mi)
        mi_list.append(act_mi)


    mi_list.sort() 


    mi_count = len(mi_list)


    mi_length = len(set(str(mi_count)))

    colors = ('bg-primary', 'bg-secondary', 'bg-success', 'bg-danger', 'bg-warning')
    mi_names = ('Verbal',  'Visual', 'Musical', 'Movement', 'Logical')
    mi_Count = [1,2,3,4,5]
    mi_list_full = []
    for item in mi_Count:
        item_count = mi_list.count(item)
        zero_count = item - 1 
        name = mi_names[zero_count]
        color = colors[zero_count]
        avg = item_count/mi_count * 100 
        results = {'name': name, 'count': avg, 'color': color}
        if results not in mi_list_full:
            mi_list_full.append(results)

    return(mi_list_full)


def retention_activities_analytics(lesson_id):
    class_objectives = lessonObjective.objects.get(id=lesson_id)
    matched_activities = selectedActivity.objects.filter(lesson_overview=class_objectives, is_selected=True)

    class_standards = class_objectives.objectives_standards.all()
    matched_standards = singleStandard.objects.filter(id__in=class_standards)
    
    passive = ('watch', 'listen', 'video', 'song')
    middle = ('notes', 'worksheet', 'complete', 'write', 'type')
    active = ('present', 'presentation', 'discuss', 'discussion', 'debate', 'group', 'teams', 'pairs', 'explain')

    if matched_activities:
        
        active_count = 0
        middle_count = 0 
        passive_count = 0 
        activity_results = 0
        for activity in matched_activities:
            activity_text = activity.lesson_text
            split_activity = activity_text.split()
            if any(word in activity_text for word in active):
                activity_results = activity_results + 3
                active_count = active_count + 1
            elif any(word in activity_text for word in middle):
                activity_results = activity_results + 2
                middle_count = middle_count + 1
            elif any(word in activity_text for word in passive):
                activity_results = activity_results + 1
                passive_count = passive_count + 1
            else:
                pass
 
        activity_count = matched_activities.count()
        remaining = activity_count - active_count - middle_count
        passive_count = passive_count + remaining 

        total_count = activity_count

        retention_avg = (activity_results/(total_count*3)) * 100
        retention_avg  = round(retention_avg)
        passive_per = (passive_count/total_count) * 100
        middle_per = (middle_count/total_count) * 100
        active_per = (active_count/total_count) * 100

        if retention_avg >= 60:
            text = 'Your retention rate is high because your lessons include active learning'
        elif retention_avg >= 30:
            text = 'Your retention rate may be average because students practice and take notes.'
        else:
            text = 'Try improving your retention rate by including a presentation of knowledge or discussion'
        
        results = {'avg': retention_avg, 'text': text, 'passive': passive_per, 'middle': middle_per, 'active': active_per}
    else:
        text = 'Add activities to view results'
        results = {'avg': 0, 'text': text, 'passive': 25, 'middle': 50, 'active': 25}

    
    return(results)


def label_activities_analytics(lesson_id):

    class_objectives = lessonObjective.objects.get(id=lesson_id)
    matched_activities = selectedActivity.objects.filter(lesson_overview=class_objectives, is_selected=True)
    class_standards = class_objectives.objectives_standards.all()
    matched_standards = singleStandard.objects.filter(id__in=class_standards)
    
    stan_list = []
    for stan in matched_standards:
        stan_text = stan.standard_objective
        stan_list.append(stan_text)


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

    mi_analytics = get_mi_analytics_count(mi_list) 
    bl_analytics = get_bl_analytics_count(bl_list)


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
    corpus = [Document1,Document2]
    if len(Document2) and len(Document1) >= 4:
        X_train_counts = count_vect.fit_transform(corpus)
        vectorizer = TfidfVectorizer()
        trsfm=vectorizer.fit_transform(corpus)
        result = cosine_similarity(trsfm[0:1], trsfm)
        result = result[0][1] * 100
        final = mi_high, bl_high, diff_count, result, mi_analytics, bl_analytics, bl_count, mi_length
        return(final)


def get_lesson_sections(text_overview, class_id, lesson_id, user_id):
    user_profile = User.objects.get(id=user_id)
    classroom_profile = classroom.objects.get(id=class_id)
    standard_set = classroom_profile.standards_set
    class_objectives = lessonObjective.objects.get(id=lesson_id)
    subject = class_objectives.subject
    grade_list = classroom_profile.grade_level.all()
    matched_grade = gradeLevel.objects.filter(id__in=grade_list).first()
    all_selected = selectedActivity.objects.filter(lesson_overview=class_objectives, is_selected=True)
    for item in all_selected:
        is_selected = False
        item.save()
    topic_matches = class_objectives.objectives_topics.all()
    topic_lists_selected = topicInformation.objects.filter(id__in=topic_matches).order_by('item')

    create_topic_matches, created = matchedTopics.objects.get_or_create(lesson_overview=class_objectives)
    #pulls information from the TinyMCE html field and then parse the information 
    if text_overview:
        soup = BeautifulSoup(text_overview)

        #get the list of activities and parse them 
        activities_list =  soup.find('ul', {"id": "activity-div"})
        activities = [x.get_text() for x in activities_list.findAll('li')]
        
        #get the list of terms and parse them
        term_sets = []
        for row in soup.findAll('table')[0].tbody.findAll('tr'):
            term = row.find('th').contents
            if term[0]:
                description = row.find('td').contents
                
                
                for item in description:
                    if item:
                        try:
                            result = item.get_text(', ', strip=True)
                            result = result.split(", ")
                            for item in result:
                                if item:
                                    result = term[0], item
                                    if result not in term_sets:
                                        term_sets.append(result)
                        except:
                            result = item.split(", ")
                            for item in result:
                                if item:
                                    result = term[0], item
                                    if result not in term_sets:
                                        term_sets.append(result)

        #build new terms with new descriptions 
        key_term_list = list(term_sets)

        term_pairs = create_terms(key_term_list, lesson_id, matched_grade, user_id, standard_set)


        for activity in activities:
            l_act = label_activities(activity, lesson_id)
            new_activity, created = selectedActivity.objects.get_or_create(created_by=user_profile, lesson_overview=class_objectives, lesson_text=activity, verb=l_act[2], work_product=l_act[3], bloom=l_act[1], mi=l_act[0])
            new_activity.is_selected=True
            new_activity.save()
            find_topics = identify_topic(activity, lesson_id)
            if find_topics:
                for item in find_topics:
                    match_topic = topicInformation.objects.filter(id=item).first()
                    update_matches = create_topic_matches.objectives_topics.add(match_topic)

           
        #create and analyze new activities and update old activities
        ###update_lesson_activities = get_lesson_activities(activities, class_id, lesson_id, user_profile, class_objectives)

        #user the new activities and see if there are new key terms we should add to the list
        ####update_key_terms = get_lesson_key_terms(key_term_pair, class_id, lesson_id, user_profile, matched_grade, subject, standard_set, topic_lists_selected, class_objectives)
        

    return('Done')



def scratch_get_lessons(lesson_id, user_id):
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

    

    run_it = get_activity_mask(topic_list)
    activities_full = []
    for line in wording_list:
        wording = line[0]
        wording_split = wording.split()
        first_word = wording_split[0]
        tokens = nlp(first_word)
        new_verb = tokens[0]._.inflect('VBG')
        new_demo = wording.replace(first_word, new_verb) 
        
        lesson_full = get_new_lesson(new_demo, topic_list,  lesson_id, user_id)
        for item in lesson_full:
            activity = {'id': item.id, 'activity': item.lesson_text}
            activities_full.append(activity)


    return(activities_full)

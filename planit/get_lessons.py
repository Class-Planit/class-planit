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
wikipedia.set_rate_limiting(True)
engine = inflect.engine()
import spacy
import pyinflect
nlp = spacy.load('en_core_web_sm')
import random
from youtube_transcript_api import YouTubeTranscriptApi
from .get_key_terms import *
from .get_activities import *
from .activity_builder import *
from .tasks import *
stop_words = ['i', "'", "'" '!', '.', ':', ',', '[', ']', '(', ')', '?', "'see", "see", 'x', '...',  'student', 'learn', 'objective', 'students', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"]

TAG_RE = re.compile(r'<[^>]+>')





def get_transcript_nouns(match_textlines):
    full_sent_list = []
    
    results = tokenize.sent_tokenize(match_textlines)

    for sent in results:
        new_list = []
        sent = ' '.join(sent.split())

        sent_blob = TextBlob(sent)
        sent_tagger = sent_blob.pos_tags
        
        for y in sent_tagger:
              
            if 'NNP' in y[1]:
                full_sent_list.append(y[0])
            elif 'NNPS' in y[1]:
                full_sent_list.append(y[0])
            elif 'NN' in y[1]:
                full_sent_list.append(y[0])

    if full_sent_list:
        full_sent_list = full_sent_list[0]
        return(full_sent_list)

def get_transcript(video_id, video_db_id, lesson_id):
    video_match = youtubeSearchResult.objects.get(id=video_db_id)

    lesson_match = lessonObjective.objects.get(id=lesson_id)
    worksheet_full, created = worksheetFull.objects.get_or_create(lesson_overview=lesson_match, title=video_match.vid_id)
    full_trans = YouTubeTranscriptApi.get_transcript(video_id)

    all_lines = []
    for line in full_trans:
        text = line['text']
        text = text.strip()
        all_lines.append(text)
    
    new_lines = []
    line_count = 0
    for line in all_lines:
        line_count = line_count + 1
        line_create = youtubeLine.objects.create(vid_id=video_id, line_num=line_count, transcript_text=line)
        video_match.transcript_lines.add(line_create)
        if(line_count%4==0):
            noun_result = get_transcript_nouns(line)
            if noun_result:
                if noun_result in line:
                    new_line = line.replace(noun_result, "_________")
                    create_question = topicQuestionitem.objects.create(is_video=True, lesson_overview=lesson_match, subject=lesson_match.subject, Question=new_line, Correct=noun_result, item=video_db_id, explanation=line, trans_line_num=line_count)
                    worksheet_full.questions.add(create_question)

    
    return('Done')





def video_id(url):
    """
    Examples:
    - http://youtu.be/SA2iWivDJiE
    - http://www.youtube.com/watch?v=_oPAwA_Udwc&feature=feedu
    - http://www.youtube.com/embed/SA2iWivDJiE
    - http://www.youtube.com/v/SA2iWivDJiE?version=3&amp;hl=en_US
    """
    o = urlparse(url)
    if o.netloc == 'youtu.be':
        return o.path[1:]
    elif o.netloc in ('www.youtube.com', 'youtube.com'):
        if o.path == '/watch':
            id_index = o.query.index('v=')
            return o.query[id_index+2:id_index+13]
        elif o.path[:7] == '/embed/':
            return o.path.split('/')[2]
        elif o.path[:3] == '/v/':
            return o.path.split('/')[2]
    return None

def youtube_results(text, lesson_id):

    class_objectives = lessonObjective.objects.get(id=lesson_id)
    class_objectives_list = str(class_objectives.teacher_objective)
    topics = class_objectives.objectives_topics.all()
    topic_list = []
    for item in topics:
            title = item.item
            topic_list.append(title)
    
    class_topics = ' '.join([str(i) for i in topic_list])


    combined = class_objectives_list

    params = {
    "engine": "youtube",
    "search_query": combined,
    'api_key': config('api_key')
    }

    search = GoogleSearch(params)
    results = search.get_dict()
   
    try:
            video_results = results['video_results']
            return(video_results)
    except:
            return(None)


 
#Show students examples of <<DEMONSTRATION>>. <<GROUPING>> Instruct students to <<VERB>> by <<DEMONSTRATION>> <<WORK_PRODUCT>>
def get_lessons_ajax(lesson_id, user_id):
    
    user_profile = User.objects.get(id=user_id)
    lesson_match = lessonObjective.objects.get(id=lesson_id)
    topic_matches = lesson_match.objectives_topics.all()
    demo_ks = lesson_match.objectives_demonstration.all()
    grouping = 'in groups of two'
    act_match = selectedActivity.objects.filter(lesson_overview = lesson_match, is_selected=True)
    rec_act_match = selectedActivity.objects.filter(lesson_overview = lesson_match, is_selected=False)

    matched_activities = []
    temp_ids_list = []
    for sent in act_match:
        matching = sent.template_id
        temp_ids_list.append(matching)
        matched_activities.append(sent.lesson_text)




    topic_list = topicInformation.objects.filter(id__in=topic_matches)
    activities_full = []
    if rec_act_match.count() <= 5: 
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
                                result = new_wording, result_one.item, item, 'single', demo.id            
                                if result not in wording_list:
                                    wording_list.append(result) 

        mi_labels = [' ', 'Verbal', 'Visual', 'Musical', 'Movement', 'Logical']
        bl_labels = [' ', 'Remember', 'Understand', 'Apply', 'Analyze', 'Evaluate', 'Create']
        colors = [' ', 'primary', 'secondary', 'success', 'danger', 'warning', 'light']
        font_a  = [' ', 'microphone', 'eye', 'music', 'walking', 'puzzle-piece']
        
        
        demo_list_sect = []

        lesson_full_List = []
        random.shuffle(wording_list)
        for line in wording_list:

            sentence = line[0]
            topic = line[1]
            t_type = line[2]
            d_type = line[3]
            demo_id = line[4]
            wording_split = sentence.split()
            first_word = wording_split[0]
            tokens = nlp(first_word)
            new_verb = tokens[0]._.inflect('VBG')
            new_demo = sentence.replace(first_word, new_verb) 

            lesson_full = get_new_lesson(new_demo, topic, d_type, t_type, lesson_id, user_profile.id, demo_id)
            for item in lesson_full:
                lesson_full_List.append(item)
            random.shuffle(lesson_full_List)
    else:        
        lesson_full_List = rec_act_match[:5]

    for item in lesson_full_List:
        temp_id = item.template_id
        text_s = item.lesson_text
        text_demo = item.ks_demo
        bl = item.bloom
        mi = item.mi
        ret = item.ret_rate
        matching = item.template_id
        if matching not in temp_ids_list:
            temp_ids_list.append(matching)
            activity = {'id': item.id, 'activity': item.lesson_text, 'bl_color': item.bl_color, 'bl_label': item.bl_labels, 'mi_color': item.mi_color, 'mi_label': item.mi_labels, 'mi_icon': item.mi_icon, 'ret':ret}
            activities_full.append(activity)
    

    return(activities_full)

def label_blooms_activities_analytics(lesson_id):
    #each activity is given a blooms level
    #this counts the number of occurences of each blooms level and divides by the total number to get a %
    class_objectives = lessonObjective.objects.get(id=lesson_id)
    matched_activities = selectedActivity.objects.filter(lesson_overview=class_objectives, is_selected=True)
    if matched_activities:
        bl_list = []
        bl_names = ('Remember', 'Understand', 'Analyze',  'Evaluate',  'Create')
        for activity in matched_activities:
            act_bl = int(activity.bloom)
            bl_list.append(act_bl)


        bl_list.sort()

        bl_count = len(bl_list)


        bl_length = len(set(str(bl_count)))

        #the blooms number is used as an index to find the color and label in the progress bar 
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


    
    else:
        bl_list_full = None
    return(bl_list_full)



def label_mi_activities_analytics(lesson_id):
    #each activity is given a blooms level
    #this counts the number of occurences of each blooms level and divides by the total number to get a %
    class_objectives = lessonObjective.objects.get(id=lesson_id)
    matched_activities = selectedActivity.objects.filter(lesson_overview=class_objectives, is_selected=True)

    mi_list = []

    if matched_activities:
        for activity in matched_activities:
            act_mi = int(activity.mi)
            mi_list.append(act_mi)


        mi_list.sort() 


        mi_count = len(mi_list)


        mi_length = len(set(str(mi_count)))

        #the mi number is used as an index to find the color and label in the progress bar 
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

    else:
        mi_list_full = None
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


def build_activity_list(soup, user_profile, class_objectives, lesson_id):
    #this function pulls in beautiful soup and pulls out the activities that will be used to create analytics and demonstrations of knowledge
    activities_list =  soup.find('ul', {"id": "activity-div"})
    activities = [x.get_text() for x in activities_list.findAll('li')]
    if len(activities) > 4:
        for activity in activities:
            l_act = label_activities(activity, lesson_id)
            new_activity, created = selectedActivity.objects.get_or_create(created_by=user_profile, lesson_overview=class_objectives, lesson_text=activity)
            if created:
                new_activity.verb=l_act[2]
                new_activity.work_product=l_act[3]
                new_activity.bloom=l_act[1]
                new_activity.mi=l_act[0]
            new_activity.is_selected=True
            new_activity.save()
            find_topics = identify_topic(activity, lesson_id)
            if find_topics:
                for item in find_topics:
                    match_topic = topicInformation.objects.filter(id=item).first()
                    update_matches = create_topic_matches.objectives_topics.add(match_topic)
                    update_activity = new_activity.objectives_topics.add(match_topic)




def save_big_questions_list(soup, user_profile, class_objectives, lesson_id):
    lesson_match = lessonObjective.objects.get(id=lesson_id) 
    #this function pulls in beautiful soup and pulls out the activities that will be used to create analytics and demonstrations of knowledge
    current_questions = googleRelatedQuestions.objects.filter(lesson_plan=lesson_match, is_selected=True).delete()
    questions = []
    for row in soup.findAll('li', {"id": "full_question"}):
        question = row.find('h6').contents
        answer = row.find('p').contents

        if len(question[0]) > 5:
            match_question = googleRelatedQuestions.objects.create(question=question[0], snippet=answer[0], is_selected=True, lesson_plan=lesson_match)
 
def build_key_terms_list(soup, user_profile, class_objectives, lesson_id, matched_grade, standard_set):
    #this takes the beautiful soup and pulls out key terms to save for changes and create more connections. 
    term_sets = []
    for row in soup.findAll('table')[0].tbody.findAll('tr'):
        term = row.find('th').contents
        if term[0]:
            description = row.find('td').contents
            for item in description:
                if item:
                    try:
                        result = item.get_text(';; ', strip=True)
                        result = result.split(";; ")
                        for item in result:
                            if item:
                                result = term[0], item
                                if result not in term_sets:
                                    term_sets.append(result)
                    except:
                        result = item.split(";; ")
                        for item in result:
                            if item:
                                result = term[0], item
                                if result not in term_sets:
                                    term_sets.append(result)

        #build new terms with new descriptions 
        key_term_list = list(term_sets)
        #located at get_key_terms.py
        term_pairs = create_terms(key_term_list, lesson_id, matched_grade, user_profile.id, standard_set)



def get_lesson_sections(text_overview, class_id, lesson_id, user_id):
    #this is the main function that reads the tinymce editor information and breaks it into activities and key terms.

    user_profile = User.objects.get(id=user_id)
    classroom_profile = classroom.objects.get(id=class_id)
    standard_set = classroom_profile.standards_set
    class_objectives = lessonObjective.objects.get(id=lesson_id)
    subject = class_objectives.subject
    matched_grade = class_objectives.current_grade_level

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

        build_activities = build_activity_list(soup, user_profile, class_objectives, lesson_id)

        build_key_terms = build_key_terms_list(soup, user_profile, class_objectives, lesson_id, matched_grade, standard_set)

        save_big_questions = save_big_questions_list(soup, user_profile, class_objectives, lesson_id)

    return('Done')




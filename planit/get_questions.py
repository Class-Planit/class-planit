# Run in python console
import nltk; nltk.download('stopwords')
import re
import numpy as np
import pandas as pd
from pprint import pprint
from .models import *
import bs4
from bs4 import BeautifulSoup
# spacy for lemmatization
import spacy

# Plotting tools
import pyLDAvis
import pyLDAvis.gensim  # don't skip this
import matplotlib.pyplot as plt
from textblob import TextBlob

# Enable logging for gensim - optional
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.ERROR)

import warnings
warnings.filterwarnings("ignore",category=DeprecationWarning)

# NLTK Stop words
from nltk.corpus import stopwords
stop_words = stopwords.words('english')
stop_words.extend(['from', 'subject', 're', 'edu', 'use'])
import spacy
import en_core_web_sm
nlp = en_core_web_sm.load()
from gensim.summarization.summarizer import summarize 
from gensim.summarization import keywords 
from sklearn.metrics import pairwise_distances_argmin
import nltk
from nltk import tokenize
from .lesson_planner import *

line = ['Civil War', '1861- 1865" Civil War "Union (North vs. Confederacy (South) Jefferson Davis- President of the Confederacy Abraham Lincoln- President of the United States" "1861- 1865" Civil War War between the North and the South']


def generate_multichoice(line):
    pass


def generate_vocab_match(line):
    pass


def generate_fib(line):
    line_text = line.line_text
    is_verb = False
    is_noun = False
    is_long = False
    sent = line_text.replace('|', ' ')
    sent = ' '.join(sent.split())
    sent_blob = TextBlob(sent)
    sent_tagger = sent_blob.pos_tags
    nouns = []
    for y in sent_tagger:
        if 'V' in y[1]:
            is_verb = True
    for y in sent_tagger:
        if len(y[1]) > 2:
            is_long = True
    for y in sent_tagger:
        word_index = sent_tagger.index(y)
        if 'NNP' in y[1]:
            is_noun = True
            result = y[0], word_index
            nouns.append(result)
        elif 'NNPS' in y[1]:
            is_noun = True
            result = y[0], word_index
            nouns.append(result)

    results = []
    if is_verb and is_noun and is_long:
        sent = re.sub(r'\(.*\)', '', sent)
        sent = re.sub('Chapter', '', sent)
        sent = re.sub('Rule Britannia!', '', sent)
        sent = re.sub('Description', '', sent)
        if sent not in results:
            last_noun = nouns[-1]
            for item, index in nouns:
                print('Last Noun --------', last_noun[1])
                last_num = last_noun[1]

                current = index
                next_noun = index + 1
                third_noun = index + 2
                noun_ranges = item
                if next_noun < last_num:
                    next_noun_word = nouns[index + 1]
                    if (int(next_noun_word[1]) - index) == 1:
                        noun_ranges = item, next_noun_word[0]

                        if third_noun < last_num:
                            third_noun_word = nouns[index + 2]
                            if (int(third_noun_word[1]) - index) == 1:
                                noun_ranges = item, next_noun_word[0], third_noun_word[0]
                        else:
                            noun_ranges = item, next_noun_word[0]
                    else:
                        noun_ranges = item
                        
                results.append(noun_ranges)

    print(results)
    return(results)


def generate_spelling(line):
    pass


def generate_true_false(line):
    pass


def generate_short_answer(line):
    line_text = line.line_text
    sent = ' '.join(line_text.split())
    questions = ['What ', 'Where ', 'How ', 'When was', 'When were', 'Which ', 'Who was', 'Who is' 'Explain ', 'Discuss ', 'Describe ']
    result = None
    for quest in questions:
        if quest in sent:
            result = sent

    return(result)



def generate_questions_text(line):
    pass


def generate_questions_topic(topic_lists):
    word_bank = []
    descriptions = []
    for topic in topic_lists:
        term = topic.item
        word_bank.append(term)
        lower_term = term.lower()
        word_bank.append(lower_term)
        description = topic.description.all()
        for item in description:
            item_id = item.id
            descriptions.append(item_id)

    matched_desriptions = topicDescription.objects.filter(id__in=descriptions)
    results = []
    for word in word_bank:
        for item in matched_desriptions:
            item_id = item.id
            topic_match = topicInformation.objects.filter(description=item_id).first()
            topic_item = topic_match.item
            description = item.description
            if word in description:
                new_description = description.replace(word, '_____________ ')
                if word == topic_item:
                    quest = new_description, topic_item, None
                elif word.lower() == topic_item.lower():
                    quest = new_description, topic_item, None
                else:
                    quest = new_description, word, topic_item

                results.append(quest)
            else:
                pass
        
    return(results)

def get_db_questions(lesson_id):
    pass

def build_questions(matched_lines):
    all_questions = []
    for line in matched_lines:
        question = generate_short_answer(line)
 
        if question:
            pass
        else:
            question = generate_fib(line)

        if question:
            all_questions.append(question)

    print(all_questions)


def get_lesson_activities(text_overview, class_id, lesson_id, user_id, class_objectives):

    print(text_overview)
    for item in text_overview:
        activity_match = item.text
        if len(activity_match) <= 3:
            pass
        else:
            if 'New' in item['class']:
                new,created = selectedActivity.objects.get_or_create(lesson_overview=class_objectives, lesson_text=item.text, created_by=user_id)
                new.is_selected = True 
                get_activity_labels = label_activities(item.text)
                new.verb = get_activity_labels[0][2]
                new.work_product = get_activity_labels[1]
                new.bloom = get_activity_labels[0][1]
                new.mi = get_activity_labels[0][0]
                new.save()
            else:
                activity_id = item['class']
                activity_match = selectedActivity.objects.filter(id=activity_id[0]).first()
                print(activity_match)
                if activity_match:
                    activity_match.lesson_text = item.text
                    activity_match.is_selected = True 
                    activity_match.save()


    return('Done')

                   



def get_lesson_key_terms(key_term_pair, class_id, lesson_id, user_id, grade_level, subject, standard_set, topic_lists_selected, class_objectives):
    class_objectives.objectives_topics.clear()
    
    for item in key_term_pair:
        
        term_id = item[0][1]
        term = item[0][0]
        description = item[1]

        if 'New' in term_id: 
            match_term = topicInformation.objects.filter(subject = subject, created_by=user_id, grade_level = grade_level, standard_set = standard_set , item = term).first()
            if match_term:
                pass
            else:
                match_term, created = topicInformation.objects.get_or_create(subject = subject, created_by=user_id, grade_level = grade_level, standard_set = standard_set , item = term)
        else:
            match_term = topicInformation.objects.filter(id=term_id).first()
            
            if match_term:
            
                if match_term.created_by == user_id:
                    match_term.item = term
                    match_term.is_admin = False      
                    match_term.save()
                else:
                    match_term.pk = None
                    match_term.id = None
                    match_term.created_by = user_id
                    match_term.item =  term
                    match_term.is_admin = False
                    match_term.save()

            else:
                match_term, created = topicInformation.objects.get_or_create(subject = subject, created_by=user_id, grade_level = grade_level, standard_set = standard_set , item = term)


        create_description, created = topicDescription.objects.get_or_create(description=description) 
        match_term.description.clear()
        match_term.description.add(create_description)

        if class_objectives.objectives_topics.filter(id=match_term.id).exists():
            pass
        else:
            class_objectives.objectives_topics.add(match_term)

        #STEP TWO : Remove Deleted Topics 
        #is there a selected term that is not in the key_term_pairs?
            #yes 
                #####| unselect this key term from the list 


def get_lesson_key_terms_extra(key_term_pair, class_id, lesson_id, user_id, grade_level, subject, standard_set):
    full_term = []
    description_list = []
    for selected_terms in topic_lists_selected:
        term = selected_terms.item
        full_term.append(term)
        for line in selected_terms.description.all():
            select_line = line.description
            description_list.append(select_line)

    if item[0] in full_term:
        if item[1] in description_list:
            pass
        
        for line in selected_terms.description.all():
            select_line = line.description
            description_list.append(select_line)
        
        result = term, description_list
        full_term.append(result)

    if item[0] in selected_terms.item:
        description_list = []
        for line in selected_terms.description.all():
            select_line = line.description
            description_list.append(select_line)

        if item[1] in description_list:
            pass
        else:
            create_description = topicDescription.objects.create(description=item[1]) 
            selected_terms.description.add(create_description)
    else:
        create_description = topicDescription.objects.create(description=item[1]) 
        create_term, created = topicInformation.objects.get_or_create(subject = subject, grade_level = matched_grade, standard_set = standard_set , item = item[0])
        create_term.description.add(create_description)
        class_objectives.objectives_topics.add(create_term)



def get_lesson_sections(text_overview, class_id, lesson_id, user_id):
    user_profile = User.objects.get(id=user_id)
    classroom_profile = classroom.objects.get(id=class_id)
    standard_set = classroom_profile.standards_set
    class_objectives = lessonObjective.objects.get(id=lesson_id)
    subject = class_objectives.subject
    grade_list = classroom_profile.grade_level.all()
    matched_grade = gradeLevel.objects.filter(id__in=grade_list).first()
    all_selected = selectedActivity.objects.filter(lesson_overview=class_objectives)
    topic_matches = class_objectives.objectives_topics.all()
    topic_lists_selected = topicInformation.objects.filter(id__in=topic_matches).order_by('item')


    if text_overview:
        soup = BeautifulSoup(text_overview)

        activities = soup.findAll('li', {"id": "activity"})
        key_terms = soup.findAll('td', {"id": "term"})
        key_descriptions = soup.findAll('td', {"id": "description"})


        

        terms = []
        for key_term in key_terms:
            term_id = key_term['class']
            result = key_term.text, term_id[0]
            terms.append(result)

        descriptions = []
        for key_description in key_descriptions:
            description = key_description.text
            if description:
                pass
            else:
                description = '- '
            descriptions.append(description)


        key_term_pair = zip(terms, descriptions)
        key_term_pair = list(key_term_pair)

        update_lesson_activities = get_lesson_activities(activities, class_id, lesson_id, user_profile, class_objectives)
        update_key_terms = get_lesson_key_terms(key_term_pair, class_id, lesson_id, user_profile, matched_grade, subject, standard_set, topic_lists_selected, class_objectives)
        

    return('Done')





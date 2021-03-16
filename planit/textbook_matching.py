# Run in python console
import nltk; nltk.download('stopwords')
import re
import numpy as np
import pandas as pd
from pprint import pprint
from .models import *

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
from nltk import pos_tag, word_tokenize

import re
from nltk.stem import PorterStemmer
porter = PorterStemmer()

alphabets= "([A-Za-z])"
prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
suffixes = "(Inc|Ltd|Jr|Sr|Co)"
starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
websites = "[.](com|net|org|io|gov)"


def stemSentence(sentence):
    token_words=word_tokenize(sentence)
    token_words
    stem_sentence=[]
    for word in token_words:
        stem_sentence.append(porter.stem(word))
        stem_sentence.append(" ")
    return "".join(stem_sentence)



def split_into_sentences(text):
    text = " " + text + "  "
    text = text.replace("\n"," ")
    text = re.sub(prefixes,"\\1<prd>",text)
    text = re.sub(websites,"<prd>\\1",text)
    if "Ph.D" in text: text = text.replace("Ph.D.","Ph<prd>D<prd>")
    text = re.sub("\s" + alphabets + "[.] "," \\1<prd> ",text)
    text = re.sub(acronyms+" "+starters,"\\1<stop> \\2",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>",text)
    text = re.sub(" "+suffixes+"[.] "+starters," \\1<stop> \\2",text)
    text = re.sub(" "+suffixes+"[.]"," \\1<prd>",text)
    text = re.sub(" " + alphabets + "[.]"," \\1<prd>",text)
    if "”" in text: text = text.replace(".”","”.")
    if "\"" in text: text = text.replace(".\"","\".")
    if "!" in text: text = text.replace("!\"","\"!")
    if "?" in text: text = text.replace("?\"","\"?")
    text = text.replace("    ",".<stop>")
    text = text.replace(".",".<stop>")
    text = text.replace("?","?<stop>")
    text = text.replace("!","!<stop>")
    text = text.replace("<prd>",".")
    sentences = text.split("<stop>")
    sentences = sentences[:-1]
    sentences = [s.strip() for s in sentences]
    return sentences



def match_topic_texts(subject, text_id):
    #ensure the matching is subject specific 
    topics = topicInformation.objects.filter(subject = subject)
    titles = textBookTitle.objects.get(id=text_id)
    textlines = textBookBackground.objects.filter(textbook=titles)
    for line in textlines:
        line_id = line.id
        text = line.line_text
        for topic in topics:
            topic_id = topic.id
            word = topic.item 
            if word in text:
                update_topic = topicInformation.objects.get(id=topic_id)
                update_line = textBookBackground.objects.get(id=line_id)
                update_topic.text_index.add(line_id)




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



def get_question_text(lesson_id):
    class_objectives = lessonObjective.objects.get(id=lesson_id)
    topic_matches = class_objectives.objectives_topics.all()
    topics = topicInformation.objects.filter(id__in=topic_matches)
    question_results = []
    all_topic_lines = []
    for topic in topics: 
        text_lines = topic.text_index.all()
        textlines = textBookBackground.objects.filter(line_counter__in=text_lines)
        lr = []
        for line in textlines:
            
            text = line.line_text
            questions = ['What ', 'Where ', 'How ', 'When ', 'Which ']
            for quest in questions:
                if quest in text:
                    all_topic_lines.append(text)


    return(all_topic_lines)


def get_cluster_text(lesson_id,user_id):

    user_profile = User.objects.get(id=user_id)
    class_objectives = lessonObjective.objects.get(id=lesson_id)
    topic_matches = class_objectives.objectives_topics.all()
 
    topics_selected = topicInformation.objects.filter(id__in=topic_matches)

    match_textbook = textBookTitle.objects.filter(subject=class_objectives.subject, uploaded_by=user_profile, lesson_id_num=lesson_id)
    topics_selected_two = textBookBackground.objects.filter(textbook__in=match_textbook)
    
    results = []
    for topic in topics_selected: 
        text_lines = topic.text_index.all()

        textlines = textBookBackground.objects.filter(id__in=text_lines)
        for item in textlines:
            results.append(item.line_counter)



    clusters = dict(enumerate(grouper(results), 1))
    sorted_clusters = sorted(clusters, key=lambda k: len(clusters[k]), reverse=True)

    total_clusters = []
    topic_clusters = []
    for item in sorted_clusters[:3]:
       

        for x, y in clusters.items():
            if item == x:
                low = y[0]
                high = y[1]
                if high > low:
                    match_textlines = textBookBackground.objects.filter(line_counter__range=[low,high])
                    topic_match = topicInformation.objects.filter(text_index__in=match_textlines).exclude(id__in=topics_selected)
                    match_textlines = []
                    if match_textlines not in total_clusters:
                        total_clusters.append(match_textlines)
                    if topic_match not in topic_clusters:
                        topic_clusters.append(topic_match)
  
    
    if topics_selected_two:
        cluster_result = []
        for item in topics_selected_two:
            match_textlines = textBookBackground.objects.filter(id=item.id)
            topic_match = topicInformation.objects.filter(text_index__in=text_match).exclude(id__in=topics_selected)
            result = text_match, topic_match
            if match_textlines not in total_clusters:
                total_clusters.append(match_textlines)
            if topic_match not in topic_clusters:
                        topic_clusters.append(topic_match)

    results = total_clusters, topic_clusters
    return(results)
        
def summ_text(match_textlines):
    summ_results = []
    for text_list in match_textlines:
        if text_list:
            line_group = []
            for line in text_list:
                text_info = line.line_text
                line_group.append(text_info)


            text_list_join = ''.join([str(i) for i in line_group])
            try:
                summ_words = summarize(text_list_join , word_count = 100) 
                summ_results.append(summ_words)
            except:
                pass

    return(summ_results) 





def get_statment_sent(match_textlines):
    full_sent_list = []
    for text_list in match_textlines:

        if text_list:
            for row in text_list:
                text_info = row.line_text
                text_list_join = ''.join([str(i) for i in text_info])
                results = tokenize.sent_tokenize(text_list_join)
            
                for sent in results:

                    is_verb = False
                    is_noun = False
                    sent = sent.replace('|', ' ')
                    sent_blob = TextBlob(sent)
                    sent_tagger = sent_blob.pos_tags
                    for y in sent_tagger:
                        if 'V' in y[1]:
                            is_verb = True
                    for y in sent_tagger:
                        if 'NNP' in y[1]:
                            is_noun = True
                        elif 'NNPS' in y[1]:
                            is_noun = True
                    remove_list = ['illustrations', 'cartoon', 'Figure', 'they', 'those', 'Name ', 'Circle ', 'Education.com ', 'The McGraw-Hill']

                    if is_verb and is_noun:
                        sent = re.sub(r'\(.*\)', '', sent)
                        sent = re.sub('Chapter', '', sent)
                        sent = re.sub('Rule Britannia!', '', sent)
                        sent = re.sub('Description', ' ', sent)
                        if any(word in sent for word in remove_list):
                            pass
                        else:
                            result = sent_tagger, row.id
                            if result not in full_sent_list:
                                full_sent_list.append(result)


    return(full_sent_list)   
  



def groupertwo(iterable):
    final_results = []
    for tb in match_textbook:
        
        lr = []
        textlines = textBookBackground.objects.filter(line_counter__in=text_lines).filter(textbook=tb.id)

        for line in textlines:
            l_count = line.line_counter
            lr.append(l_count)

        clusters = dict(enumerate(grouper(lr), 1))

        for x, y in clusters.items():
            get_textbooks = textBookBackground.objects.filter(line_counter__in=y).filter(textbook=tb.id)
            text = []
            for item in get_textbooks:
                text.append(item.line_text)
            if text:
                final_results.append(text)
    all_results.append(final_results)
    




def grouper(iterable):
    prev = None
    group = []
    for item in iterable:
        if not prev or item - prev <= 15:
            group.append(item)
        else:
            yield group
            group = [item]
        prev = item
    if group:
        yield group

def match_textbook_lines(text, class_id, lesson_id):

    classroom_profile = classroom.objects.get(id=class_id)
    standard_set = classroom_profile.standards_set
    class_objectives = lessonObjective.objects.get(id=lesson_id)
    teacher_input = class_objectives.teacher_objective

    blob = TextBlob(teacher_input)
    blob_result = blob.noun_phrases
    result_full = []
    for term in blob_result:
        if term in result_full:
            pass
        else:
            result_full.append(term)

    subject = class_objectives.subject
    grade_list = classroom_profile.grade_level.all()
    get_textbooks = textBookTitle.objects.filter(grade_level__in=grade_list, standards_set=standard_set, subject=subject)

    get_textlines = textBookBackground.objects.filter(textbook__in=get_textbooks)

    for x in text:
        text = x.item
        result_one = text.lower()
        result_full.append(result_one)


    return_list = []
    counters = []
    

    for line in get_textlines:
        text = line.line_text
        for word in result_full:
            if word in text.lower():
                result = word, line, line.line_counter
                counters.append(line.line_counter)
                return_list.append(result)
    if counters:
        clusters = dict(enumerate(grouper(counters), 1))
    
        top_num = 0
        results = None
        for x, y in clusters.items():
            y_Length = len(y)
            if y_Length > top_num:
                top_num = y_Length
                results = y
            else:
                pass

        get_textbooks = textBookBackground.objects.filter(line_counter__in=results)
        text = []
        for item in get_textbooks:
            text.append(item.line_text)

    
    return(text)



    


def generate_textbook(user_id, class_id, lesson_id, content, week_of):
    user_profile = User.objects.get(id=user_id)
    classroom_profile = classroom.objects.get(id=class_id)
    class_objectives = lessonObjective.objects.get(id=lesson_id)
    grade_levels = classroom_profile.grade_level.all()
    matched_grade_levels = gradeLevel.objects.filter(id__in=grade_levels)
    subject = class_objectives.subject
    standard_match = standardSet.objects.get(id=classroom_profile.standards_set_id)

    worksheet_title = '%s: %s for week of %s' % (user_profile, subject, week_of) 

    textbook_match, created = textBookTitle.objects.get_or_create(title=worksheet_title, standards_set=standard_match, subject=subject, uploaded_by=user_profile, lesson_id_num=lesson_id)
    for grade in grade_levels:
            update_text = textbook_match.grade_level.add(grade)
          


    text_id = textbook_match.id

    split_content = split_into_sentences(content)

    for line in split_content:
        get_lemma = stemSentence(line)
        obj, created = textBookBackground.objects.get_or_create(textbook=textbook_match, line_text=line, line_lemma=get_lemma)
        obj.line_counter = int(str(text_id) + str(obj.id)) 

        obj.save()
        
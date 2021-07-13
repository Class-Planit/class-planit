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

def get_sentence_nouns(match_textlines):
    full_sent_list = []

    results = tokenize.sent_tokenize(match_textlines)

    for sent in results:
        
        sent = ' '.join(sent.split())
        is_verb = False
        is_noun = False
        is_long = False
        sent = sent.replace('|', ' ')
        sent_blob = TextBlob(sent)
        sent_tagger = sent_blob.pos_tags
        

        for y in sent_tagger:
            
            if len(y[1]) > 2:
                is_long = True
            else: 
                pass    
            if 'NNP' in y[1]:
                is_noun = True
            elif 'NNPS' in y[1]:
                is_noun = True
            elif 'NN' in y[1]:
                is_noun = True
            elif 'JJ' in y[1]:
                is_noun = True
            else:
                pass

            remove_list = ['illustrations', 'cartoon', 'Figure', 'they', 'those', 'Circle ', 'Education.com']
            results = []
            if is_noun and is_long:

                sent = re.sub(r'\(.*\)', '', sent)
                sent = re.sub('Chapter', '', sent)
                sent = re.sub('Rule Britannia!', '', sent)
                sent = re.sub('Description', '', sent)
                if any(word in sent for word in remove_list):
                    pass
                else:
                    for item in sent_tagger:
                        is_noun = False
                        if 'NNP' in item[1]:
                            is_noun = True
                        elif 'NNPS' in item[1]:
                            is_noun = True
                        elif 'NN' in item[1]:
                            is_noun = True
                        elif 'JJ' in item[1]:
                            is_noun = True
                        if is_noun:
                            index = sent_tagger.index(item)
                            
                            result = item, index
                            if result[0][0] not in stop_words:
                                if result not in full_sent_list:
                                    full_sent_list.append(result)


    
    final_list = []
    for item in full_sent_list:
        first_word = item[0][0]
        word_index = item[1]
        next_index = word_index + 1
        next_next_word = word_index + 2
        for y in full_sent_list:
            if y[1] == next_index:
                second_word = y[0][0]

                combine_wording = first_word + ' ' + second_word
                for x in full_sent_list:
                    if x[1] == next_next_word:
                        third_word = x[0][0]
                        combine_wording = combine_wording + ' ' + third_word
                
                if combine_wording not in final_list:
                    final_list.append(combine_wording)
    
    if final_list:
        pass
    else:
        for item in full_sent_list:
            first_word = item[0][0]
            for word in match_textlines.split():

                if first_word.lower() == word.lower():
                    if first_word not in final_list:
                        final_list.append(first_word)




    return(final_list)



#Show students examples of <<DEMONSTRATION>>. <<GROUPING>> Instruct students to <<VERB>> by <<DEMONSTRATION>> <<WORK_PRODUCT>>
def get_lessons_full(topic_list, demo_ks, lesson_id, user_id):
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

    activities_full = []
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
            activity = {'id': item.id, 'activity': item.lesson_text}
            activities_full.append(activity)

    return(wording_list)


def get_new_lessons(lesson_id, user_id):
    user_profile = User.objects.get(id=user_id)
    lesson_match = lessonObjective.objects.get(id=lesson_id)
    subject_match = lesson_match.subject
    grade_match = lesson_match.current_grade_level
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
                    
                    demo_ks_match = LearningDemonstrationTemplate.objects.filter(topic_type__in=topic_one, subject=subject_match, grade_level=grade_match)
                    for demo in demo_ks_match:
                        wording = demo.content

                        topic_two = demo.topic_type.all()

                        for item in topic_two:
                            new_wording = wording.replace(str(item), result_one.item)  
                            result = new_wording, result_list
                          
                            if result not in wording_list:

                                wording_list.append(result) 

    


    activities_full = []
    for line in wording_list:
        
        sentence = line[0]
        topic = line[1]
        d_type = line[2]

        wording_split = sentence.split()
        first_word = wording_split[0]
        tokens = nlp(first_word)
        new_verb = tokens[0]._.inflect('VBG')
        new_demo = sentence.replace(first_word, new_verb) 
        lesson_full = get_new_lesson(new_demo, topic, d_type, lesson_id, user_profile.id)
        for item in lesson_full:
            activity = {'id': item.id, 'activity': item.lesson_text}
            activities_full.append(activity)

    return(activities_full)


def get_multiple_types_activity(topic_list):
    #find if there is a word in all the descriptions that is a noun as it may be types of the same thing?
    word_list = []
    t_type = []
    for topic in topic_list:
        words = topic.item
        d_types = topic.topic_type.all()
        d_matched = topicTypes.objects.filter(id__in=d_types)
        for item in d_matched:
            t_type.append(item.item)
        word_list.append(words)

    t_type = set(t_type)


    t_list = []
    for item in t_type:
        t_list.append(item)

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
                    new_verb = engine.plural_noun(y[0])
                    wording = 'outline of ' +  new_verb
                    result = wording, wordfreq[0][0], t_list, 'multi'
                    wording_list.append(result)
        

    return(wording_list)

    
def get_plural_types_activity(topic_list):
    word_list = []
    t_type = []
    for topic in topic_list:
        words = topic.item
        d_types = topic.topic_type.all()
        d_matched = topicTypes.objects.filter(id__in=d_types)
        for item in d_matched:
            t_type.append(item.item)
        word_list.append(words)

    t_type = set(t_type)

    t_list = []
    for item in t_type:
        t_list.append(item)
    words_list_full = ' '.join([str(i) for i in word_list])
    words_list_full = words_list_full.split()

    wordfreq = []
    for w in words_list_full:
        result = w, words_list_full.count(w)
        wordfreq.append(result)

    wordfreq.sort(key=lambda x: x[1], reverse=True)

    wording_options = ['characterize the different ', 'identify the different ', 'labeling the different ']
    random.shuffle(wording_options)
    wording_list = []

    if wordfreq[0][1] > 1:
        plural = engine.plural(wordfreq[0][0])
        if plural:
            wording = wording_options[0] +  plural
            result = wording, wordfreq[0][0], t_list, 'plural'
            wording_list.append(result)
        
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
    current_rec_list, created = reccomendedTopics.objects.get_or_create(matched_lesson=class_objectives)
    removed_t = current_rec_list.removed_topics.all()
    removed_topics = topicInformation.objects.filter(id__in=removed_t)
 
    topic_matches = class_objectives.objectives_topics.all()

    topics = topicInformation.objects.filter(id__in=topic_matches).exclude(id__in=removed_t)

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
        if result >= .30:
            objective_predictions.append(total)
        elif result >= .15:
            if any(word in Document1 for word in Document2):
                total = standard_id, result
                objective_predictions.append(total)
        elif standard_id in topic_ids:
            total = standard_id, 1
            objective_predictions.append(total)
        else:
            pass
                
    objective_predictions.sort(key=lambda x: x[1], reverse=True)
    full_result = []
    for item in objective_predictions:
        full_result.append(item)
    return(full_result)

def get_topic_matches(class_objectives, topic_count, grade_list, subject, standard_set, lesson_id, user_id):
    current_rec_list, created = reccomendedTopics.objects.get_or_create(matched_lesson=class_objectives)
    removed_t = current_rec_list.removed_topics.all()
    removed_topics = topicInformation.objects.filter(id__in=removed_t)
 
    if topic_count > 2:
        #we use textbook mapping after we have 3 topics 
        get_topic_ids = group_topic_texts(lesson_id)
    else:
        get_topic_ids = []

    objectives_list = []
    for grade in grade_list:
        topic_list = topicInformation.objects.filter(subject=subject, standard_set=standard_set, grade_level=grade).exclude(id__in=removed_t)

        #takes each relevant topic by subject, standards, and grade 
        if topic_list:
            for topic in topic_list:
                descriptions = topic.description.all()
                desc_list = get_description_string(topic.id, user_id)
                
                result = topic.id, (desc_list, topic.item) 
                topic_item_joined = ' '.join([str(i) for i in result[1]]).lower()
                
                topic_input_stem = stemSentence(topic_item_joined)

                topic_item_without_sw = [word for word in topic_input_stem.split() if not word in stop_words]
               
                full = topic.id, topic_item_without_sw
                objectives_list.append(full) 
               
    #returns a list of relevant topics that have been cleaned for comparison 

    return(objectives_list)

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
        all_d.append(line)

    final = ';; '.join(all_d)
    return(final)



def build_term_description(item, user_profile, is_secondary, lesson_objective):
    term = item[1]

    if len(term) >= 1:
        print('###########')
        print(term)
        print('###########')
        full_desc = ''.join(term[1])
        
        match_topic = topicInformation.objects.filter(item=term[0], created_by=user_profile, is_admin=False, from_wiki=True, grade_level= lesson_objective.current_grade_level, subject=lesson_objective.subject, standard_set=lesson_objective.standard_set).first()
        if match_topic:
            pass
        else:
            match_topic, created = topicInformation.objects.get_or_create(item=term[0], created_by=user_profile, is_admin=False, from_wiki=True, is_secondary=is_secondary, grade_level= lesson_objective.current_grade_level, subject=lesson_objective.subject, standard_set=lesson_objective.standard_set)
        new_description, created = topicDescription.objects.get_or_create(topic_id=match_topic.id, created_by=user_profile, is_admin=False, is_generated=True)
        if created:
            get_desc_summary = get_desciption_summary(term[0], full_desc)
            new_description.description = get_desc_summary
            new_description.is_generated = True
            new_description.save()
        add_description = match_topic.description.add(new_description)
        top_id = match_topic.id
        result = top_id, item[2]
        if item[0]:
            match_topic.text_index.add(item[0])
        
        return(result)

def build_wiki_topic_list(topics, lesson_id, user_profile, standards_nouns):
    lesson_objectives = lessonObjective.objects.get(id=lesson_id)
    not_selected_topics = []
    if topics:
        ''' There are topics that have already been selected 
        '''
        for top in topics:
            if top.is_secondary:
                top_list = [top.item]
                wiki_topics = wiki_results(lesson_id, user_profile.id, top_list)
                for item in wiki_topics:
                    result = build_term_description(item, user_profile, True, lesson_objectives)
                    if result[0] not in not_selected_topics:
                        not_selected_topics.append(result)
            else:
                top_list = [top.item]
                wiki_topics = wiki_results(lesson_id, user_profile.id, top_list)
                for item in wiki_topics:
                    result = build_term_description(item, user_profile, False, lesson_objectives)
                    if result[0] not in not_selected_topics:
                        not_selected_topics.append(result)

    else:
        ''' There are no topics selected for the Lesson Objective 
        '''
        wiki_topics = wiki_results(lesson_id, user_profile.id, standards_nouns)
        for item in wiki_topics:
            result = build_term_description(item, user_profile, False, lesson_objectives)
            if result[0] not in not_selected_topics:
                not_selected_topics.append(result)
        #we want to search wikipedia based on the main words in the objective 

    return(not_selected_topics)

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


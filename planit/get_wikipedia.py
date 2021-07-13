from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from django.db.models import Q, Sum
from .models import *
import numpy.random
from serpapi import GoogleSearch
import re
from itertools import chain
import nltk
from nltk import pos_tag, word_tokenize
from nltk.corpus import wordnet 
from nltk.tokenize import WordPunctTokenizer
from nltk import tokenize
import wikipedia
from youtube_search import YoutubeSearch
nltk.download('stopwords')
nltk.download('wordnet')
from textblob import TextBlob
import requests
from decouple import config, Csv
from rake_nltk import Rake
import re
from collections import Counter
#test comment 
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import random
wikipedia.set_rate_limiting(True)
count_vect = CountVectorizer()
from nltk.corpus import stopwords
stop_words = stopwords.words('english')
import wikipediaapi
wiki_wiki = wikipediaapi.Wikipedia('en')
stop_words.extend(['The', 'students', 'learn'])

stop_words = ['i', "'", "'" '!', '.', ':', ',', '[', ']', '(', ')', '?', "'see", "see", 'x', '...',  'student', 'learn', 'objective', 'students', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"]

def get_pdf_sent(full_results):
    full_sent_list = []
    text_list_join = ''.join([str(i) for i in full_results])
    results = tokenize.sent_tokenize(text_list_join)

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
        for y in sent_tagger:
            if 'V' in y[1]:
                is_verb = True
        for y in sent_tagger:
            if 'NNP' in y[1]:
                is_noun = True
            elif 'NNPS' in y[1]:
                is_noun = True
        remove_list = ['cite', 'index', 'special', 'Special', 'Category:', '/', 'File', 'Wikipedia:', 'Main_Page', 'Help:', '#', 'United_States', 'Overweight', 'Talk:']
        results = []
        if is_verb and is_noun and is_long:
            sent = re.sub(r'\(.*\)', '', sent)
            sent = re.sub('Chapter', '', sent)
            sent = re.sub('Rule Britannia!', '', sent)
            sent = re.sub('Description', '', sent)
            if any(word in sent for word in remove_list):
                pass
            else:
                if sent not in full_sent_list:
                    full_sent_list.append(sent)
    
    return(full_sent_list)

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

def check_topic_relevance(text, lesson_id):

    class_objectives = lessonObjective.objects.get(id=lesson_id)
    class_objectives_list = str(class_objectives.teacher_objective)

    Document1 = class_objectives_list
    Document2 = '%s %s' % (text[0], text[1])

    corpus = [Document1,Document2]
    X_train_counts = count_vect.fit_transform(corpus)
    vectorizer = TfidfVectorizer()
    trsfm=vectorizer.fit_transform(corpus)
    result = cosine_similarity(trsfm[0:1], trsfm)
    result = result[0][1]

    return(result)

def check_topic_wiki_relevance(text, topic_id):

    topic_match = topicInformation.objects.get(id=topic_id)
    desc_list = topic_match.description.all()
    d_match = topicDescription.objects.filter(id__in=desc_list)

    result_list = []
    for item in d_match:
        descriptions = item.description
        result_list.append(descriptions)

    desc_full = '; '.join(result_list)

    Document1 = desc_full
    Document2 = '%s %s' % (text[0], text[1])
    
    corpus = [Document1,Document2]
    X_train_counts = count_vect.fit_transform(corpus)
    vectorizer = TfidfVectorizer()
    trsfm=vectorizer.fit_transform(corpus)
    result = cosine_similarity(trsfm[0:1], trsfm)
    result = result[0][1]

    return(result)

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

  
        return(cleaned_list)

def get_topic_nouns(match_textlines, lesson_id):
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
            
    rel_nouns = []
    for item in final_list:
        check_relevance = check_topic_relevance(item, lesson_id)
        if check_relevance > .09:
            rel_nouns.append(item)


    return(rel_nouns)

def get_wiki_full(title, lesson_id, topic_id):

    text_title = 'Wiki: %s' % (title)
    textbook_match = textBookTitle.objects.filter(title=text_title)

    wiki_list = [] 
    if textbook_match:
        pass
    else:
        textbook_match = textBookTitle.objects.create(title=text_title)
        url = "https://en.wikipedia.org/wiki/%s" % (title)
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
        full_text = soup.get_text()
        f_text = tokenize.sent_tokenize(full_text)
        line_counter = 1
        for line in f_text:
            line_counter = line_counter + 1
            new_text, created = textBookBackground.objects.get_or_create(textbook=textbook_match , line_counter= line_counter, page_counter=1, line_text=line)
        
        link_list = []
        for link in soup.find_all("a"):
            term = link.string

            url = link.get("href", "")
            results = url.replace('/wiki/', '') 
            remove_list = ['cite', 'index', 'special', 'Special', 'Category:', '/', 'File', 'Wikipedia:', 'Main_Page', 'Help:', '#', 'United_States', 'Overweight', 'Talk:']
            if any(word in results for word in remove_list):
                    pass
            else:
                if results not in link_list:
                    link_list.append(results)

        wiki_titles = []
        

        for sentence in link_list[:10]:
                try:
                    wiki_search = wikipedia.page(sentence)
                    if wiki_search not in wiki_titles:
                        wiki_titles.append(wiki_search)
                except:
                        pass        

          

        for wiki_title in wiki_titles:       
                try:
                    topic_result = wikipedia.summary(wiki_title.title, sentences = 3, auto_suggest=False, redirect=True)
                    
                    result = check_topic_wiki_relevance(topic_result, lesson_id)
                    
                    if result >= .20:
                       
                        term = wiki_search.title, topic_result, result
                        wiki_list.append(create_wiki_topic)
                except wikipedia.DisambiguationError as e:
                        pass

            
        return(wiki_list)

def get_wiki_term_summary(search_item, wiki_title):
    topic_result = wiki_title.summary[:500]
    strip_sent = tokenize.sent_tokenize(topic_result)
    topic_r = ' '.join(strip_sent[:2])
    search_t = search_item.title()
    term = search_t, topic_r
    
    return(term)


def wiki_results(lesson_id, user_id, standards_nouns):
    final_terms = []
    wiki_titles = []

    remove_list = ['cite', 'index', 'special', 'Special', 'Category:', '/', 'File', 'Wikipedia:', 'Main_Page', 'Help:', '#', 'United_States', 'Overweight', 'Talk:']
    
    for search_item in standards_nouns:
        wiki_search = wiki_wiki.page(str(search_item))
        if wiki_search.exists():
            r_search = wiki_search.fullurl
            wiki_t = r_search, search_item
            w_summary = get_wiki_term_summary(search_item, wiki_search)
            sim_score = check_topic_relevance(w_summary, lesson_id)
            results = None, w_summary, sim_score
            if results not in final_terms:
                final_terms.append(results)
            if wiki_t not in wiki_titles:
                wiki_titles.append(wiki_t)

   
    wiki_count = 0
    for wiki_title in wiki_titles:

        matched_topic = topicInformation.objects.filter(item=wiki_title[1]).first()

        if matched_topic:
            lesson_match = lessonObjective.objects.filter(id=lesson_id, objectives_topics=matched_topic)

            if lesson_match:
                link_list = []
                
                textbook_match, created = textBookTitle.objects.get_or_create(title=wiki_title[0])
                if created:
                    #gets main item summary 
                    term = wiki_title[1]
                    wiki_count = wiki_count + 1
                    final_terms.append(term)
                    res = requests.get(wiki_title[0])
                    soup = BeautifulSoup(res.text, "html.parser")
                    if soup:
                        for link in soup.find_all("a"):
                            term = link.string
                            
                            url = link.get("href", "")
                            results = url.replace('/wiki/', '') 
                        
                            if any(word in results for word in remove_list):
                                    pass
                            else:
                                if results not in link_list:
                                    final = term, results
                                    if final not in link_list:
                                        link_list.append(final)

                        link_list = set(link_list)
                        full_text = soup.get_text()    
                        full_t = full_text.strip()
                        full_results = tokenize.sent_tokenize(full_t)
                        fresults = get_pdf_sent(full_results)
                        line_counter = 1
                        for line in fresults:
                            
                            line_counter = line_counter + 1
                            
                            a_string = line.rstrip("\n")
                            final_line = re.sub(r'\[.*\]', '', a_string)
                            
                            for word in link_list:
                                if word[0] is not None:
                                    if len(word[0]) >= 4:
                                        if word[0] in final_line:
                                            wiki_text = word[0], final_line
                                            new_text, created = textBookBackground.objects.get_or_create(textbook=textbook_match , header= word[0], section=word[1] ,page_counter=1, line_text=final_line)
                                            new_text.line_counter= line_counter
                                            new_text.save()

                else:
                    
                    new_text = textBookBackground.objects.filter(textbook=textbook_match)
                    
                    word_list = []
                    word_full = []
                    for word in new_text:
                        if word.header not in word_list:
                            word_list.append(word.header)
                            word_full.append(word)

                    random.shuffle(word_full)
                    word_counts = 0
                    for word in word_full:
                        if word.term_created == False:
                            if word_counts <= 10:
                                wiki_search = wiki_wiki.page(str(word.header))
                                if wiki_search.exists():
                                    r_search = wiki_search.fullurl
                                    
                                    secondary_term  = get_wiki_term_summary(word.header, wiki_search)
                                    
                                    sim_score = check_topic_relevance(secondary_term, lesson_id)
                                    if sim_score >= .10:
                                        results = word.id, secondary_term, sim_score
                                        word_counts = word_counts + 1
                                        word.term_created == True 
                                        word.save()
                                        if results not in final_terms:
                                            final_terms.append(results)
               
 
    return(final_terms)


from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from django.db.models import Q, Sum
from .models import *
import numpy.random
from serpapi import GoogleSearch
import re
from itertools import chain
import heapq
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
stoplist = set(stopwords.words("english"))

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
    top_match = class_objectives.objectives_topics.all()
    topic_matches = topicInformation.objects.filter(id__in=top_match)
    t_terms = []
    for word in topic_matches:
        t_terms.append(word.item)

    final_objective = ' '.join([class_objectives_list, str(t_terms)])

    Document1 = final_objective
    Document2 = text

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


def text_summary_nltk(text, term, sent_count):

    summ_text = re.sub(r'\[[0-9]*\]', ' ', text)
    summ_text = re.sub(r'\s+', ' ', summ_text)
    sentence_list = nltk.sent_tokenize(text)

    word_frequencies = {}
    for word in nltk.word_tokenize(summ_text):
        if word not in stoplist:
            if word not in word_frequencies.keys():
                word_frequencies[word] = 1
            else:
                word_frequencies[word] += 1

    maximum_frequncy = max(word_frequencies.values())

    for word in word_frequencies.keys():
        word_frequencies[word] = (word_frequencies[word]/maximum_frequncy)

    sentence_scores = {}
    for sent in sentence_list:
        for word in nltk.word_tokenize(sent.lower()):
            if word in word_frequencies.keys():
                if len(sent.split(' ')) < 30:
                    if sent not in sentence_scores.keys():
                        sentence_scores[sent] = word_frequencies[word]
                    else:
                        sentence_scores[sent] += word_frequencies[word]

    summary_sentences = heapq.nlargest(sent_count, sentence_scores, key=sentence_scores.get)

    summary = ' '.join(summary_sentences)
    summary = summary.replace('More items', '')
    summary = summary.replace('...', '')
    summary = re.sub(r"[-\"#/@;:<>{}`+=~|.!?,]", "", summary)

    return(summary)

def get_wiki_term_summary(search_item, wiki_title):
    topic_result = wiki_title.summary[:500]
    strip_sent = tokenize.sent_tokenize(topic_result)
    
    term_description = ' '.join(strip_sent[:2])
   
    search_term = search_item.title()
    term = term_description
    
    return(term)


def wiki_results(lesson_id, user_id, standards_nouns):
    word_counts = 0
    final_terms = []
    wiki_titles = []
    wiki_initial = []
    remove_list = ['cite', 'index', 'special', 'issn', 'ISSN', 'Special', 'Category:', '/', 'File', 'Wikipedia:', 'Main_Page', 'Help:', '#', 'United_States', 'Overweight', 'Talk:']
    
    if word_counts <= 5:
        for search_item in standards_nouns:
            inital_search = wikipedia.search(str(search_item))
            try:
                wikipage = wikipedia.page(str(inital_search[0]))
                wiki_image = wikipage.images[0]
            except:
                wiki_image = None

            if inital_search:
                result = inital_search[0], wiki_image
                if result not in wiki_initial:
                    wiki_initial.append(result)

        for search_item, image in wiki_initial:
            wiki_search = wiki_wiki.page(str(search_item))
            
            if wiki_search.exists():
                r_search = wiki_search.fullurl
                wiki_t = r_search, search_item.title(), image

                w_summary = get_wiki_term_summary(search_item.title(), wiki_search)
                sim_score = check_topic_relevance(w_summary, lesson_id)
                results = search_item.title(), w_summary, sim_score, None
                if results not in final_terms:
                    final_terms.append(results)
                if wiki_t not in wiki_titles:
                    wiki_titles.append(wiki_t)

    

    wiki_count = 0
    
    for wiki_title in wiki_titles:

        matched_topic = topicInformation.objects.filter(item=wiki_title[1]).first()
        
        if matched_topic:
            if wiki_title[2]:
                matched_topic.image_url = wiki_title[2]
                matched_topic.save()
            lesson_match = lessonObjective.objects.filter(id=lesson_id, objectives_topics=matched_topic)

            if lesson_match:
                link_list = []
                
                check_textbook = textBookTitle.objects.filter(title=wiki_title[0], prim_topic_id=matched_topic.id).first()
                if check_textbook:
                    textbook_match, created = check_textbook, False
                else:
                    textbook_match, created = textBookTitle.objects.get_or_create(title=wiki_title[0], prim_topic_id=matched_topic.id)
 
                if created:
                    #gets main item summary 
                    term = wiki_title[1]
                    wiki_count = wiki_count + 1
                    res = requests.get(wiki_title[0])
                    soup = BeautifulSoup(res.text, "html.parser")
                    full_text = soup.text
                    full_summary = text_summary_nltk(full_text, term, 7)

                    if soup:
                        for link in soup.find_all("a"):
                            term = link.string
                            
                            url = link.get("href", "")
                            if 'wiki' in url:
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
                        line_counter = str(textbook_match.id) + '0000' + '1'
                        line_counter = int(line_counter)
                        for line in fresults:
                            
                            line_counter = line_counter + 1
                            
                            a_string = line.rstrip("\n")
                            final_line = re.sub(r'\[.*\]', '', a_string)
                            

                            if 'ISBN' not in final_line:
                                for word in link_list:
                                    if word[0] is not None:
                                        if len(word[0]) >= 4:
                                            if word[0] in final_line:
                                                if "^" not in final_line:
                                                    wiki_text = word[0], final_line
                                                    if len(final_line) <= 999:
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
                    
                    
                    for word in word_full:
                      
                        if word_counts <= 3:
                            textline_matches = textBookBackground.objects.filter(textbook=textbook_match, header=word.header)
                            line_wording = []
                            for line in textline_matches:
                                desc = line.line_text
                                line_wording.append(desc)
                            line_wording = '; '.join(line_wording)

                            if word.term_created == False:
                                wiki_search = wiki_wiki.page(str(word.header))
                                if wiki_search.exists():
                                    r_search = wiki_search.fullurl
                                    
                                    secondary_term  = get_wiki_term_summary(word.header, wiki_search)
                                    combined_wording = str(line_wording) + '; ' + str(secondary_term)

                                    test_summary = text_summary_nltk(combined_wording, wiki_search, 3)

                                    if len(test_summary) > 4:
                                        sim_score = check_topic_relevance(test_summary, lesson_id)
                                     
                                        if sim_score >= .10:
                                            
                                            results = word.header, test_summary, sim_score, matched_topic.id
                                            word_counts = word_counts + 1
                                            word.term_created == True 
                                            word.save()
                                            if results not in final_terms:
                                                final_terms.append(results)
                                    else:
                                        if len(secondary_term) > 4:
                                            sim_score = check_topic_relevance(secondary_term, lesson_id)
                                          
                                            if sim_score >= .10:
                                                results = word.header, secondary_term, sim_score, matched_topic.id
                                                word_counts = word_counts + 1
                                                word.term_created == True 
                                                word.save()
                                                if results not in final_terms:
                                                    final_terms.append(results)
               
 
    return(final_terms)
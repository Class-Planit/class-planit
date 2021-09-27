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
from bs4.element import Comment
from .activity_builder import *
Language.factories['tok2vec']

stop_words = [ 'Bloom', 'Diff', 'Differentiation', 'Depth', 'Retention', 'Rate', 'Worksheet', 'Digital', 'i', "'", "'" '!', '.', ':', ',', '[', ']', '(', ')', '?', "'see", "see", 'x', '...',  'student', 'learn', 'objective', 'students', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"]

TAG_RE = re.compile(r'<[^>]+>')

def get_api_standard_matches(overview, grade, subject):
    standards_match = singleStandard.objects.filter()
    prediction = []
    for standard_id, standard_full in standards:
        Document1 = standard_full
        
        Document2 = ' '.join([str(i) for i in tokens_without_sw]) 
        corpus = [Document1,Document2]

        X_train_counts = count_vect.fit_transform(corpus)
        vectorizer = TfidfVectorizer()
        trsfm=vectorizer.fit_transform(corpus)
        result = cosine_similarity(trsfm[0:1], trsfm)
        result = result[0][1]
        total = standard_id, result
        
        if result >= .15:
            
            prediction.append(total)


    if prediction:
        prediction.sort(key=lambda x: x[1], reverse=True)
        full_result = []
        for item in prediction[:3]:
            full_result.append(item[0])
    else:
        full_result = []

    return(full_result)


def check_objective(t_results):
    objectives = []
    for line in t_results:
        objective_titles = ['Objective', 'Objectives', 'Standards', ]
        if 'Objective' in line:
             objectives.append(line)
    return(objectives)   

def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

def get_important_topics(teacher_input_nouns):
    pass





def get_api_sentence_nouns(match_textlines):
    full_sent_list = []
    
    results = tokenize.sent_tokenize(match_textlines)

    for sent in results:
        new_list = []
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
            else:
                pass

            remove_list = ['illustrations', 'cartoon', 'Education.com']
            results = []
            if is_noun and is_long:

                sent = re.sub(r'\(.*\)', '', sent)
                sent = re.sub('Chapter', '', sent)
                sent = re.sub('Rule Britannia!', '', sent)
                sent = re.sub('Description', '', sent)
                if any(word in sent for word in remove_list):
                    pass
                else:
                    sent_index = sent_tagger.index(y)
                    
                    if y[0] not in stop_words:
                        final_r = y[0], y[1], sent_index
                        new_list.append(final_r)
        full_sent_list.append(new_list)    

    final_list = []
    for line in full_sent_list:
        for item in line:
 
            first_word = item[0]
            word_index = item[2]
            next_index = word_index + 1
            next_next_word = word_index + 2
            for fsl_item in line:
                if fsl_item[2] == next_index:
                    try:
                        second_word = fsl_item[0]

                        combine_wording = first_word + ' ' + second_word
                        for x_fsl_item in line:
                            try:
                                if x_fsl_item[2] == next_next_word:
                                    third_word = x_fsl_item[0]
                                    combine_wording = combine_wording + ' ' + third_word
                            except:
                                pass
                    except:
                        pass

                    if  combine_wording: 
                        if combine_wording not in final_list:
                            final_list.append(combine_wording)
    
    if final_list:
        pass
    else:
        for line in full_sent_list:
            for item in line:
                first_word = item[0]
                for word in match_textlines.split():

                    if first_word.lower() == word.lower():
                        if first_word not in final_list:
                            final_list.append(first_word)


    print('==============')
    print(final_list)
    print('==============')
    return(final_list)



def generate_api_term_recs(teacher_input):

    new_list = []
    final_list = []
    for line in teacher_input:
        standards_nouns = get_api_sentence_nouns(line)
        Document1 = ' '.join(standards_nouns)
        Document2 = ' '.join(teacher_input)

        corpus = [Document1,Document2]

        X_train_counts = count_vect.fit_transform(corpus)
        vectorizer = TfidfVectorizer()
        trsfm=vectorizer.fit_transform(corpus)
        result = cosine_similarity(trsfm[0:1], trsfm)
        result = standards_nouns, result[0][1]
        if result[1] > .06:
            for word in standards_nouns:
                final = word, result[1]
                if final not in new_list: 
                    new_list.append(final)

    new_list.sort(key=lambda x: x[1], reverse=True)

    wiki_initial = []
    for search_item in new_list[:20]:
        inital_search = wikipedia.search(str(search_item[0]))

        for i_search in inital_search[:3]:
            if i_search not in wiki_initial:
                remove_list = ['List of', 'Names of', 'Flags of', 'Glossary of']
                if any(word in i_search for word in remove_list):
                    pass
                else:
                    wiki_initial.append(i_search)

    for line in wiki_initial:
        Document1 = line
        Document2 = ' '.join([str(i) for i in teacher_input])
        corpus = [Document1,Document2]

        X_train_counts = count_vect.fit_transform(corpus)
        vectorizer = TfidfVectorizer()
        trsfm=vectorizer.fit_transform(corpus)
        result = cosine_similarity(trsfm[0:1], trsfm)
        result = line, result[0][1]

        if result[1] > .009:
            if line not in final_list: 
                final_list.append(line)               

    append_list = []
    for line in final_list:
        result = '<a class="btn btn-sm btn-outline-success selecttopic" lessonid=href="#" >'\
                + line + '</a>'
        append_list.append(result)

    return(append_list)    

def analyze_data(overview):
    soup = BeautifulSoup(overview)

    #[s.extract() for s in soup(['style', 'script', '[document]', 'head', 'title'])]
    mydivs = soup.findAll('span', attrs={"class":"kix-wordhtmlgenerator-word-node"})
    #new_lesson = lessonObjective.objects.get_or_create(user_id)
    t_results = []
    if mydivs:
        
        for d in mydivs:
            print(d)
            text_results = d.getText()
            glines = text_results.strip() 
            glines = glines.replace('\u200c', '')
            glines = glines.replace('\xa0', '')
            
            t_results.append(glines)
    elif soup.findAll('section', attrs={"class":"content-detail-info"}):
        mydivs = soup.findAll('section', attrs={"class":"content-detail-info"})
        for d in mydivs:
            text_results = d.getText()
            t_results.append(text_results)

    else:
        texts = soup.findAll(text=True)
        visible_texts = filter(tag_visible, texts)  
        for item in visible_texts:
            if len(item) >= 50:
                item = item.replace('\n', ' ')
                t_results.append(item)

    
    objective_check  = generate_api_term_recs(t_results)
    
    return(objective_check)
    #activity_check  = check_activity(visible_text)
    #key_term_check  = check_key_term(visible_text)
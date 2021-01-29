from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from django.db.models import Q, Sum
import pandas as pd 
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

import requests
from decouple import config, Csv
from rake_nltk import Rake
import re
from collections import Counter
#test comment 
from urllib.parse import urlparse

wikipedia.set_rate_limiting(True)
count_vect = CountVectorizer()
from nltk.corpus import stopwords
stop_words = stopwords.words('english')

stop_words.extend(['The', 'students', 'learn'])

stop_words = ['i', 'student', 'learn', 'objective', 'students', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"]


def stemSentence(sentence):
    token_words=word_tokenize(sentence)
    token_words
    stem_sentence=[]
    for word in token_words:
        stem_sentence.append(porter.stem(word))
        stem_sentence.append(" ")
    return "".join(stem_sentence)

def match_standard(teacher_input, subject, class_id):
        classroom_profile = classroom.objects.get(id=class_id)
        grade_list = classroom_profile.grade_level.all()
        standard_set = classroom_profile.standards_set
        grade_standards = []
        for grade in grade_list:
                obj = singleStandard.objects.filter(subject=subject, standards_set=standard_set, grade_level=grade)
                objectives_list = []
                for standard in obj:
                        objective = standard.standard_objective,  standard.competency
                        result = standard.id, objective
                        objectives_list.append(result) 

                prediction = []
                for standard_full in objectives_list:
                        
                        standard_full_joined = ' '.join([str(i) for i in standard_full[1] if not i in stopwords.words()])
                        text_tokens = word_tokenize(teacher_input)
                        tokens_without_sw = [word for word in text_tokens if not word in stopwords.words()]
                        Document1 = ' '.join([str(i) for i in tokens_without_sw])
                        
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
                        results = grade, prediction[:3]
                        grade_standards.append(results)

        return(grade_standards)


def get_vocab_context(word):
        item = str(word), 
        for word in item:
                try:
                        pos = nltk.pos_tag(word_tokenize(word))
                        syns = wordnet.synsets(word)
                        definition = syns[0].definition()       
                        sentence = syns[0].examples()
                        if syns:
                                return(word, definition, sentence, pos)
                     
                       
                except:
                        pass


def get_context_text(text):
        result = wikipedia.search(text)
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



def modify(inputStr):

        tokens = nltk.WordPunctTokenizer().tokenize(inputStr)
        tagged = nltk.pos_tag(tokens)
        auxiliary_verbs = [i for i, w in enumerate(tagged) if w[1] == 'VBP']
        if auxiliary_verbs:
                tagged.insert(0, tagged.pop(auxiliary_verbs[0]))
        else:
                tagged.insert(0, ('did', 'VBD'))
        tagged.insert(0, ('When', 'WRB'))

        return ' '.join([t[0] for t in tagged])

def check_topic_relevance(text, lesson_id):

        class_objectives = lessonObjective.objects.get(id=lesson_id)
        class_objectives_list = str(class_objectives.teacher_objective)


        topics = googleSearchResult.objects.filter(lesson_plan=lesson_id, is_selected=True)
        topic_results = []
        if topics: 
                for item in topics:
                        full_results = item.snippet
                        topic_results.append(full_results)

        
        questions = googleRelatedQuestions.objects.filter(lesson_plan=lesson_id, is_selected=True)
        question_results = []
        if questions: 
                for item in questions:
                        result = item.question
                        question_results.append(result)

        wiki = wikiTopic.objects.filter(lesson_plan=lesson_id, is_selected=True)
    
        wiki_results = []
        
        if wiki: 
                for item in wiki:
                        text = item.topic
                        wiki_results.append(text)
                             

        
        class_topics = ' '.join([str(i) for i in topic_results])
        related_questions = ' '.join([str(i) for i in question_results])
        related_wiki = ' '.join([str(i) for i in wiki_results])

        combined = class_objectives_list + str(class_topics) + str(related_questions) + str(related_wiki)

        planned_objective = str(combined)
        planned_objective = ''.join([str(i) for i in planned_objective])
        Document1 = planned_objective
        Document2 = text
        corpus = [Document1,Document2]
        X_train_counts = count_vect.fit_transform(corpus)
        vectorizer = TfidfVectorizer()
        trsfm=vectorizer.fit_transform(corpus)
        result = cosine_similarity(trsfm[0:1], trsfm)
        result = result[0][1]
        return(result)

def youtube_results(text, lesson_id):
        class_objectives = lessonObjective.objects.get(id=lesson_id)
        class_objectives_list = str(class_objectives.teacher_objective)
        topics = class_objectives.objectives_topics.all()
        topic_list = []
        for item in topics:
                title = item.item
                topic_list.append(title)
       
        class_topics = ' '.join([str(i) for i in topic_list])


        combined = class_objectives_list + class_topics

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


def wiki_google_results(text, lesson_id):
        class_objectives = lessonObjective.objects.get(id=lesson_id)
        class_objectives_list = str(class_objectives.teacher_objective)
        objective_topic = get_keywords(class_objectives_list)
        
        topic_matches = class_objectives.objectives_topics.all()
        topics = topicInformation.objects.filter(id__in=topic_matches)
        search_sentences = []
        for topic in topics:
                term = topic.item
                description = topic.description
                subject = str(topic.subject)
                grade = str(topic.grade_level)
                search_sentence = term
                search_sentences.append(search_sentence)
        for item in objective_topic:
                search_sentence = item
                search_sentences.append(search_sentence) 

        for sentence in search_sentences:
                
                params = {
                'engine': "google",
                'q': sentence,
                'api_key': config('api_key')
                }

                client = GoogleSearch(params)
                results = client.get_json()

                try:
                        search_results = results['organic_results']
                except:
                        search_results = []

                try:
                        related_results = results["related_questions"]
                except:
                        related_results = []

                if search_results:
                        for item in search_results[:3]:
                                title = item['title']
                                link = item['link']
                                snippet = item['snippet']
                                new_result, created = googleSearchResult.objects.get_or_create(lesson_plan=class_objectives , title=title, link=link, snippet=snippet)

                if related_results:
                        for item in related_results[:3]:
                                question = item['question']
                                link = item['link']
                                snippet = item['snippet']
                                new_result, created = googleRelatedQuestions.objects.get_or_create(lesson_plan=class_objectives , question=question, link=link, snippet=snippet)


                result_list = list(chain(related_results, search_results))
                
                summary_list = []
                for item in result_list:
                        summary = item['snippet']
                        summary_list.append(summary)

                result_text = ' '.join(summary_list)
                keyword_results = get_keywords(result_text)
                

                try:
                        wiki_search = wikipedia.search(sentence)
                       

                        try:
                                topic_result = wikipedia.summary(wiki_search[0], sentences = 3, auto_suggest=False, redirect=True)
                                
                                result = check_topic_relevance(topic_result, lesson_id)
                                if result >= .10:
                                        
                                        new_wiki, created = wikiTopic.objects.get_or_create(lesson_plan=class_objectives , term=wiki_search[0], topic=topic_result, relevance=result)
        
                        except wikipedia.DisambiguationError as e:
                                pass

                
                except:
                        pass
                        
        return('Success')

def get_website_info(item_id):
        topic = googleSearchResult.objects.get(id=item_id)
        url = topic.link
        result = requests.get(url)
        soup = bs4.BeautifulSoup(result.text)
        paragraph = []
        for tag in soup.select('li'):
                p = tag.text.strip()
                paragraph.append(p)

        return(paragraph)

def split_sentence(sentence):
    return list(filter(lambda x: len(x) > 0, re.split('\W+', sentence.lower())))

def generate_vocabulary(train_captions, min_threshold):
    """
    Return {token: index} for all train tokens (words) that occur min_threshold times or more, 
        `index` should be from 0 to N, where N is a number of unique tokens in the resulting dictionary.
    """  
    #divide the string tokens (individual words), by calling the split_sentence function 
    individual_words = split_sentence(train_captions)
    #create a list of words that happen min_threshold times or more in that string  
    condition_keys = sorted([key for key, value in Counter(individual_words).items() if value >= min_threshold])
    #generate the vocabulary(dictionary)
    result = dict(zip(condition_keys, range(len(condition_keys))))
    return result



def get_wiki_lesson_keywords(lesson_id):
       
        class_objectives = lessonObjective.objects.get(id=lesson_id)
        
        
        subject = class_objectives.subject
        class_match = class_objectives.lesson_classroom_id
        classroom_match = classroom.objects.get(id=class_match)
        grade_levels = classroom_match.grade_level.all()
        grade_matches = gradeLevel.objects.filter(id__in=grade_levels)
        standard_match = classroom_match.standards_set_id
        class_objectives_list = str(class_objectives.teacher_objective)

        
        wiki = wikiTopic.objects.filter(lesson_plan=lesson_id, is_selected=True).first()
      
        if wiki:
                item = wiki.term           
        else:
                item =  class_objectives.objective_title    

        wiki_full = []
        try:
                topic_result = wikipedia.summary(item, sentences = 10, auto_suggest=False, redirect=True)
                wiki_page = wikipedia.WikipediaPage(title = item[0])
                results = topic_result
                wiki_full.append(results)

                
        except wikipedia.DisambiguationError as e:
                pass

        


        
        wiki_full = ''.join([str(i) for i in wiki_full]).lower()

        keyword_results = get_keywords(wiki_full)
        
        filtered_list = []
        for word in keyword_results:
                if word.lower() not in stop_words:
                        filtered_list.append(word) 
                
           
        wiki_sent = tokenize.sent_tokenize(wiki_full)
        topic_keywords = []  
        for word in filtered_list:
                if len(word) >= 3:
                        for item in wiki_sent:
                                item = ''.join([str(i) for i in item])
                                item = item.replace("\n", " ") 
                                item = item.replace("=", " ") 
                               
                                if word in item:
                                        
                                        result = word, item.capitalize()
                                        
                                        if result in topic_keywords:
                                                pass
                                        else:
                                                topic_keywords.append(result)

       
        for topic in topic_keywords:
                result = check_topic_relevance(topic[1], lesson_id)
                if result >= .15:
                        topic_title = topic[0].title()
                        new_topic_description, created = topicDescription.objects.get_or_create(description=topic[1])

                        for grade in grade_matches:
                                topic_match = topicTypes.objects.get(item='key_term ')
                                new_topic, created = topicInformation.objects.get_or_create(subject=subject, grade_level=grade, standard_set_id=standard_match, topic=topic_title, item=topic_title, image_name='None')
                                
                                add_topic = new_topic.description.add(new_topic_description)
                                        
                        
                                
                                add_topic = new_topic.topic_type.add(topic_match)
        




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
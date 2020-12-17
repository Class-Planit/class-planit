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
import wikipedia
from youtube_search import YoutubeSearch
nltk.download('stopwords')
nltk.download('wordnet')
import bs4
import requests
from decouple import config, Csv
from rake_nltk import Rake
#test comment 

count_vect = CountVectorizer()




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


        topics = googleSearchResult.objects.filter(lesson_plan=lesson_id)
        topic_results = []
        if topics: 
                for item in topics:
                        result = item.snippet
                        topic_results.append(result)

        questions = googleRelatedQuestions.objects.filter(lesson_plan=lesson_id)
        question_results = []
        if questions: 
                for item in questions:
                        result = item.question
                        question_results.append(result)



        class_topics = ' '.join([str(i) for i in topic_results])
        related_questions = ' '.join([str(i) for i in question_results])

        combined = class_objectives_list + str(topic_results) + str(question_results)
        
        text = ''.join([str(i) for i in text])
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



def google_results(text, lesson_id):
        class_objectives = ' '.join([str(i) for i in lessonObjective.objects.get(id=lesson_id)])

        class_topics = ' '.join([str(i) for i in googleSearchResult.objects.filter(lesson_plan=lesson_id)])
        related_questions = ' '.join([str(i) for i in googleRelatedQuestions.objects.filter(lesson_plan=lesson_id)])

        combined = class_objectives + class_topics + related_questions
        params = {
        'engine': "google",
        'q': combined,
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
                for item in search_results[:10]:
                        title = item['title']
                        link = item['link']
                        snippet = item['snippet']
                        new_result, created = googleSearchResult.objects.get_or_create(lesson_plan=class_objectives , title=title, link=link, snippet=snippet)

        if related_results:
                for item in related_results[:10]:
                        question = item['question']
                        link = item['link']
                        snippet = item['snippet']
                        new_result, created = googleRelatedQuestions.objects.get_or_create(lesson_plan=class_objectives , question=question, link=link, snippet=snippet)



        return('Success')



def wiki_google_results(text, lesson_id):
        class_objectives = lessonObjective.objects.get(id=lesson_id)
        class_objectives_list = str(class_objectives.teacher_objective)


        topics = googleSearchResult.objects.filter(lesson_plan=lesson_id)
        topic_results = []
        if topics: 
                for item in topics:
                        result = item.snippet
                        topic_results.append(result)

        questions = googleRelatedQuestions.objects.filter(lesson_plan=lesson_id)
        question_results = []
        if questions: 
                for item in questions:
                        result = item.question
                        question_results.append(result)



        class_topics = ' '.join([str(i) for i in topic_results])
        related_questions = ' '.join([str(i) for i in question_results])

        combined = class_objectives_list + str(topic_results) + str(question_results)
        params = {
        'engine': "google",
        'q': combined,
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
                for item in search_results[:10]:
                        title = item['title']
                        link = item['link']
                        snippet = item['snippet']
                        new_result, created = googleSearchResult.objects.get_or_create(lesson_plan=class_objectives , title=title, link=link, snippet=snippet)

        if related_results:
                for item in related_results[:10]:
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

        for item in keyword_results:
                keyword_results_num = check_topic_relevance(item, lesson_id)
                
                if keyword_results_num >= .20:
                      
                        try:
                                wiki_search = wikipedia.search(item)
                              
                                
                                for item in wiki_search:
                                        try:
                                                topic_result = wikipedia.summary(item, sentences = 3, auto_suggest=False, redirect=True)
                                                
                                                result = check_topic_relevance(topic_result, lesson_id)
                                        
                                                if result >= .15:
                                                        new_result = result * 100 
                                                        
                                                        new_wiki, created = wikiTopic.objects.get_or_create(lesson_plan=class_objectives , topic=topic_result, relevance=new_result)
                         
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


def get_lesson_keywords(lesson_id):
        class_objectives = lessonObjective.objects.get(id=lesson_id)
        class_objectives_list = str(class_objectives.teacher_objective)


        topics = googleSearchResult.objects.filter(lesson_plan=lesson_id, is_selected=True)
        topic_results = []
        if topics: 
                for item in topics:
                        full_results = get_website_info(item.id)
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
                        wiki_search = wikipedia.summary(item, sentences = 10, auto_suggest=False, redirect=True)
                        question_results.append(wiki_search)

        class_topics = ' '.join([str(i) for i in topic_results])
        related_questions = ' '.join([str(i) for i in question_results])

        combined = class_objectives_list + str(class_topics) + str(related_questions) + str(wiki_results)
        
        keyword_results = get_keywords(combined)


        topic_keywords = []    
     
        for item in keyword_results:

                 
                keyword_results_num = check_topic_relevance(item, lesson_id)
              
                if keyword_results_num >= .05:
              
                        definitions = get_vocab_context(item)  
                    
                        if definitions:     
                                new_keyword, created = keywordResults.objects.get_or_create(lesson_plan=class_objectives, word=item, definition=definitions[1], sentence=definitions[2], p_o_s=definitions[3], relevance=keyword_results_num )
                        else:
                                new_keyword, created = keywordResults.objects.get_or_create(lesson_plan=class_objectives, word=item, relevance=keyword_results_num )
        return('success')



def get_questions(lesson_id):
        class_objectives = lessonObjective.objects.get(id=lesson_id)
        lesson_match = lessonFull.objects.filter(lesson_overview=class_objectives).first()
        

        text = str(class_objectives.teacher_objective)
        google_result = google_results(text, lesson_id)
        g_summary = []
        youtube_result = []
        for term in google_result:
                if 'YouTube' in term:
                        result = YoutubeSearch(term, max_results=4).to_dict()
                        for item in result:
                                results = item['id']
                                youtube_result.append(results)
                else:
                        g_summary.append(term) 

        keyword_one = get_keywords(text)
        

        keyword_context = []
        for keyword in keyword_one:
                item = get_context_text(keyword)
                result = check_topic_relevance(item, lesson_id)
                
                if result >= .20:
                        topic_summary = []
                        for topic in item[:5]:
                                try:
                                        topic_result = wikipedia.summary(topic, sentences = 5, auto_suggest=False, redirect=True)
                                        result = check_topic_relevance(topic_result, lesson_id)
                                
                                        if result >= .45:
                                                
                                        
                                                keyword_two = get_keywords(topic_result)
                                                
                                                result = keyword_two
                                                topic_summary.append(result)
                                except wikipedia.DisambiguationError as e:
                                        pass

                        if topic_summary in keyword_context:
                                pass
                        else:                
                                result = topic_summary
                                keyword_context.append(result)
        
        definitions = []
        for word_list in keyword_context: 
                for item_list in word_list:
                        for word in item_list:
                                definition = get_vocab_context(word)
                                if definition:
                                        definitions.append(definition)

        return(g_summary, keyword_context, definitions, youtube_result)


                                        
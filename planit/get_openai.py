import os
import openai
from decouple import config, Csv
from .models import *
import json
import requests
import re

openai.api_key = config('OPENAI_API_KEY') 

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


def openai_term_labels(user_id, topic_term, subject, grade):
    subject = 'english'
    grade = 'eight'
    path3 = f'planit/files/{subject}/{grade}/examples.csv'

    description = get_description_string(topic_term.id, user_id)
    wording = f'term: {topic_term.item} description: {description}'
    #this is for the mi and blooms level assignment
    
    with open(path3) as f:
        examples = []
        labels = []
        for line in f:
            line = line.split(',')
            example_wording = [line[0], line[1]]
            examples.append(example_wording)
            labels.append(line[1])

        response = openai.Classification.create(
                    search_model="ada", 
                    model="curie",
                    examples=examples,
                    query=wording,
                    labels=labels)

    
    return(response['label'].upper())


   



def activity_score(sentence):
    pass

def get_single_types_activity(topic_list):
    word_list = []
    for topic in topic_list:
        
        word = topic.item
        topic_types = topic.topic_type.all()
        t_matches = topicTypes.objects.filter(id__in=topic_types)
        for tt in t_matches:
            topic_t = tt.item
            all_templates = LearningDemonstrationTemplate.objects.filter(topic_type=tt)
            for temp in all_templates:
                result =  temp.content
                sentence  = result.replace(topic_t, word)
                result = sentence, word, topic_t, 'single'
                word_list.append(result)


    return(word_list)


def get_activity_mask(topic_list):
    pass
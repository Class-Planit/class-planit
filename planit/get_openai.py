import os
import openai
from decouple import config, Csv
from .models import *
import json
import requests
import re

openai.api_key = config('OPENAI_API_KEY') 

def get_desciption_summary(item, full_desc):
    full_sentence = f'term: {item} description: {full_desc}'
    if len(full_sentence)  > 4:
        response = openai.Completion.create(
                    engine="curie",
                    prompt=full_sentence,
                    temperature=0.3,
                    max_tokens=80,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0,
                    stop=["\n"]
                    )
        results = response['choices'][0]

        return(results['text'])

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
    print('Starting')
    admin_subjects = ['Physical Education', 'Health Education', 'Spanish Language', 'Science', 'Social Studies', 'Mathematics', 'English', 'Venture']
    if subject in admin_subjects:
        path3 = f'planit/files/{subject}/{grade}/examples.csv'
    else:
        path3 = f'planit/files/default/{grade}/examples.csv'

    description = get_description_string(topic_term.id, user_id)
    wording = f'term: {topic_term.item} description: {description}'
    #this is for the mi and blooms level assignment

    try:
        with open(path3) as f:

            examples = []
            labels = []
            for line in f:
                line = line.split(',')
                
                example_wording = [line[0], line[1]]
                examples.append(example_wording)
                labels.append(line[1])

            print('##########')
            print(examples)
            print('##########')

            response = openai.Classification.create(
                        search_model="ada", 
                        model="curie",
                        examples=examples,
                        query=wording,
                        labels=labels)
    except:
        path = f'planit/files/default/Eight/examples.csv'
        with open(path) as f:

            examples = []
            labels = []
            for line in f:
                line = line.split(',')

                example_wording = [line[0], line[1]]
                examples.append(example_wording)
                labels.append(line[1])

            print('##########')
            print(examples)
            print('##########')
            response = openai.Classification.create(
                        search_model="ada", 
                        model="curie",
                        examples=examples,
                        query=wording,
                        labels=labels)



    print('Ending')
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
                print(result)
                word_list.append(result)


    return(word_list)


def get_activity_mask(topic_list):
    pass
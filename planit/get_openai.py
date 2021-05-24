import os
import openai
from decouple import config, Csv
from .models import *

import pandas as pd
import re

openai.api_key = config('OPENAI_API_KEY') 


def get_description_string(desc_list, user_id):
    pass  

def openai_tes(user_id, topic_term, matched_topics):
    pass



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
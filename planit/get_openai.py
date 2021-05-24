import os
import openai
from decouple import config, Csv
from .models import *
import torch
from pytorch_transformers import GPT2Tokenizer, GPT2LMHeadModel
import pandas as pd
import re

openai.api_key = config('OPENAI_API_KEY') 

model = GPT2LMHeadModel.from_pretrained("gpt2")
model.eval()
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")


def get_description_string(desc_list, user_id):
    pass  

def openai_tes(user_id, topic_term, matched_topics):
    pass



def activity_score(sentence):
    tokenize_input = tokenizer.tokenize(sentence)
    tensor_input = torch.tensor([tokenizer.convert_tokens_to_ids(tokenize_input)])
    loss = model(tensor_input, labels=tensor_input)
    return -loss[0].item()

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
   
    all_templates = lessonTemplates.objects.all()
    candidates = []
    for demos in topic_list:
        wording = demos.item
        candidates.append(wording)

    for sentc in all_templates:
        final_list = []
        sent_one = sentc.wording
        sent_template = sent_one.replace('DEMO_KS', '{}')

        
        for candidate in candidates:
            sent_result = sent_one.replace('DEMO_KS', candidate)
            
            result = activity_score(sent_template.format(candidate)), sent_result, candidate
            
            final_list.append(result)



    
    return(final_list)
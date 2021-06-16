

try:
    from PIL import Image
except ImportError:
    import Image
import os
import requests
from PIL import Image, ImageFile, ImageDraw, ImageChops, ImageFilter, ImageEnhance
from .models import *
from io import BytesIO, StringIO
from urllib.request import FancyURLopener
from urllib.request import urlopen, Request
from django.core.files import File
from django.core.files.images import ImageFile


def find_match_topic_texts(subject, text_id):
    #ensure the matching is subject specific 
    topics = topicInformation.objects.filter(subject = subject)
    titles = textBookTitle.objects.get(id=text_id)
    textlines = textBookBackground.objects.filter(textbook=titles)
    matched_topics = []
    for line in textlines:
        line_id = line.id
        text = line.line_text
        for topic in topics:
            topic_id = topic.id
            word = topic.item 
            if word.lower() in text.lower():
                update_topic = topicInformation.objects.get(id=topic_id)
                matched_topics.append(update_topic)

    return(matched_topics)

def match_topic_texts(subject, text_id):
    #ensure the matching is subject specific 
    topics = topicInformation.objects.filter(subject = subject)
    titles = textBookTitle.objects.get(id=text_id)
    textlines = textBookBackground.objects.filter(textbook=titles)
    for line in textlines:
        line_id = line.id
        text = line.line_text
        for topic in topics:
            topic_id = topic.id
            word = topic.item 
            if word.lower() in text.lower():
                update_topic = topicInformation.objects.get(id=topic_id)
                update_line = textBookBackground.objects.get(id=line_id)
                update_topic.text_index.add(line_id)




def get_pdf_sent(match_textlines):
    full_sent_list = []
    text_list_join = ''.join([str(i) for i in match_textlines])
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
        remove_list = ['illustrations', 'cartoon', 'Figure', 'they', 'those', 'Circle ', 'Education.com']
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
                    full_sent_list.append(sent_tagger)
    
    return(full_sent_list)



from serpapi import GoogleSearch
from .models import *
from decouple import config, Csv

def get_possible_images(topic, topic_id):
    params = {
    "q": topic,
    "tbm": "isch",
    "ijn": "0",
    "api_key": config('api_key')
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    images_results = results['images_results']
    if images_results:
        url = images_results[0]['original']
        topic_match = topicInformation.objects.get(id=topic_id)

        topic_match.image_url = url
        topic_match.save()
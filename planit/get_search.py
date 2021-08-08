from serpapi import GoogleSearch
from decouple import config, Csv


def get_search_images(search_term, search_ref):

    params = {
        "q": search_term,
        "tbm": "isch",
        "ijn": "0",
        'api_key': config('api_key')
        }

    search = GoogleSearch(params)
    results = search.get_dict()
    images_results = results['images_results']

    full_results = []
    for img in images_results[:4]:
        image_r = img['thumbnail']
        title = img['title']
        result = {'title': title, 'image_r': image_r, 'quest_ref': search_ref}
        full_results.append(result)
    

    return(full_results)

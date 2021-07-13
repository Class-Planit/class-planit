def build_wiki_topic_list(topics, lesson_id, user_profile, standards_nouns):
    
    not_selected_topics = []
    if topics:
        
        for top in topics:  
           
            if top.from_wiki:
                
                if top.is_secondary:
                    pass
                else:
                    
                    title = top.item
                    get_full_links = get_wiki_full(title, lesson_id, top.id)
                  
                    if get_full_links:
                        for item in get_full_links: 
                            full_desc = ''.join(item[1])
                            get_desc_summary = get_desciption_summary(item[0], full_desc)
                            match_topic = topicInformation.objects.filter(item=item[0], created_by=user_profile, is_admin=False, from_wiki=True).first()
                            if match_topic:
                                pass
                            else:
                                match_topic, created = topicInformation.objects.get_or_create(item=item[0], created_by=user_profile, is_admin=False, from_wiki=True, is_secondary=True)
                            new_description, created = topicDescription.objects.get_or_create(topic_id=match_topic.id, created_by=user_profile, is_admin=False)
                            new_description.description = get_desc_summary 
                            new_description.save()
                            add_description = match_topic.description.add(new_description)
                            top_id = match_topic.id
                        
                            if top_id not in topic_ids:
                                result = top_id, item[2]
                                if result[0] not in not_selected_topics:
                                    not_selected_topics.append(result)
            else:
                
                wiki_topics = wiki_results(lesson_id, user_profile.id, standards_nouns)
                for item in wiki_topics: 

                    full_desc = ''.join(item[1])
                    get_desc_summary = get_desciption_summary(item[0], full_desc)
                    match_topic = topicInformation.objects.filter(item=item[0], created_by=user_profile, is_admin=False, from_wiki=True).first()
                    if match_topic:
                        pass
                    else:
                        match_topic, created = topicInformation.objects.get_or_create(item=item[0], created_by=user_profile, is_admin=False, from_wiki=True)
                    new_description, created = topicDescription.objects.get_or_create(topic_id=match_topic.id, created_by=user_profile, is_admin=False)
                    new_description.description = get_desc_summary 
                    new_description.save()
                    add_description = match_topic.description.add(new_description)
                    top_id = match_topic.id
                    result = top_id, item[2]
                    if result[0] not in not_selected_topics:
                        not_selected_topics.append(result)

    else:
        
        wiki_topics = wiki_results(lesson_id, user_profile.id, standards_nouns)
        for item in wiki_topics: 
            result = build_term_description(item, description, user_profil, is_wiki)
            full_desc = ''.join(item[1])
            get_desc_summary = get_desciption_summary(item[0], full_desc)
            match_topic = topicInformation.objects.filter(item=item[0], created_by=user_profile, is_admin=False, from_wiki=True).first()
            if match_topic:
                pass
            else:
                match_topic, created = topicInformation.objects.get_or_create(item=item[0], created_by=user_profile, is_admin=False, from_wiki=True)
            new_description, created = topicDescription.objects.get_or_create(topic_id=match_topic.id, created_by=user_profile, is_admin=False)
            new_description.description = get_desc_summary
            new_description.save()
            add_description = match_topic.description.add(new_description)
            top_id = match_topic.id
            result = top_id, item[2]
            if result[0] not in not_selected_topics:
                not_selected_topics.append(result)

    return(not_selected_topics)




########################


wiki_titles = []

    for search in standards_nouns:
        wiki_search = wikipedia.search(search)
        for r_search in wiki_search:
           
            if r_search not in wiki_titles:
                wiki_titles.append(r_search)


    wiki_list = []    
    wiki_count = 0
    for wiki_title in wiki_titles:
        try:
                wiki_url = "https://en.wikipedia.org/wiki/%s" % (wiki_title)
                topic_result = wikipedia.summary(wiki_title, sentences = 3, auto_suggest=False, redirect=True)
                results = tokenize.sent_tokenize(topic_result)
                sent_result = ' '.join(results[:3])
                result = check_topic_relevance(sent_result, lesson_id)
                print('================')
                print(wiki_title, sent_result, result)
                print('================')
                if wiki_count > 5:
                    if result >= .10:
                        term = wiki_title, sent_result, result
                        wiki_count = wiki_count + 1
                        wiki_list.append(term)
                else:
                    term = wiki_title, sent_result, result
                    wiki_count = wiki_count + 1
                    wiki_list.append(term)

        except wikipedia.DisambiguationError as e:
                pass

        

    wiki_list.sort(key=lambda x: x[2], reverse=True) 

    return(wiki_list)
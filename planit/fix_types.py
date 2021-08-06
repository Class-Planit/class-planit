from .models import *



#checks that the topic type is a valid format (only uppercase, no / or spaces)
def check_topic_type(topic):
    if isinstance(topic, str):
        old_topic = topic
    else:
        old_topic = topic.item
        
    #only use the first half of / for correct_topic
    index = old_topic.find("/")
    if index != -1:
        correct_topic = old_topic[0:index]
    else:
        correct_topic = old_topic
    #make all uppercase and remove spaces
    correct_topic = correct_topic.upper()
    correct_topic = correct_topic.replace(" ", "")
    if correct_topic == "KEY_TERM":
        correct_topic = "KT"
    #was the topic corrected?
    if old_topic == correct_topic:
        corrected = False
    else:
        corrected =  True
    results = old_topic, correct_topic, corrected 

    return results


#looks through all Topics and determines if the topic is valid
#update invalid topics and update all demonstrationTemplates with that topic
def fix_incorrect_types():
    #get all Topics in topic_list
    topic_list = topicTypes.objects.filter()


    #for each_topic in topic_list
    for each_topic in topic_list:
        #check that each_topic is valid
        checked = check_topic_type(each_topic)
        corrected_topic = checked[1]
        topic_match, created = topicTypes.objects.get_or_create(item=corrected_topic)

        #if corrected == True:
        if checked[2] == True:
            #demos_list with demonstrationTemplates.filter(topic= each_topic)
            demos_list = LearningDemonstrationTemplate.objects.filter(topic_type= each_topic)
            #for each demo in demos_list:
            for each_demo in demos_list:
                #update the topic type
                each_demo.topic_type.remove(each_topic)
                each_demo.topic_type.add(topic_match)
                #demo.save() so that it saves the changes
                each_demo.save()
    return



from django.test import TestCase

# Create your tests here.
if get_topic_ids:
                result_list = topicInformation.objects.filter(id__in=get_topic_ids)
                obj = sorted(chain(topic_matches, result_list), key=lambda instance: instance.id)
        else:
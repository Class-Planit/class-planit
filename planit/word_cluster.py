import numpy as np
from sklearn.cluster import AffinityPropagation
import distance
from .models import *


def word_clusters(lesson_id):  

    class_objectives = lessonObjective.objects.get(id=lesson_id)
    topic_matches = class_objectives.objectives_topics.all()
    
    topics = topicInformation.objects.filter(id__in=topic_matches)
    results_list = []
    for item in topics: 
        result = item.item
        results_list.append(result)

    topic_list = ' '.join([str(i) for i in results_list]).lower()

    words = topic_list.split(" ") #Replace this line
    words = np.asarray(words) #So that indexing with a list will work
    lev_similarity = -1*np.array([[distance.levenshtein(w1,w2) for w1 in words] for w2 in words])

    affprop = AffinityPropagation(affinity="precomputed", damping=0.5)
    affprop.fit(lev_similarity)
    for cluster_id in np.unique(affprop.labels_):
        exemplar = words[affprop.cluster_centers_indices_[cluster_id]]
        cluster = np.unique(words[np.nonzero(affprop.labels_==cluster_id)])
        cluster_str = ", ".join(cluster)
        print(" - *%s:* %s" % (exemplar, cluster_str))
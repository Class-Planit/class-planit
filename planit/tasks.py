import celery
from decouple import config
from celery import shared_task
from celery_progress.backend import ProgressRecorder
from .models import *
from datetime import date
from datetime import datetime
from time import sleep 

from django.db.models import Avg


app = celery.Celery('base')
app.conf.update(BROKER_URL=config('REDIS_URL'),
                CELERY_RESULT_BACKEND=config('REDIS_URL'))

@shared_task(bind=True)
def upload_standards(self):
    
    path3 = 'Planit/files/teks_final.csv'
    with open(path3) as f:
        for line in f:
            line = line.split(',') 
            standard_set = line[0]
            grade_level = line[1]
            subject = line[2]
            skill_topic = line[3]
            standard_objective = line[4]
            competency = line[5]

            new_standard_set, i = standardSet.objects.get_or_create(Location=standard_set)
            new_grade, i = gradeLevel.objects.get_or_create(grade=grade_level , grade_labels=grade_level , standards_set=new_standard_set)
            new_subject, i = standardSubjects.objects.get_or_create(subject_title=subject, standards_set=new_standard_set, is_admin=True)
            add_grade_subject = new_subject.grade_level.add(new_grade)

            obj, created = singleStandard.objects.get_or_create(standards_set=new_standard_set, subject=new_subject, grade_level=new_grade, skill_topic=skill_topic, standard_objective=standard_objective, competency=competency)

@shared_task(bind=True)
def activity_builder(self, teacher_input, class_id, lesson_id, user_id):
 
    classroom_profile = classroom.objects.get(id=class_id)
    
    grade_list = classroom_profile.grade_level.all()
    standard_set = classroom_profile.standards_set
    
    class_objectives = lessonObjective.objects.get(id=lesson_id)
    create_topic_matches, created = matchedTopics.objects.get_or_create(lesson_overview=class_objectives)
    topic_matches = class_objectives.objectives_topics.all()
    selected_standard = class_objectives.objectives_standards.all()
    topics = topicInformation.objects.filter(id__in=topic_matches)
    demo_ks = class_objectives.objectives_demonstration.all()
    topic_count = topics.count()
    results_list = []
    topic_ids = []
    for item in topics: 
        result = item.item
        item_id = item.id 
        results_list.append(result)
        topic_ids.append(item_id)

    lesson_matches = get_lessons(topics, demo_ks, lesson_id, user_id)
    subject = class_objectives.subject
    grade_standards = []
    teacher_input_full = teacher_input + str(results_list) + str(selected_standard)

    teacher_input_stem = teacher_input_full.lower()
    teacher_input_stem = stemSentence(teacher_input_stem)
    text_tokens = word_tokenize(teacher_input_stem)
    tokens_without_sw = [word for word in text_tokens if not word in stop_words]

    get_objective_matches = get_topic_matches(teacher_input, tokens_without_sw, class_objectives, topic_count, grade_list, subject, standard_set, lesson_id)

    matched_topics = match_objectives(get_objective_matches, tokens_without_sw, topic_ids)

    for item in matched_topics:      
        match_topic = topicInformation.objects.filter(id=item).first()
        update_matches = create_topic_matches.objectives_topics.add(match_topic)


    get_standard = match_standard(teacher_input, standard_set, subject, grade_list)

    matched_standards = get_standard_matches(get_standard, tokens_without_sw)

    
    full_results = {'matched_topics': matched_topics[:10], 'matched_standards': matched_standards, 'lesson_matches': lesson_matches}

    return(full_results)

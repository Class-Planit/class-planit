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

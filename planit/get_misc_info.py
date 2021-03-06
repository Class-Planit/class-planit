import _datetime
from datetime import datetime
from .models import *


def get_active_week(current_week, week_of): 
    if current_week == week_of:
        active_week = current_week
    else:
        try:
            active_week = int(week_of)
        except:
            active_week = current_week
    
    return(active_week)

def get_week_info(week_of): 
    #checks if the week is a current week 
    # returns current week, active week, previous week and next week 
    current_week = date.today().isocalendar()[1] 
    active_week = get_active_week(current_week, week_of)

    previous_week = active_week - 1
    next_week = active_week + 1

    week_info = {'current_week': current_week, 'active_week': active_week, 'previous_week': previous_week, 'next_week': next_week}
    return(week_info)

def get_subject_and_classroom(objective_matches, user_id):
    user_profile = User.objects.get(id=user_id)

    subject_results = []

    #for objective in objective_matches:
    #    subject_match = objective.subject_id
    #    subject_title = objective.subject 
    #    results = subject_match,subject_title
    #    if results not in subject_results:
    #        subject_results.append(results)

    classroom_results = []
    all_classrooms = classroom.objects.filter(main_teacher=user_profile)
    for each_classroom in all_classrooms:
        classroom_match = each_classroom.id
        classroom_title = each_classroom.classroom_title
        results = classroom_match,classroom_title
        if results not in classroom_results:
            classroom_results.append(results)
        class_subjects = each_classroom.subjects.all()
        for each_subject in class_subjects:
            subject_match = each_subject.id
            subject_title = each_subject.subject_title
            results1 = subject_match,subject_title
            if results1 not in subject_results:
                subject_results.append(results1)

    return subject_results, classroom_results

def get_subject_and_classroom_dashboard(objective_matches):
    subject_results = []
    for objective in objective_matches:
        subject_match = objective.subject_id
        subject_title = objective.subject 
        results = subject_match,subject_title
        if results not in subject_results:
            subject_results.append(results)
    classroom_results = []
    for objective in objective_matches:
        classroom_match = objective.lesson_classroom_id
        classroom_title = objective.lesson_classroom
        results = classroom_match,classroom_title
        if results not in classroom_results:
            classroom_results.append(results)
    return subject_results, classroom_results


def get_standard_subjects(standards_set):
    #get all the subjects from a standard
    temp_standard_subjects = ['English', 'Social Studies', 'Algebra']
    return temp_standard_subjects

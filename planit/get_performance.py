from .models import *
from django.db.models import Count
from isoweek import Week
from django.db.models import Avg
import math

def get_weekly_brackets(user_id, week_of_start, week_of_finsih, year):
    user_profile = User.objects.get(id=user_id)
    classroom_profiles = classroom.objects.filter(main_teacher=user_profile)
    assignment_matches = worksheetClassAssignment.objects.filter(week_of__range=[week_of_start, week_of_finsih], assigned_classrooms__in=classroom_profiles).order_by('week_of').values_list('id', flat=True)
 
    week_list = []
    low = []
    mid = []
    high = []
    for week in range(week_of_start, week_of_finsih):
        d = Week(year, week).monday()
        week_l = d.strftime('%m/%d')
        if week_l not in week_list:
            week_list.append(week_l)
        student_high = studentWorksheetAnswerFull.objects.filter(week_of=week, score__range=[67, 101], assignment_num__in=assignment_matches).count()
        student_mid = studentWorksheetAnswerFull.objects.filter(week_of=week, score__range=[33, 67], assignment_num__in=assignment_matches).count()
        student_low = studentWorksheetAnswerFull.objects.filter(week_of=week, score__range=[0, 33], assignment_num__in=assignment_matches).count()
        low.append(student_low)
        mid.append(student_mid)
        high.append(student_high)
    week_list.reverse()
    low.reverse()
    mid.reverse()
    high.reverse()
    result = {'weeks': week_list, 'low': low, 'mid': mid, 'high': high}
    return(result)



def get_demo_ks_brackets(user_id, week_of_start, week_of_finsih, year):
    user_profile = User.objects.get(id=user_id)
    classroom_profiles = classroom.objects.filter(main_teacher=user_profile)
    lesson_matches = lessonObjective.objects.filter(lesson_classroom__in=classroom_profiles, week_of__range=[week_of_start, week_of_finsih])
    
    lesson_scores = []
    for lesson in lesson_matches:
        assignment_matches = worksheetClassAssignment.objects.filter(lesson_overview=lesson).values_list('id', flat=True)
        title = '%s %s week of %s' % (lesson.lesson_classroom, lesson.subject, lesson.week_of)
        student_all = studentWorksheetAnswerFull.objects.filter(assignment_num__in=assignment_matches).aggregate(Avg('score'))
        score_avg = student_all['score__avg']
        if score_avg is None:
            score_avg = 0

        result = {'lesson_id': lesson.id, 'title': title, 'avg': score_avg}
        lesson_scores.append(result)

    lesson_scores.sort(key=lambda x: x['avg'], reverse=True)

    return(lesson_scores[:5])


def get_student_praise_count(student_match, start, end, year):
    student_praise = studentPraise.objects.filter(student=student_match, week_of__range=[start, end])
    student_praise_count = studentPraise.objects.values('theme_id').annotate(c=Count('theme_id'))
    return(student_praise_count)

def get_student_trend(all_assignments):
    scores = []
    for item in all_assignments:
        scores.append(item.score)

    trends = [b - a for a, b in zip(scores[::1], scores[1::1])]

    trend = 0
    for result in trends:
        if result > 0:
            trend = trend + 1
        elif result < 0:
            trend = trend - 1
        else:
            pass
    
    return(trend)

def get_student_results(user_id, week_of_start, week_of_finsih, year):
    user_profile = User.objects.get(id=user_id)
    classroom_profiles = classroom.objects.filter(main_teacher=user_profile)
    lesson_matches = lessonObjective.objects.filter(lesson_classroom__in=classroom_profiles, week_of__range=[week_of_start, week_of_finsih])
    
    assignment_matches = worksheetFull.objects.filter(lesson_overview__in=lesson_matches).values_list('id', flat=True)
    total_assignments = worksheetClassAssignment.objects.filter(lesson_overview__in=lesson_matches).count()
    student_all = studentWorksheetAnswerFull.objects.filter(worksheet_assignment__in=assignment_matches)

    student_totals = []
    for student in student_all:

        student_match = User.objects.get(id=student.student_id)
        
        student_name = '%s %s' % (student_match.first_name, student_match.last_name[:1])
        all_assignments = studentWorksheetAnswerFull.objects.filter(student=student_match, worksheet_assignment__in=assignment_matches, is_submitted=True).order_by('completion_date')
        
        if all_assignments:
            student_avg = all_assignments.aggregate(Avg('score'))
            s_avg = math.trunc(student_avg['score__avg'])
            student_complete = all_assignments.count()
        else:
            student_avg = 0
            s_avg = 0
            student_complete = 0
        get_trend = get_student_trend(all_assignments)
        get_praise = get_student_praise_count(student_match, week_of_start, week_of_finsih, year)
    
        result = {'student_id': student_match.id, 'student_name': student_name, 'student_praise': get_praise, 'student_avg': s_avg, 'student_trend': get_trend, 'as_complete': student_complete, 'as_total': total_assignments }
        if result not in student_totals:
            student_totals.append(result)
    
    return(student_totals)
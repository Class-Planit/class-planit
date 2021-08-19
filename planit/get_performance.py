from .models import *
from django.db.models import Count
from isoweek import Week
from django.db.models import Avg
import math

def get_weekly_brackets(user_id, week_of_start, week_of_finsih, year):
    user_profile = User.objects.get(id=user_id)
    classroom_profiles = classroom.objects.filter(main_teacher=user_profile)
    assignment_matches = worksheetClassAssignment.objects.filter(week_of__range=[week_of_start, week_of_finsih], assigned_classrooms__in=classroom_profiles).order_by('week_of').values_list('id', flat=True)

    total_students = 0
    for class_list in classroom_profiles:
        s_count = class_list.student.all()
        student_count = s_count.count()
        total_students = total_students + student_count

    student_answers = studentWorksheetAnswerFull.objects.filter(week_of__range=[week_of_start, week_of_finsih], assignment_num__in=assignment_matches)
    total_answers = student_answers.count()
    completion_rate = 0 
    if total_answers != 0:
        if total_students != 0:
            completion_rate = (total_answers/total_students) * 100 

    performance_average = student_answers.aggregate(Avg('score'))

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
        total_answers = total_answers + student_high + student_mid + student_low
        low.append(student_low)
        mid.append(student_mid)
        high.append(student_high)
    week_list.reverse()
    low.reverse()
    mid.reverse()
    high.reverse()

    
    result = {'weeks': week_list, 'low': low, 'mid': mid, 'high': high, 'performance_average': performance_average, 'completion_rate': completion_rate}
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



def get_worksheet_performance(worksheet):

    worksheet_assignments = worksheetClassAssignment.objects.filter(worksheet_full=worksheet)
    lesson_match = worksheet.lesson_overview_id
    if lesson_match:
        lesson_id = worksheet.lesson_overview_id  
        lesson_full = lessonObjective.objects.get(id=lesson_match)
        classroom_id = lesson_full.lesson_classroom_id
    else:
        lesson_match = 0 
        lesson_id = 0     
        lesson_full = None    
        classroom_id = None
    classroom_assignments = []
    if worksheet_assignments:
        ws_count = worksheet_assignments.count()
       
        for assignment in worksheet_assignments:

            due_date = assignment.due_date
            assigned_classrooms = assignment.assigned_classrooms.all()
            
            for classroom_match in assigned_classrooms:
              
                student_count = 0
                total_score = 0
                submitted_count = 0
                student_classroom_matches = classroom_match.student.all()
                s_count = student_classroom_matches.count()
                student_count = student_count + s_count

                student_answer_matches = assignment.student_answers.all()
                new_student_count = student_answer_matches.count()
                
                s_matches = studentWorksheetAnswerFull.objects.filter(id__in=student_answer_matches, student_profile__in=student_classroom_matches,  is_submitted=True)
                
                new_count = s_matches.count()
                student_count = student_count + new_student_count
                submitted_count = submitted_count + new_count

                for sm in s_matches:
                    s_score = sm.score
                    total_score = total_score + s_score
        
                if student_count != 0:
                    if submitted_count != 0:
                        performance_average = total_score / submitted_count
                        performance_average = int(math.ceil(performance_average))
                        submitted_percent = (submitted_count/student_count) * 100 
                        submitted_percent = int(math.ceil(submitted_percent))
                    else:
                        performance_average = 0 
                        submitted_percent = 0
                else:
                        performance_average = 0 
                        submitted_percent = 0

                assignment_link = "https://www.app1-classplanit.co/student-dashboard/%s/%s/0/" % (lesson_match, worksheet.id)

                assignment_results = {'worksheet_id': worksheet.id, 'lesson_id': lesson_id, 'lesson_match': lesson_full, 'classroom_id': classroom_match.id,  'worksheet_link': assignment_link, 'worksheet': worksheet.title, 'classroom_match': classroom_match, 'due_date': due_date, 'completion': submitted_percent, 'performance': performance_average}
               
                classroom_assignments.append(assignment_results)

    if classroom_assignments:  
        return(classroom_assignments)
    else:
        return(None)
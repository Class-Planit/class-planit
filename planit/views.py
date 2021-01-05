from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View, FormView, TemplateView, DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.edit import FormMixin
from django.template.loader import render_to_string
from django.urls import reverse_lazy
import _datetime
from datetime import datetime
from django.views.generic import TemplateView
from chartjs.views.lines import BaseLineChartView
try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract
from pytesseract import image_to_string
from .forms import *
from .models import *
from .match_standards import *
from .ocr import *
# Create your views here.
# Create your views here.
class Homepage(TemplateView):
    template_name = 'homepage.html' 


class Dashboard(TemplateView):
    template_name = 'dashboard/dashboard.html' 

    def get(self,request,week_of):
        user_profile = User.objects.filter(username=request.user.username).first()
        return render(request, 'dashboard/dashboard.html', {'user_profile': user_profile, 'week_of': week_of})




class Classrooms(TemplateView):
    template_name = 'dashboard/classrooms.html' 

class LessonPlanner(TemplateView):
    template_name = 'dashboard/lesson_planner.html' 

class SubjectPlanner(TemplateView):
    template_name = 'dashboard/subject_planner.html' 


def CreateObjective(request, user_id=None, week_of=None):
    user_profile = User.objects.filter(username=request.user.username).first()
    user_classrooms = classroom.objects.filter(main_teacher=user_profile)

    if 'Current' in week_of:
        current_week = date.today().isocalendar()[1] 
    else:
        current_week = int(week_of)

    if user_classrooms:
        class_subjects = classroomSubjects.objects.filter(subject_classroom__in=user_classrooms)
        subjects = []
        for cs in class_subjects:
          
            subjects_matches = cs.subjects.all()
            for subject_single in subjects_matches:
                subjects_m = standardSubjects.objects.filter(subject_title=subject_single)
                subjects.extend(subjects_m)
    else:
        subjects = []


    if request.method == "POST":
        form = lessonObjectiveForm(request.POST, request.FILES)

        if form.is_valid():
            prev = form.save(commit=False)
            prev.week_of = current_week
            subject = prev.subject_id
            classroom_match = prev.lesson_classroom_id
            prev.save()
           
            return redirect('select_standards', user_id=user_profile.id, class_id=classroom_match, subject=subject, lesson_id=prev.id)
    else:
        form = lessonObjectiveForm()
  

    results = ocr_core('Planit/static/images/image0.jpeg')

    step = 1
    return render(request, 'dashboard/create_objective.html', {'form': form, 'step': step, 'results': results, 'user_profile': user_profile, 'user_classrooms': user_classrooms, 'subjects': subjects  })


def SelectStandards(request, user_id=None, class_id=None, subject=None, lesson_id=None):
    current_week = date.today().isocalendar()[1] 
    user_profile = User.objects.get(id=user_id)

    classroom_profile = classroom.objects.get(id=class_id)
    grade_list = classroom_profile.grade_level.all()

    standard_match = standardSet.objects.get(id=classroom_profile.standards_set_id)
    classroom_subjects = classroomSubjects.objects.filter(subject_classroom=classroom_profile).first()
    subjects_list = classroom_subjects.subjects.all()
    subject_matches = standardSubjects.objects.filter(id__in=classroom_subjects.subjects.all())
    current_subject = standardSubjects.objects.get(id=subject)
    
    class_objectives = lessonObjective.objects.all().order_by('subject')
    
    vocab_list = vocabularyList.objects.filter(lesson_plan__in=class_objectives)
    lesson_activities = lessonFull.objects.filter(lesson_overview__in=class_objectives)
    lesson_match = lessonObjective.objects.get(id=lesson_id)
    current_standards = singleStandard.objects.filter(id__in=lesson_match.objectives_standards.all())
    teacher_objective = lesson_match.teacher_objective
    lesson_standards = singleStandard.objects.filter(id__in=lesson_match.objectives_standards.all())

    recomendations = lessonStandardRecommendation.objects.filter(lesson_classroom=classroom_profile, objectives=lesson_match)
    
    results = match_standard(teacher_objective, current_subject, class_id)
    
    for item in results:
        grade = item[0]
        standards = item[1]
        for standard in standards:
            standard_id = standard[0]
            standard_match = singleStandard.objects.filter(id=standard_id).first()
            create_objective, created = lessonStandardRecommendation.objects.get_or_create(lesson_classroom=classroom_profile, objectives=lesson_match, objectives_standard=standard_match)   

    step = 2
    return render(request, 'dashboard/create_objective.html', {'user_profile': user_profile, 'step': step, 'current_standards': current_standards, 'recomendations': recomendations, 'lesson_match': lesson_match, 'subject_matches': subject_matches, 'lesson_activities': lesson_activities, 'class_objectives': class_objectives, 'vocab_list': vocab_list, 'current_week': current_week, 'subjects_list': subjects_list, 'grade_list': grade_list, 'classroom_profile': classroom_profile, 'classroom_subjects': classroom_subjects})

def EditObjectiveStandards(request, user_id=None, class_id=None, subject=None, lesson_id=None, standard_id=None, action=None):
    user_profile = User.objects.get(id=user_id)
    classroom_profile = classroom.objects.get(id=class_id)
    lesson_match = lessonObjective.objects.get(id=lesson_id)
    standard_match = singleStandard.objects.get(id=standard_id)
    recomendations = lessonStandardRecommendation.objects.get(lesson_classroom=classroom_profile, objectives_standard=standard_id, objectives=lesson_match )
    action = int(action)
    if action == 0:
        lesson_match.objectives_standards.add(standard_match)
        recomendations.is_selected = True
        recomendations.save()
    else:
        lesson_match.objectives_standards.remove(standard_match)
        recomendations.is_selected = False
        recomendations.save()
    return redirect('{}#standards'.format(reverse('select_standards', kwargs={'user_id':user_profile.id, 'class_id':classroom_profile.id, 'subject':subject, 'lesson_id':lesson_id})))

def SelectKeywords(request, user_id=None, class_id=None, subject=None, lesson_id=None):
    current_week = date.today().isocalendar()[1] 
    user_profile = User.objects.get(id=user_id)

    classroom_profile = classroom.objects.get(id=class_id)
    grade_list = classroom_profile.grade_level.all()

    standard_match = standardSet.objects.get(id=classroom_profile.standards_set_id)
    classroom_subjects = classroomSubjects.objects.filter(subject_classroom=classroom_profile).first()
    subjects_list = classroom_subjects.subjects.all()
    subject_matches = standardSubjects.objects.filter(id__in=classroom_subjects.subjects.all())
    
    
    class_objectives = lessonObjective.objects.all().order_by('subject')
    vocab_list = vocabularyList.objects.filter(lesson_plan__in=class_objectives)
    lesson_activities = lessonFull.objects.filter(lesson_overview__in=class_objectives)
    lesson_match = lessonObjective.objects.get(id=lesson_id)
    lesson_standards = singleStandard.objects.filter(id__in=lesson_match.objectives_standards.all())
    teacher_objective = lesson_match.teacher_objective

    related_question = googleRelatedQuestions.objects.filter(lesson_plan=lesson_match, is_selected=False)
    related_topics = googleSearchResult.objects.filter(lesson_plan=lesson_match, is_selected=False)
   
    questions_selected = googleRelatedQuestions.objects.filter(lesson_plan=lesson_match, is_selected=True)
    topics_selected = googleSearchResult.objects.filter(lesson_plan=lesson_match, is_selected=True)
    selected_wiki = wikiTopic.objects.filter(lesson_plan=lesson_match, is_selected=True)

    wiki_topics = wikiTopic.objects.filter(lesson_plan=lesson_match).exclude(is_selected=True).order_by('-relevance')

    
    if lesson_match.is_skill:
        results = google_results(teacher_objective, lesson_id)
    else:
        results = wiki_google_results(teacher_objective, lesson_id)
    
    
    
  
    step = 3
    return render(request, 'dashboard/create_objective.html', {'user_profile': user_profile, 'selected_wiki': selected_wiki, 'questions_selected': questions_selected, 'topics_selected': topics_selected,  'related_question': related_question, 'related_topics': related_topics, 'wiki_topics': wiki_topics, 'step': step, 'lesson_standards': lesson_standards, 'lesson_match': lesson_match, 'lesson_activities': lesson_activities, 'class_objectives': class_objectives, 'current_week': current_week, 'classroom_profile': classroom_profile})

def SelectRelatedInformation(request, user_id=None, class_id=None, subject=None, lesson_id=None, type_id=None, item_id=None, action=None):
    user_profile = User.objects.get(id=user_id)
    classroom_profile = classroom.objects.get(id=class_id)
    #Keyword = 1 , Google Topic = 2, Question = 3, Wiki Topic = 5  
    type_id = int(type_id)
    if type_id == 1: 
        keyword_match = keywordResults.objects.get(id=item_id)
        action = int(action)
        if action == 0:
            keyword_match.is_selected = True
            keyword_match.save()
        elif action == 2:
            keyword_match.delete()
        else:
            keyword_match.is_selected = False
            keyword_match.save()
        return redirect('{}#keywords'.format(reverse('select_keywords_two', kwargs={'user_id':user_profile.id, 'class_id':classroom_profile.id, 'subject':subject, 'lesson_id':lesson_id})))
    elif type_id == 2:
        keyword_match = googleSearchResult.objects.get(id=item_id)
        action = int(action)
        if action == 0:
            keyword_match.is_selected = True
            keyword_match.save()
        elif action == 2:
            keyword_match.delete()
        else:
            keyword_match.is_selected = False
            keyword_match.save()
        return redirect('{}#keywords'.format(reverse('select_keywords', kwargs={'user_id':user_profile.id, 'class_id':classroom_profile.id, 'subject':subject, 'lesson_id':lesson_id})))
    elif type_id == 3:
        keyword_match = googleRelatedQuestions.objects.get(id=item_id)
        action = int(action)
        if action == 0:
            keyword_match.is_selected = True
            keyword_match.save()
        elif action == 2:
            keyword_match.delete()
        else:
            keyword_match.is_selected = False
            keyword_match.save()
        return redirect('{}#keywords'.format(reverse('select_keywords', kwargs={'user_id':user_profile.id, 'class_id':classroom_profile.id, 'subject':subject, 'lesson_id':lesson_id})))
    else:
        keyword_match = wikiTopic.objects.get(id=item_id)
        action = int(action)
        if action == 0:
            keyword_match.is_selected = True
            keyword_match.save()
        elif action == 2:
            keyword_match.delete()
        else:
            keyword_match.is_selected = False
            keyword_match.save()
        return redirect('{}#keywords'.format(reverse('select_keywords', kwargs={'user_id':user_profile.id, 'class_id':classroom_profile.id, 'subject':subject, 'lesson_id':lesson_id})))

def SelectKeywordsTwo(request, user_id=None, class_id=None, subject=None, lesson_id=None):
    current_week = date.today().isocalendar()[1] 
    user_profile = User.objects.get(id=user_id)

    classroom_profile = classroom.objects.get(id=class_id)
    grade_list = classroom_profile.grade_level.all()

    standard_match = standardSet.objects.get(id=classroom_profile.standards_set_id)
    classroom_subjects = classroomSubjects.objects.filter(subject_classroom=classroom_profile).first()
    subjects_list = classroom_subjects.subjects.all()
    subject_matches = standardSubjects.objects.filter(id__in=classroom_subjects.subjects.all())
    
    
    class_objectives = lessonObjective.objects.all().order_by('subject')
    vocab_list = vocabularyList.objects.filter(lesson_plan__in=class_objectives)
    lesson_activities = lessonFull.objects.filter(lesson_overview__in=class_objectives)
    lesson_match = lessonObjective.objects.get(id=lesson_id)
    lesson_standards = singleStandard.objects.filter(id__in=lesson_match.objectives_standards.all())
    teacher_objective = lesson_match.teacher_objective



    questions_selected = googleRelatedQuestions.objects.filter(lesson_plan=lesson_match, is_selected=True)
    topics_selected = googleSearchResult.objects.filter(lesson_plan=lesson_match, is_selected=True)

    keywords_selected = keywordResults.objects.filter(lesson_plan=lesson_match, is_selected=True).order_by('-relevance')
    keywords_matched = keywordResults.objects.filter(lesson_plan=lesson_match, is_selected=False).order_by('-relevance')

    keywords = get_lesson_keywords(lesson_id)
    
    
    
  
    step = 4
    return render(request, 'dashboard/create_objective.html', {'user_profile': user_profile, 'keywords_selected': keywords_selected, 'questions_selected': questions_selected, 'topics_selected': topics_selected, 'keywords_matched': keywords_matched, 'step': step, 'lesson_standards': lesson_standards, 'lesson_match': lesson_match, 'lesson_activities': lesson_activities, 'class_objectives': class_objectives, 'current_week': current_week, 'classroom_profile': classroom_profile})



def ActivityBuilder(request, user_id=None, class_id=None, subject=None, lesson_id=None):
    current_week = date.today().isocalendar()[1] 
    user_profile = User.objects.get(id=user_id)

    classroom_profile = classroom.objects.get(id=class_id)
    grade_list = classroom_profile.grade_level.all()

    standard_match = standardSet.objects.get(id=classroom_profile.standards_set_id)
    classroom_subjects = classroomSubjects.objects.filter(subject_classroom=classroom_profile).first()
    subjects_list = classroom_subjects.subjects.all()
    subject_matches = standardSubjects.objects.filter(id__in=classroom_subjects.subjects.all())                                         
    
    
    class_objectives = lessonObjective.objects.all().order_by('subject')
    vocab_list = vocabularyList.objects.filter(lesson_plan__in=class_objectives)
    lesson_activities = lessonFull.objects.filter(lesson_overview__in=class_objectives)
    lesson_match = lessonObjective.objects.get(id=lesson_id)
    lesson_standards = singleStandard.objects.filter(id__in=lesson_match.objectives_standards.all())
    print(lesson_standards)
    teacher_objective = lesson_match.teacher_objective



    questions_selected = googleRelatedQuestions.objects.filter(lesson_plan=lesson_match, is_selected=True)
    topics_selected = googleSearchResult.objects.filter(lesson_plan=lesson_match, is_selected=True)

    keywords_selected = keywordResults.objects.filter(lesson_plan=lesson_match, is_selected=True).order_by('-relevance')
    keywords_matched = keywordResults.objects.filter(lesson_plan=lesson_match, is_selected=False).order_by('-relevance')

    keywords = get_lesson_keywords(lesson_id)
    
    
    
  
    step = 4
    return render(request, 'dashboard/activity_builder.html', {'user_profile': user_profile, 'keywords_selected': keywords_selected, 'questions_selected': questions_selected, 'topics_selected': topics_selected, 'keywords_matched': keywords_matched, 'step': step, 'lesson_standards': lesson_standards, 'lesson_match': lesson_match, 'lesson_activities': lesson_activities, 'class_objectives': class_objectives, 'current_week': current_week, 'classroom_profile': classroom_profile})




def CreateLesson(request, user_id=None, class_id=None, subject=None, lesson_id=None):
    current_week = date.today().isocalendar()[1] 
    user_profile = User.objects.get(id=user_id)

    classroom_profile = classroom.objects.get(id=class_id)
    grade_list = classroom_profile.grade_level.all()

    standard_match = standardSet.objects.get(id=classroom_profile.standards_set_id)
    classroom_subjects = classroomSubjects.objects.filter(subject_classroom=classroom_profile).first()
    subjects_list = classroom_subjects.subjects.all()
    subject_matches = standardSubjects.objects.filter(id__in=classroom_subjects.subjects.all())                                         
    
    
    class_objectives = lessonObjective.objects.all().order_by('subject')
    vocab_list = vocabularyList.objects.filter(lesson_plan__in=class_objectives)
    lesson_activities = lessonFull.objects.filter(lesson_overview__in=class_objectives)
    lesson_match = lessonObjective.objects.get(id=lesson_id)
    lesson_standards = singleStandard.objects.filter(id__in=lesson_match.objectives_standards.all())

    teacher_objective = lesson_match.teacher_objective



    questions_selected = googleRelatedQuestions.objects.filter(lesson_plan=lesson_match, is_selected=True)
    topics_selected = googleSearchResult.objects.filter(lesson_plan=lesson_match, is_selected=True)

    keywords_selected = keywordResults.objects.filter(lesson_plan=lesson_match, is_selected=True).order_by('-relevance')
    keywords_matched = keywordResults.objects.filter(lesson_plan=lesson_match, is_selected=False).order_by('-relevance')

    keywords = get_lesson_keywords(lesson_id)
    
    if request.method == "POST":
        form = lessonObjectiveForm(request.POST, request.FILES)

        if form.is_valid():
            prev = form.save(commit=False)
            prev.week_of = current_week
            subject = prev.subject_id
            classroom_match = prev.lesson_classroom_id
            prev.save()
           
            return redirect('select_standards', user_id=user_profile.id, class_id=classroom_match, subject=subject, lesson_id=prev.id)
    else:
        form = lessonObjectiveForm()
    
  
    step = 4
    return render(request, 'dashboard/activity_builder.html', {'user_profile': user_profile, 'form': form, 'keywords_selected': keywords_selected, 'questions_selected': questions_selected, 'topics_selected': topics_selected, 'keywords_matched': keywords_matched, 'step': step, 'lesson_standards': lesson_standards, 'lesson_match': lesson_match, 'lesson_activities': lesson_activities, 'class_objectives': class_objectives, 'current_week': current_week, 'classroom_profile': classroom_profile})



def StandardUploadTwo(request):
    #second step to the standards upload process
    #name="standards_upload"
    user_profile = User.objects.filter(username=request.user.username).first()

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

    return redirect('Dashboard', week_of='Current')


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
from django.forms import modelformset_factory, inlineformset_factory
import random
from django.http import JsonResponse
import json
try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract
import csv, io
from django.template.loader import get_template
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from twilio.rest import Client
from twilio.rest import TwilioRestClient
from pytesseract import image_to_string

from .forms import *
from .models import *
import random
from .activity_builder import *
from .get_lessons import *
from .get_questions import *
from .ocr import * 
from .get_classrooms import *
from .get_openai import *
from .get_performance import *
from .get_students import * 
##################| Homepage Views |#####################
#Homepage Landing Page
def Homepage(request):
    

    if request.method == "POST":

        form = TeacherForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            
            user_email = form.cleaned_data.get('email')
            my_number = form.cleaned_data.get('phone_number')
            if '+1' in my_number:
                pass
            else:
                my_number = '+1', my_number
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            user_id = user.id
            
            welcome_message = 'Welcome to Class Planit, %s! We will be in touch when your account is activated.' % (username)
        
            to = str(my_number)
            if to:
                try:
                    client = Client(config('TWILIO_ACCOUNT_SID'), config('TWILIO_AUTH_TOKEN'))
                    response = client.messages.create(
                            body=str(welcome_message),
                            to=to, from_=config('TWILIO_PHONE_NUMBER'))
                    message = Mail(
                            from_email='welcome@classplanit.co',
                            to_emails=user_email,
                            subject='Welcome to Class Planit',
                            html_content= get_template('dashboard/welcome_to_class_planit.html').render({'user': user}))
                except Exception as e:
                    pass
            try:
                sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
                response = sg.send(message)
                print(response.status_code)
                print(response.body)
                print(response.headers)
            except Exception as e:
                pass
            return redirect('thank_you', user_id=user_id)
        else:
            return redirect('registration_full', retry=True)
        
    else:

        form = TeacherForm()
    
    choice = random.choice([1, 2])
    if choice == 1:
        return render(request, 'homepage/index.html', {'form': form})
    else:
        return render(request, 'homepage/index2.html', {'form': form})

#Full Form Regstration if error on pop up modal
def FormFull(request, retry=None):
    if retry:
        message = 'Something Went Wrong! Please complete your registration again.'
    else:
        message = "Let's Get Started!"
    if request.method == "POST":

        form = TeacherForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            
            user_email = form.cleaned_data.get('email')
            my_number = form.cleaned_data.get('phone_number')
            if '+1' in my_number:
                pass
            else:
                my_number = '+1', my_number
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            user_id = user.id
            
            welcome_message = 'Welcome to Class Planit, %s! We will be in touch when your account is activated.' % (username)
        
            to = str(my_number)
            if to:
                try:
                    client = Client(config('TWILIO_ACCOUNT_SID'), config('TWILIO_AUTH_TOKEN'))
                    response = client.messages.create(
                            body=str(welcome_message),
                            to=to, from_=config('TWILIO_PHONE_NUMBER'))
                    message = Mail(
                            from_email='welcome@classplanit.co',
                            to_emails=user_email,
                            subject='Welcome to Class Planit',
                            html_content= get_template('dashboard/welcome_to_class_planit.html').render({'user': user}))
                except Exception as e:
                    pass
            try:
                sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
                response = sg.send(message)
                print(response.status_code)
                print(response.body)
                print(response.headers)
            except Exception as e:
                pass
            return redirect('thank_you', user_id=user_id)

    else:

        form = TeacherForm()
    
    return render(request, 'homepage/registration_full.html', {'form': form, 'message': message})

#User Login 
def login_user(request):

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('Dashboard', week_of='Current')
        else:
            pass
  
    return render(request, 'dashboard/sign-in.html', {})

#How it works page to explain the product 
class HowItWorks(TemplateView):
    template_name = 'homepage/how_it_works.html' 

    def get(self,request):

        return render(request, 'homepage/how_it_works.html', { })

#?not sure what this view does, will test
class Services(TemplateView):
    template_name = 'homepage/services.html' 

    def get(self,request):

        return render(request, 'homepage/services.html', { })

#Teams page 
class AboutUs(TemplateView):
    template_name = 'homepage/about.html' 

    def get(self,request):

        return render(request, 'homepage/about.html', { })

##################| End Homepage Views |#####################
class classroomLists(TemplateView):
    template_name = 'dashboard/classroom_list.html' 

    def get(self,request):
        current_year = datetime.datetime.now().year
        current_week = date.today().isocalendar()[1] 
        user_profile = User.objects.filter(username=request.user.username).first()
        class_summary = get_classroom_summary(user_profile.id, current_year)
        
        page = 'Classrooms'
        return render(request, 'dashboard/classroom_list.html', {'user_profile': user_profile, 'class_summary': class_summary, 'page': page})


def ClassroomSingle(request, user_id=None, class_id=None):
    current_year = datetime.datetime.now().year
    user_profile = User.objects.filter(username=request.user.username).first()
    class_profile = classroom.objects.get(id=class_id)
    student_summary = get_classroom_list_summary(user_profile.id, current_year, class_id)
    return render(request, 'dashboard/classrooms.html', {'user_profile': user_profile, 'student_summary': student_summary, 'class_profile': class_profile})


#Main Dashboard View labeled as 'Overview'
class Dashboard(TemplateView):
    template_name = 'dashboard/dashboard.html' 

    def get(self,request,week_of):
        current_week = date.today().isocalendar()[1] 
        if 'Current' in week_of:
            active_week = current_week
        else:
            active_week = int(week_of)
        user_profile = User.objects.filter(username=request.user.username).first()
        if user_profile:
            classroom_profiles = classroom.objects.filter(main_teacher=user_profile)

            objective_matches = lessonObjective.objects.filter(week_of=active_week, lesson_classroom__in=classroom_profiles)

            return render(request, 'dashboard/dashboard.html', {'user_profile': user_profile, 'current_week': current_week, 'active_week': active_week, 'objective_matches': objective_matches})
        else:
            return redirect('login_user')


#Step One Teachers type in their Objective 
def CreateObjective(request, user_id=None, week_of=None):
    user_profile = User.objects.filter(username=request.user.username).first()
    user_classrooms = classroom.objects.filter(main_teacher=user_profile)
    


    if 'Current' in week_of:
        current_week = date.today().isocalendar()[1] 
    else:
        current_week = int(week_of)

    if user_classrooms:
        subjects = []
        for classroom_m in user_classrooms:
            s_match = classroom_m.subjects.all()
            subject_match = standardSubjects.objects.filter(id__in=s_match)
            if subject_match not in subjects:
                subjects.append(subject_match)

    else:
        subjects = []


    if request.method == "POST":
        form = lessonObjectiveForm(request.POST, request.FILES)

        if form.is_valid():
            prev = form.save(commit=False)
            prev.week_of = current_week
            subject = prev.subject_id
            selected_class = prev.lesson_classroom_id
            
            prev.save()

            return redirect('activity_builder', user_id=user_profile.id, class_id=selected_class, subject=subject, lesson_id=prev.id, page=0)
    else:
        form = lessonObjectiveForm()
  



    step = 1
    return render(request, 'dashboard/identify_objectives.html', {'form': form, 'step': step, 'user_profile': user_profile, 'user_classrooms': user_classrooms, 'subjects': subjects  })


def ActivityBuilder(request, user_id=None, class_id=None, subject=None, lesson_id=None, page=None):
    current_week = date.today().isocalendar()[1] 
    user_profile = User.objects.get(id=user_id)
    
    classroom_profile = classroom.objects.get(id=class_id)
    lesson_match = lessonObjective.objects.get(id=lesson_id)
    l_topics = lesson_match.objectives_topics.all()
    lesson_topics = topicInformation.objects.filter(id__in=l_topics)

    teacher_input = lesson_match.teacher_objective
    standards_matches = lesson_match.objectives_standards.all()

    standards_topics = activity_builder_task(teacher_input, class_id, lesson_id, user_id)
    
    matched_standards = standards_topics['matched_standards']

    standards_select = singleStandard.objects.filter(id__in=matched_standards)

    
        
    new_text, created = lessonText.objects.get_or_create(matched_lesson=lesson_match)

    
    return render(request, 'dashboard/activity_builder.html', {'user_profile': user_profile, 'new_text': new_text, 'classroom_profile': classroom_profile, 'lesson_match': lesson_match, 'standards_select': standards_select, 'standards_matches': standards_matches })

#Adds or Removes Selected Standards
def EditObjectiveStandards(request, user_id=None, class_id=None, subject=None, lesson_id=None, standard_id=None, action=None):
    user_profile = User.objects.get(id=user_id)
    classroom_profile = classroom.objects.get(id=class_id)
    lesson_match = lessonObjective.objects.get(id=lesson_id)
    standard_match = singleStandard.objects.get(id=standard_id)
    
    action = int(action)
    if action == 0:
        lesson_match.objectives_standards.add(standard_match)

    else:
        lesson_match.objectives_standards.remove(standard_match)

    
    return redirect('activity_builder', user_id=user_profile.id, class_id=class_id, subject=subject, lesson_id=lesson_id, page=0)


def SelectTopic(request):
    if request.method == 'GET':
        user_profile = User.objects.filter(username=request.user.username).first()
        user_id = user_profile.id
        topic_id = request.GET['topic_id']
        lesson_id = request.GET['lesson_id']
        lesson_match = lessonObjective.objects.get(id=lesson_id)
        topic_match = topicInformation.objects.get(id=topic_id)
        update_lesson = lesson_match.objectives_topics.add(topic_match)

        description_list = []
        for desc in topic_match.description.all():
            if desc.created_by_id == user_id:
                if desc.is_admin == False:
                    result = "<li id='description'>%s</li>" % (desc.description)
                    description_list.append(result)
        if description_list:
            pass
        else:
            description_list = []
            for desc in topic_match.description.all():
                if desc.is_admin == True:
                    result = "<li id='description'>%s</li>" % (desc.description)
                    description_list.append(result)
        description_list = ' '.join(description_list)
        final = "<ul>%s</ul>" % (description_list)
        context = {'term': topic_match.item, 'description': final}

        return JsonResponse(context)
    else:
        return HttpResponse("Request method is not a GET")


def SelectActivity(request):
    if request.method == 'GET':
        user_profile = User.objects.filter(username=request.user.username).first()
        user_id = user_profile.id
        activity_id = request.GET['activity_id']
        lesson_id = request.GET['lesson_id']
        lesson_match = lessonObjective.objects.get(id=lesson_id)
        activity_match = selectedActivity.objects.get(id=activity_id)

        activity_match.is_selected = True 
        activity_match.save()

        context = {'text': activity_match.lesson_text}

        return JsonResponse(context)
    else:
        return HttpResponse("Request method is not a GET")


def SaveLessonText(request, lesson_id):
    user = User.objects.filter(id=request.user.id).first()
    lesson_match = lessonObjective.objects.get(id=lesson_id)
    new_text, created = lessonText.objects.get_or_create(matched_lesson=lesson_match)
    less_class = lesson_match.lesson_classroom_id
    if request.method == 'GET':
        overview = request.GET['overview']
        new_text.overview = overview
        new_text.is_initial = False
        new_text.save()
        update_lesson_analytics = get_lesson_sections(overview, less_class, lesson_id, user.id)
        now = datetime.datetime.now().strftime('%H:%M:%S')
        context = {"data": now}
        return JsonResponse(context)
    else:
        return HttpResponse("Request method is not a GET")

def SelectStandards(request, lesson_id):
    user = User.objects.filter(id=request.user.id).first()
    lesson_match = lessonObjective.objects.get(id=lesson_id)
    
    if request.method == 'GET':
        stand_id = request.GET['stand_id']
        standard_match = singleStandard.objects.get(id=stand_id)
        lesson_match.objectives_standards.add(standard_match)
        strandard_result = str(standard_match.standard_objective) + str(standard_match.competency)

        context = {"data": strandard_result}
        return JsonResponse(context)
    else:
        return HttpResponse("Request method is not a GET")


def GetActivitySummary(request, lesson_id):
    if request.method == 'GET':
        user_profile = User.objects.filter(id=request.user.id).first()
        lesson_analytics = label_activities_analytics_small(lesson_id)
        context = {"data": lesson_analytics, "message": "your message"}
        return JsonResponse(context)
    else:
        return HttpResponse("Request method is not a GET")


def GetBloomsAnalytics(request, lesson_id):
    if request.method == 'GET':
        user_profile = User.objects.filter(id=request.user.id).first()
        get_bl_data = label_blooms_activities_analytics(lesson_id)
        get_mi_data = label_mi_activities_analytics(lesson_id)
        context = {"data": get_bl_data, "message": "your message"}
        return JsonResponse(context)
    else:
        return HttpResponse("Request method is not a GET")

def GetMIAnalytics(request, lesson_id):
    if request.method == 'GET':
        user_profile = User.objects.filter(id=request.user.id).first()
        get_mi_data = label_mi_activities_analytics(lesson_id)
        context = {"data": get_mi_data, "message": "your message"}
        return JsonResponse(context)
    else:
        return HttpResponse("Request method is not a GET")

def GetRetentionAnalytics(request, lesson_id):
    if request.method == 'GET':
        user_profile = User.objects.filter(id=request.user.id).first()
        get_retention_data = retention_activities_analytics(lesson_id)
        context = {"data": get_retention_data, "message": "your message"}

        return JsonResponse(context)
    else:
        return HttpResponse("Request method is not a GET")


def UpdateKeyTerms(request, lesson_id, class_id):
    if request.method == 'GET':
        user_profile = User.objects.filter(id=request.user.id).first()
        lesson_match = lessonObjective.objects.get(id=lesson_id)
        teacher_input = lesson_match.teacher_objective
        update_term_list = activity_builder_jq(teacher_input, class_id, lesson_id, user_profile.id)
        context = {"data": update_term_list, "message": "your message"}

        return JsonResponse(context)
    else:
        return HttpResponse("Request method is not a GET")


def UpdateLessonActivities(request, lesson_id, class_id):
    if request.method == 'GET':
        user_profile = User.objects.filter(id=request.user.id).first()
        lesson_match = lessonObjective.objects.get(id=lesson_id)
        teacher_input = lesson_match.teacher_objective
        update_activity_list = get_lessons(lesson_id, user_profile.id)

        context = {"data": update_activity_list, "message": "your message"}

        return JsonResponse(context)
    else:
        return HttpResponse("Request method is not a GET")

  

def view_name(request):
    if request.method == 'GET':
        user_profile = User.objects.filter(id=request.user.id).first()
        html = [{
                "Id": 49,
                "SupplierName": "Supplier 1"
            }, {
                "Id": 50,
                "SupplierName": "Supplier 2"
            }, {
                "Id": 51,
                "SupplierName": "Supplier 3"
            }, {
                "Id": 52,
                "SupplierName": "Supplier 4"
            }]
        context = {"data": html, "message": "your message"}
        return JsonResponse(context)
    else:
        return HttpResponse("Request method is not a GET")

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
    elif type_id == 7:
        keyword_match = youtubeSearchResult.objects.get(id=item_id)
        action = int(action)
        if action == 0:
            keyword_match.is_selected = True
            keyword_match.save()
        else:
            keyword_match.is_selected = False
            keyword_match.save()
        return redirect('{}#youtube'.format(reverse('select_keywords', kwargs={'user_id':user_profile.id, 'class_id':classroom_profile.id, 'subject':subject, 'lesson_id':lesson_id})))
    elif type_id == 6:
        lesson_match = lessonObjective.objects.get(id=lesson_id)
        topic_match = topicInformation.objects.get(id=item_id)
        action = int(action)
        if action == 0:
            update_lesson = lesson_match.objectives_topics.remove(topic_match)
        else:
            update_lesson = lesson_match.objectives_topics.add(topic_match)
        return redirect('{}#keywords'.format(reverse('activity_builder', kwargs={'user_id':user_profile.id, 'class_id':classroom_profile.id, 'subject':subject, 'lesson_id':lesson_id, 'page': 0})))
    elif type_id == 8:
        lesson_match = lessonObjective.objects.get(id=lesson_id)
        topic_match = topicInformation.objects.get(id=item_id)
        action = int(action)
        if action == 0:
            update_lesson = lesson_match.objectives_topics.remove(topic_match)
        else:
            update_lesson = lesson_match.objectives_topics.add(topic_match)
        return redirect('{}#youtube'.format(reverse('select_standards_two', kwargs={'user_id':user_profile.id, 'class_id':classroom_profile.id, 'subject':subject, 'lesson_id':lesson_id, 'select_all':False})))
    elif type_id == 10:
        lesson_match = lessonObjective.objects.get(id=lesson_id)
        topic_match = selectedActivity.objects.get(id=item_id)
        action = int(action)

        if action == 0:
            topic_match.is_selected = True 
            topic_match.save()
        else:
            topic_match.is_selected = False
            topic_match.save()
        return redirect('{}#keywords'.format(reverse('activity_builder', kwargs={'user_id':user_profile.id, 'class_id':classroom_profile.id, 'subject':subject, 'lesson_id':lesson_id, 'page': 0})))
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


def DigitalActivities(request, user_id=None, class_id=None, subject=None, lesson_id=None, worksheet_id=None, page=None, act_id=None, question_id=None):
    current_week = date.today().isocalendar()[1] 
    user_profile = User.objects.filter(id=user_id).first()

    classroom_profile = classroom.objects.get(id=class_id)
    grade_list = classroom_profile.grade_level.all()
    grade_match = gradeLevel.objects.filter(id__in=grade_list).first()
    standard_match = standardSet.objects.get(id=classroom_profile.standards_set_id)

    lesson_match = lessonObjective.objects.get(id=lesson_id)
    subject_match = lesson_match.subject_id
    subject_match_full = standardSubjects.objects.get(id=subject_match) 


    worksheet_title = '%s: %s %s for week of %s' % (user_profile, classroom_profile, subject_match_full, current_week) 
    get_worksheet, created = worksheetFull.objects.get_or_create(created_by=user_profile, title=worksheet_title, lesson_overview=lesson_match)
    question_matches = get_worksheet.questions.all()

    check_lesson_questions = topicQuestion.objects.filter(id__in=question_matches)
    
    if check_lesson_questions:
        all_matched_questions = topicQuestion.objects.filter(lesson_overview=lesson_match)
        matched_questions = topicQuestion.objects.filter(id__in=question_matches)
    else:
        text_questions_one = get_question_text(lesson_id, user_profile)
        matched_questions = topicQuestion.objects.filter(id__in=text_questions_one).order_by('?')[:10]
        line_match = []
        for quest in matched_questions:
            l_text = quest.linked_text
            l_topic = quest.linked_topic
            if l_text:
                result = l_text
            else:
                result = l_topic

            if result not in line_match:
                line_match.append(result)
                get_worksheet.questions.add(quest)
        all_matched_questions = topicQuestion.objects.filter(id__in=text_questions_one)
    
    

    short_answer  = []
    fib = []
    multi_choice = []
    unknown = []
    for quest in all_matched_questions:
        quest_type = quest.question_type_id

        short_a = questionType.objects.get(item='short_answer')
        fill_a = questionType.objects.get(item='fill_in_the_blank')
        mc = questionType.objects.get(item='multi_choice')
        if short_a.id == quest_type:
            short_answer.append(quest)
        elif fill_a.id == quest_type:
            fib.append(quest)
        elif mc.id == quest_type:
            multi_choice.append(quest)
        else:
            unknown.append(quest)


    if 'None' in question_id:
        question_match = current_question = None
        next_q = 1
        question_id = 0
    else:
        if matched_questions:
            q = int(question_id)
            next_q = q + 1
            question_match = current_question = matched_questions[q]
        else:
            question_match = current_question = None
            next_q = 1
            question_id = 0
    

    if 'False' in act_id:
        pass
    else:
        question_match = current_question = topicQuestion.objects.get(id=act_id)

    lesson_standards = singleStandard.objects.filter(id__in=lesson_match.objectives_standards.all())
    topic_matches = lesson_match.objectives_topics.all()
    topic_lists_selected = topicInformation.objects.filter(id__in=topic_matches).order_by('item')

    worksheet_theme = worksheetTheme.objects.get(id=1)

    img_id = worksheet_theme.background_image

    background_img = userImageUpload.objects.filter(id=worksheet_theme.background_image_id).first()

    return render(request, 'dashboard/activity_builder_2.html', {'user_profile': user_profile, 'get_worksheet': get_worksheet, 'all_matched_questions': all_matched_questions, 'question_match': question_match, 'question_id': question_id, 'next_q': next_q, 'background_img': background_img, 'worksheet_theme': worksheet_theme, 'current_question': current_question, \
                                                                 'matched_questions': matched_questions, 'subject_match_full': subject_match_full, 'current_week': current_week, 'page': page, 'class_id': class_id, 'subject': subject, 'lesson_id': lesson_id, \
                                                                  'short_answer': short_answer, 'fib':fib, 'multi_choice':multi_choice, 'unknown':unknown})


def StudentDashboard(request, lesson_id=None, worksheet_id=None, question_id=None):
    user_profile = User.objects.filter(id=request.user.id).first()
    worksheet_match = worksheetFull.objects.get(id=worksheet_id)
    if user_profile:
        question_matches = worksheet_match.questions.all()
        matched_questions = topicQuestion.objects.filter(id__in=question_matches)
        student_answer_sheet, created = studentWorksheetAnswerFull.objects.get_or_create(student=user_profile, worksheet_assignment=worksheet_match)
        s_answers = student_answer_sheet.student_answers.all()
        single_answers = studentQuestionAnswer.objects.filter(id__in=s_answers)

        word_bank = []
        question_list = []
        for quest in matched_questions:
            quest_type = quest.question_type_id
            short_a = questionType.objects.get(item='short_answer')
            fill_a = questionType.objects.get(item='fill_in_the_blank')
            mc = questionType.objects.get(item='multi_choice')
            if short_a.id == quest_type:
                result = 'short_answer', quest, quest.Correct
                question_list.append(result)
            elif fill_a.id == quest_type:

                result = 'fill_in_the_blank', quest, quest.Correct
                word_bank.append(quest.Correct)
                question_list.append(result)
            elif mc.id == quest_type:
                result = 'multi_choice', quest
                correct = quest.Correct
                i_one = quest.Incorrect_One
                i_two = quest.Incorrect_Two
                i_three = quest.Incorrect_Three
                answers = [correct, i_one, i_two, i_three]
                random.shuffle(answers)
                result = 'multi_choice', quest, answers, quest.Correct
                question_list.append(result)
            else:
                result = 'short_answer', quest, quest.Correct
                question_list.append(result)

        

        question_count = len(question_list)

        q = int(question_id)

        previous_q = q - 1
        if previous_q < 0:
            previous_q = 0

        next_q = q + 1
        if next_q > question_count:
            next_q = question_count

        question_match = current_question = question_list[q]

        student_answer = None
        for answer in single_answers:
            quest_id = answer.question_num_id
            c_question = current_question[1]
            current_id = c_question.id
            if quest_id == current_id:
                student_answer = answer.answer
            
        current_per = (q/question_count) * 100

        worksheet_theme = worksheetTheme.objects.get(id=1)

        img_id = worksheet_theme.background_image

        background_img = userImageUpload.objects.filter(id=worksheet_theme.background_image_id).first()
        form = StudentForm()
        return render(request, 'dashboard/student_dashboard.html', {'user_profile': user_profile, 'current_per': current_per, 'question_count': question_count, 'word_bank': word_bank, 'single_answers': single_answers, 'student_answer': student_answer, 'worksheet_match': worksheet_match, 'lesson_id':lesson_id, 'worksheet_id':worksheet_id, 'question_id':question_id, 'form': form, 'previous_q': previous_q, 'next_q': next_q, 'current_question': current_question, 'worksheet_theme': worksheet_theme, 'background_img': background_img})
    else:
        form = StudentForm()
        login_required = True
        return render(request, 'dashboard/student_dashboard.html', {'login_required': login_required, 'form': form, 'lesson_id':lesson_id, 'worksheet_id':worksheet_id,})

def StudentWorksheetSubmit(request, user_id=None, lesson_id=None, worksheet_id=None, submit=None):
    user_profile = User.objects.filter(id=request.user.id).first()
    worksheet_match = worksheetFull.objects.get(id=worksheet_id)

    question_matches = worksheet_match.questions.all()
    matched_questions = topicQuestion.objects.filter(id__in=question_matches)
    student_answer_sheet = studentWorksheetAnswerFull.objects.filter(student=user_profile, worksheet_assignment=worksheet_match).first()
    s_answers = student_answer_sheet.student_answers.all()
    single_answers = studentQuestionAnswer.objects.filter(id__in=s_answers)
    
    if 'true' in submit:
        student_answer_sheet.is_submitted = True
        student_answer_sheet.save()
        return redirect('student_main', user_id=user_profile.id)

    return render(request, 'dashboard/student_submit.html', {'user_profile': user_profile, 'single_answers': single_answers, 'worksheet_id': worksheet_id, 'lesson_id': lesson_id })

def StudentMainDashboard(request, user_id=None, lesson_id=None, worksheet_id=None, submit=None):
    form = StudentForm()
    form2 = StudentForm()
    user_profile = User.objects.filter(id=user_id).first()
    return render(request, 'dashboard/student_main.html', {'user_profile': user_profile, 'form': form, 'form2': form2 })

def StudentMCSelect(request, user_id=None, lesson_id=None, worksheet_id=None):

    if request.method == 'GET':
        user_profile = User.objects.filter(username=request.user.username).first()
        worksheet_match = worksheetFull.objects.get(id=worksheet_id)
        student_answer_key, created  = studentWorksheetAnswerFull.objects.get_or_create(student=user_profile, worksheet_assignment=worksheet_match)

        user_id = user_profile.id
        question_id = request.GET['question_id']
        question = request.GET['question']
        answer = request.GET['answer']
        match_question = topicQuestion.objects.get(id=question_id)
        correct_answer = match_question.Correct
        single_answer, created = studentQuestionAnswer.objects.get_or_create(worksheet_assignment=worksheet_match, student=user_profile, question_num=match_question)
        single_answer.question = question
        single_answer.correct = correct_answer
        single_answer.answer = answer
        if answer == correct_answer:
            single_answer.is_correct = True
        
        single_answer.is_graded = True
        single_answer.save()
        student_answer_key.student_answers.add(single_answer)

        context = {'data': answer}
        return JsonResponse(context)
    else:
        return HttpResponse("Request method is not a GET")


def StudentFIBAnswer(request, user_id=None, lesson_id=None, worksheet_id=None, question_id=None, index_id=None):

    if request.method == 'GET':
        user_profile = User.objects.filter(username=request.user.username).first()
        worksheet_match = worksheetFull.objects.get(id=worksheet_id)
        student_answer_key, created  = studentWorksheetAnswerFull.objects.get_or_create(student=user_profile, worksheet_assignment=worksheet_match)
        match_question = topicQuestion.objects.get(id=question_id)
        correct_answer = match_question.Correct
        question = match_question.Question
        answer = request.GET["fibanswer"]

        single_answer, created = studentQuestionAnswer.objects.get_or_create(worksheet_assignment=worksheet_match, student=user_profile, question_num=match_question)
        single_answer.question = question
        single_answer.correct = correct_answer
        single_answer.answer = answer
        if answer == correct_answer:
            single_answer.is_correct = True
        
        single_answer.is_graded = True
        single_answer.save()
        student_answer_key.student_answers.add(single_answer)
        
        return redirect('student_dashboard', lesson_id=lesson_id, worksheet_id=worksheet_id, question_id=index_id)
    else:
        return HttpResponse("Request method is not a GET")


def StudentSAAnswer(request, user_id=None, lesson_id=None, worksheet_id=None, question_id=None, index_id=None):

    if request.method == 'GET':
        user_profile = User.objects.filter(username=request.user.username).first()
        worksheet_match = worksheetFull.objects.get(id=worksheet_id)
        student_answer_key, created  = studentWorksheetAnswerFull.objects.get_or_create(student=user_profile, worksheet_assignment=worksheet_match)
        match_question = topicQuestion.objects.get(id=question_id)
        question = match_question.Question
        answer = request.GET["saanswer"]

        single_answer, created = studentQuestionAnswer.objects.get_or_create(worksheet_assignment=worksheet_match, student=user_profile, question_num=match_question)
        single_answer.question = question
        single_answer.answer = answer

        single_answer.save()
        student_answer_key.student_answers.add(single_answer)
        
        return redirect('student_dashboard', lesson_id=lesson_id, worksheet_id=worksheet_id, question_id=index_id)
    else:
        return HttpResponse("Request method is not a GET")

  
def StudentRegistration(request, lesson_id=None, worksheet_id=None):
    current_year = datetime.datetime.now().year

    worksheet_match = worksheetFull.objects.get(id=worksheet_id)
    lesson_match = lessonObjective.objects.get(id=lesson_id)
    l_classroom = lesson_match.lesson_classroom_id
    class_match = classroom.objects.get(id=l_classroom)
    classroom_list, created = classroomLists.objects.get_or_create(lesson_classroom=class_match, year=current_year)

    if request.method == "POST":
        form = StudentForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            user_id = user.id
            create_student, created = studentProfiles.objects.get_or_create(first_name = first_name, last_name = last_name, is_enrolled =True, student_username = user)
            classroom_list.students.add(create_student)
            if user is not None:
                login(request, user)

            return redirect('student_dashboard', lesson_id=lesson_id, worksheet_id=worksheet_id, question_id=0)
        else:
            return redirect('student_dashboard', lesson_id=lesson_id, worksheet_id=worksheet_id, question_id=0)
    
#User Login 
def StudentLogin(request, lesson_id=None, worksheet_id=None):

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('student_dashboard', lesson_id=lesson_id, worksheet_id=worksheet_id, question_id=0)
        else:
            pass
  
    return render(request, 'dashboard/sign-in.html', {})

def EditQuestions(request, user_id=None, class_id=None, subject=None, lesson_id=None, worksheet_id=None, page=None, act_id=None, question_id=None):
    user_profile = User.objects.get(id=user_id)
    question_match = topicQuestion.objects.get(id=question_id)
    question_type = question_match.question_type
    worksheet_match = worksheetFull.objects.get(id=worksheet_id)
    subject_match = standardSubjects.objects.get(id=subject)
    if request.method == "POST":
        form = topicQuestionForm(request.POST, request.FILES, instance=question_match)

        if form.is_valid():
            prev = form.save(commit=False)
            prev.question_type = question_type
            prev.subject = subject_match
            prev.is_admin = False
            prev.created_by = user_profile
            prev.save()
            worksheet_match.questions.add(prev)

    return redirect('digital_activities', user_id=user_id, class_id=class_id, lesson_id=lesson_id, subject=1, page='Preview', worksheet_id=worksheet_id, act_id='False', question_id=0)

def NewQuestions(request, user_id=None, class_id=None, subject=None, lesson_id=None, worksheet_id=None, page=None, act_id=None, question_id=None):
    user_profile = User.objects.get(id=user_id)
    worksheet_match = worksheetFull.objects.get(id=worksheet_id)
    subject_match = standardSubjects.objects.get(id=subject)
    if request.method == "POST":
        form = topicQuestionForm(request.POST, request.FILES)

        if form.is_valid():
            prev = form.save(commit=False)
            prev.subject = subject_match
            prev.is_admin = False
            prev.created_by = user_profile
            prev.save()
            worksheet_match.questions.add(prev)
        return redirect('digital_activities', user_id=user_id, class_id=class_id, lesson_id=lesson_id, subject=1, page='Preview', worksheet_id=worksheet_id, act_id='False', question_id=0)


def StudentPerformance(request, user_id, class_id, week_of):
    all_themes = studentPraiseTheme.objects.all()
    user_profile = User.objects.get(id=user_id)
    current_year = datetime.datetime.now().year
    current_week = date.today().isocalendar()[1]
    start = current_week - 12
    if start < 1:
        start = 1
    

    week_breakdown = get_weekly_brackets(user_id, start, current_week, current_year)
    top_lessons = get_demo_ks_brackets(user_id, start, current_week, current_year)
    student_results = get_student_results(user_id, start, current_week, current_year)
    return render(request, 'dashboard/tasks.html', {'user_profile': user_profile, 'all_themes': all_themes, 'week_breakdown': week_breakdown, 'top_lessons': top_lessons, 'student_results': student_results})
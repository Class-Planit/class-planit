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
from .match_standards import *
from .textbook_matching import *
from .word_cluster import *
from .topic_matching import *
from .ocr import *
from weasyprint import HTML, CSS
import tempfile
from .tasks import *
from .get_questions import *
from .lesson_planner import *
import random

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


def RegisterStudent(request, worksheet_id=None):
    

    if request.method == "POST":

        form = studentProfilesForm(request.POST)
        if form.is_valid():
            prev = form.save(commit=False)
            student_pin = prev.student_pin
            prev.save()
            worksheet_id = int(worksheet_id)
            if worksheet_id == 0:
                return redirect('student_dashboard', student_id=prev.id, pin=student_pin)
            else:
                return redirect('worksheet_start', student_id=prev.id, pin=student_pin, worksheet_id=worksheet_id)
    else:

        form = studentProfilesForm()
    return render(request, 'dashboard/student_register.html', {'form': form, 'worksheet_id': worksheet_id})



def LoginStudent(request, worksheet_id=None):
    

    if request.method == "POST":

        form = studentProfilesForm(request.POST)
        if form.is_valid():
            prev = form.save(commit=False)
            student_pin = prev.student_pin
            prev.save()

            worksheet_id = int(worksheet_id)
            if worksheet_id == 0:
                return redirect('student_dashboard', student_id=prev.id, pin=student_pin)
            else:
                return redirect('worksheet_start', student_id=prev.id, pin=student_pin, worksheet_id=worksheet_id)

    else:

        form = studentProfilesForm()
    return render(request, 'dashboard/student_register.html', {'form': form, 'worksheet_id': worksheet_id})


def StudentDashboard(request, student_id=None, pin=None):
    matched_students = studentProfiles.objects.filter(id=student_id, pin=pin).first()

    return render(request, 'dashboard/student_dashboard.html', {})


def StudentWorksheetStart(request, student_id=None, pin=None, worksheet_id=None):
    matched_students = studentProfiles.objects.filter(id=student_id, pin=pin).first()
    worksheet_match = worksheetFull.objects.get(id=worksheet_id)
    return render(request, 'dashboard/student_worksheet.html', {'matched_students': matched_students, 'worksheet_match': worksheet_match})

#Teacher Questionnaire 
def QuestionnaireFull(request):

    if request.method == "POST":

        form = teacherQuestionnaireForm(request.POST)
        if form.is_valid():
            form.save()
            
            return redirect('thank_you_questionnaire')
    else:

        form = teacherQuestionnaireForm()
    
    return render(request, 'homepage/teacher_questionnaire.html', {'form': form})

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

#Thank for Registering Page, we will get back to you
class ThankYou(TemplateView):
    template_name = 'homepage/thank_you.html' 

    def get(self,request,user_id):
        user_profile = User.objects.get(id=user_id)

        return render(request, 'homepage/thank_you.html', {'user_profile': user_profile })

#Thanks for submitting the questionnaire
class ThankYouQuestionnaire(TemplateView):
    template_name = 'homepage/thank_you_questionnaire.html' 

    def get(self,request):
        return render(request, 'homepage/thank_you_questionnaire.html', {})

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

##################| End Homepage Views |#####################


##########################################################
##################| Dashboard Views |#####################

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

#user settings 
def AccountSetup(request, user_id):
    if request.method == "POST":
        user_profile = User.objects.filter(username=request.user.username).first()
        form = classroomForm(request.POST, request.FILES)

        if form.is_valid():
            prev = form.save(commit=False)
            prev.main_teacher = user_profile
            prev.is_active = True
            prev.save()
        
        
            return redirect('select_standards', user_id=user_profile.id, class_id=classroom_match, subject=subject, lesson_id=prev.id, select_all=False, topic_id='False')
    else:
        user_profile = User.objects.filter(username=request.user.username).first()
        form = classroomForm()
        step = 'One'
        return render(request, 'dashboard/account_setup.html', {'user_profile': user_profile})

#?not sure what this view does, will test
class AccountSetupTwo(TemplateView):
    template_name = 'dashboard/account_setup.html' 

    def get(self,request,user_id):
        if request.method == "POST":
            user_profile = User.objects.filter(username=request.user.username).first()
            form = classroomForm(request.POST, request.FILES)

            if form.is_valid():
                prev = form.save(commit=False)
                prev.main_teacher = user_profile
                prev.is_active = True
                prev.save()
            
            
                return redirect('select_standards', user_id=user_profile.id, class_id=classroom_match, subject=subject, lesson_id=prev.id, select_all=False, topic_id='False')
        else:
            user_profile = User.objects.filter(username=request.user.username).first()
            form = classroomForm()
            step = 'One'
            return render(request, 'dashboard/account_setup.html', {'user_profile': user_profile})

##################| Classroom Tabs Views |#####################
#Main Classroom View labeled as 'Classrooms'
class ClassroomList(TemplateView):
    template_name = 'dashboard/classroom_list.html' 

    def get(self,request):
        current_week = date.today().isocalendar()[1] 
        user_profile = User.objects.filter(username=request.user.username).first()
        classroom_profiles = classroom.objects.filter(main_teacher=user_profile)
        page = 'Classrooms'

        return render(request, 'dashboard/classroom_list.html', {'user_profile': user_profile, 'classroom_profiles': classroom_profiles, 'page': page})

#Create New Classroom 
def CreateClassroom(request, user_id=None, class_id=None):
    user_profile = User.objects.filter(username=request.user.username).first()
    s_user = school_user.objects.filter(user_id=user_profile.id).first()
    ay = academicYear.objects.filter(planning_teacher=user_profile).first()
    
    grade_levels = gradeLevel.objects.filter(standards_set=s_user.standards_set)
    if request.method == "POST":
        user_profile = User.objects.filter(username=request.user.username).first()
        form = classroomForm(request.POST, request.FILES)

        if form.is_valid():
            grade_level = form.cleaned_data.get('grade_level')
           
            prev = form.save(commit=False)
            prev.main_teacher = user_profile
            prev.is_active = True
            prev.standards_set = s_user.standards_set
            prev.academic_year = ay
            prev.save()
            
            update_classroom = classroom.objects.get(id=prev.id)
            for gl in grade_level:
                update_classroom.grade_level.add(gl)
            return redirect('create_classroom_two', user_id=user_id, class_id=prev.id)
    else:
        user_profile = User.objects.filter(username=request.user.username).first()
        form = classroomForm()
        step = 'One'
    
    page = 'Classrooms'
    return render(request, 'dashboard/create_classroom.html', {'user_profile': user_profile, 'form': form, 'page': page, 'grade_levels': grade_levels})

#Add Subjects to New Classroom 
def CreateClassroomTwo(request, user_id=None, class_id=None):
    user_profile = User.objects.filter(username=request.user.username).first()
    s_user = school_user.objects.filter(user_id=user_profile.id).first()
    ay = academicYear.objects.filter(planning_teacher=user_profile).first()
    class_match = classroom.objects.get(id=class_id)
    grade_levels = gradeLevel.objects.filter(standards_set=s_user.standards_set)
    cs = class_match.subjects.all()
    current_subject = standardSubjects.objects.filter(id__in=cs)
    matched_subject = standardSubjects.objects.filter(standards_set=class_match.standards_set).exclude(id__in=current_subject)

    if request.method == "POST":
        user_profile = User.objects.filter(username=request.user.username).first()
        form = classroomForm(request.POST, request.FILES)

        if form.is_valid():
            prev = form.save(commit=False)
            prev.main_teacher = user_profile
            prev.is_active = True
            prev.standards_set = s_user.standards_set
            prev.academic_year = ay
            prev.save()

            return redirect('create_classroom_two', user_id=user_id, class_id=prev.id)
    else:
        user_profile = User.objects.filter(username=request.user.username).first()
        form = classroomForm()
        step = 'One'
    
    page = 'Classrooms'
    return render(request, 'dashboard/create_classroom.html', {'user_profile': user_profile, 'class_match': class_match, 'form': form, 'page': page, 'grade_levels': grade_levels, 'current_subject': current_subject, 'matched_subject': matched_subject})


#Add New Subject Redirect
def addSubject(request, user_id=None, class_id=None, subject_id=None):
    user_profile = User.objects.get(id=user_id)
    classroom_profile = classroom.objects.get(id=class_id)
    matched_subject = standardSubjects.objects.get(id=subject_id)
    update_classroom = classroom_profile.subjects.add(matched_subject)
    return redirect('{}#subjects'.format(reverse('create_classroom_two', kwargs={'user_id':user_id, 'class_id':class_id})))


#View Single Classroom 
class Classrooms(TemplateView):
    template_name = 'dashboard/classrooms.html' 

    def get(self,request,class_id):
        user_profile = User.objects.filter(username=request.user.username).first()
        class_match = classroom.objects.get(id=class_id)
        cs = class_match.subjects.all()
        current_subject = standardSubjects.objects.filter(id__in=cs)
        matched_subject = standardSubjects.objects.filter(standards_set=class_match.standards_set).exclude(id__in=current_subject)
        if request.method == "POST":
            form = classroomForm(request.POST, request.FILES)

            if form.is_valid():
                prev = form.save(commit=False)
                prev.main_teacher = user_profile
                prev.is_active = True
                prev.save()
            
                return redirect('select_standards', user_id=user_profile.id, class_id=classroom_match, subject=subject, lesson_id=prev.id, select_all=False, topic_id='False')
        else:
            
            form = classroomForm()
        
        return render(request, 'dashboard/classrooms.html', {'user_profile': user_profile, 'class_match': class_match, 'current_subject': current_subject, 'matched_subject': matched_subject})


##################| Build Worksheet Tabs Views |#####################

#?not sure what this view does, will test
class LessonPlanner(TemplateView):
    template_name = 'dashboard/lesson_planner.html' 

#?not sure what this view does, will test
class SubjectPlanner(TemplateView):
    template_name = 'dashboard/subject_planner.html'

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
           
            return redirect('select_standards_two', user_id=user_profile.id, class_id=selected_class, subject=subject, lesson_id=prev.id, select_all=False)
    else:
        form = lessonObjectiveForm()
  



    step = 1
    return render(request, 'dashboard/create_objective_1.html', {'form': form, 'step': step, 'user_profile': user_profile, 'user_classrooms': user_classrooms, 'subjects': subjects  })

#Step Two: Select and Add Relevant Topics 
#create_objective_3.html
def SelectKeywordsTwo(request, user_id=None, class_id=None, subject=None, lesson_id=None, select_all=None):
    #pull in current week and user data
    current_week = date.today().isocalendar()[1] 
    user_profile = User.objects.get(id=user_id)

    # pull in class information 
    classroom_profile = classroom.objects.get(id=class_id)
    
    grade_list = classroom_profile.grade_level.all()
    standard_match = standardSet.objects.get(id=classroom_profile.standards_set_id)

    subject = int(subject)
    current_subject = standardSubjects.objects.get(id=subject)
    
    

    lesson_match = lessonObjective.objects.get(id=lesson_id)
    current_standards = singleStandard.objects.filter(id__in=lesson_match.objectives_standards.all())
    teacher_objective = lesson_match.teacher_objective
    lesson_standards = singleStandard.objects.filter(id__in=lesson_match.objectives_standards.all())
    topic_matches = lesson_match.objectives_topics.all()
    
    matched_topics = match_topics(teacher_objective, class_id, lesson_id)
    text_result = group_topic_texts(lesson_id) #match_textbook_lines(topic_matches, class_id, lesson_id)
    

    split_list = []
    if matched_topics:
        for item in matched_topics:
            item_id = item[0][0]
            if item_id not in split_list:
                split_list.append(item_id)


    topic_lists_one = []
    topic_lists = []
    selected_lists = []
    for item in split_list:
        topic = topicInformation.objects.get(id=item)
        topic_word = topic.item
        topic_descriptions = topic.description.all()
        topic_matches = topicDescription.objects.filter(id__in=topic_descriptions)
        description_lists = []
        for tm in topic_matches:
            wording = tm.description
            description_lists.append(wording)
        
        description_lists = '; '.join([str(i) for i in description_lists])
        check_topics = topicInformation.objects.filter(id__in=split_list).exclude(id=topic.id)
        for item in check_topics:
            check_word = item.item
            Ratio = levenshtein_ratio_and_distance(topic_word,check_word,ratio_calc = True)
            if Ratio > .85:
                for desc in topic_descriptions:
                    item.description.add(desc)   
                    if topic.id in split_list:
                        split_list.remove(topic.id)
            else:
                if lesson_match.objectives_topics.filter(id=topic.id).exists():
                    result = { "id":topic.id, "term":topic.item, "description":description_lists, "is_selected":1 }
                    if result not in selected_lists:
                        selected_lists.append(result)
                else:
                    result = { "id":topic.id, "term":topic.item, "description":description_lists, "is_selected":0 }
                    if result not in topic_lists:
                        topic_lists.append(result)



    select_all = str(select_all)
    if 'True' in select_all:
        for topic in topic_lists:
            if topic[1] == 1:
                pass
            else:
                update_lesson = lesson_match.objectives_topics.add(topic[0])
        return redirect('{}#youtube'.format(reverse('select_standards', kwargs={'user_id':user_profile.id, 'class_id':classroom_profile.id, 'subject':subject, 'lesson_id':lesson_id, 'select_all':False, topic_id:'False'})))
        
  
    if request.method == "POST":
        form = topicInformationForm(request.POST, request.FILES)

        if form.is_valid():
            prev = form.save()
            lesson_match.objectives_demonstration.add(prev)
           
            return redirect('select_standards', user_id=user_profile.id, class_id=classroom_profile.id, subject=subject, lesson_id=prev.id, select_all=False, topic_id='False')
    else:
        form = topicInformationForm()


   
    return render(request, 'dashboard/create_objective_3.html', {'user_profile': user_profile, 'selected_lists': selected_lists, 'topic_lists': topic_lists, 'form': form, 'current_standards': current_standards, 'lesson_match': lesson_match, 'current_week': current_week, 'grade_list': grade_list, 'classroom_profile': classroom_profile })

#Step Three: Select Standards and Add Demo of Knowledge/Skill 
#create_objective_2.html
def SelectStandards(request, user_id=None, class_id=None, subject=None, lesson_id=None, select_all=None, topic_id=None):
    #pull in current week and user data
    current_week = date.today().isocalendar()[1] 
    user_profile = User.objects.get(id=user_id)

    # pull in class information 
    classroom_profile = classroom.objects.get(id=class_id)
    
    grade_list = classroom_profile.grade_level.all()
    standard_match = standardSet.objects.get(id=classroom_profile.standards_set_id)

    subject = int(subject)
    current_subject = standardSubjects.objects.get(id=subject)
    
    

    lesson_match = lessonObjective.objects.get(id=lesson_id)
    current_standards = singleStandard.objects.filter(id__in=lesson_match.objectives_standards.all())
    teacher_objective = lesson_match.teacher_objective
    lesson_standards = singleStandard.objects.filter(id__in=lesson_match.objectives_standards.all())
    topic_matches = lesson_match.objectives_topics.all()
    demo_matches = lesson_match.objectives_demonstration.all()
    selected_demos = LearningDemonstration.objects.filter(id__in=demo_matches)
    recomended_demos = find_ks_demos(class_id, lesson_id)


    if 'False' in topic_id:
        pass
    else:
        topic_id = int(topic_id)
        update_reco_demo = recomended_demos[topic_id]
        if update_reco_demo:
            if user_profile.is_superuser:
                new_demo, create = LearningDemonstration.objects.get_or_create(content=update_reco_demo , created_by=user_profile, topic_id=topic_id, is_admin=True) 
            else:
                new_demo, create = LearningDemonstration.objects.get_or_create(content=update_reco_demo , created_by=user_profile, topic_id=topic_id, is_admin=False) 

        update_lesson = lesson_match.objectives_demonstration.add(new_demo)
    
    recomended_demos = find_ks_demos(class_id, lesson_id)
    random.shuffle(recomended_demos)
    recomendations = lessonStandardRecommendation.objects.filter(lesson_classroom=classroom_profile, objectives=lesson_match)

    if recomendations:
        pass
    else:
        results = match_standard(teacher_objective, current_subject, class_id)
        
        recomendations = []
        for item in results:
            grade = item[0]
            standards = item[1]
            for standard in standards:
                standard_id = standard[0]
                standard_match = singleStandard.objects.filter(id=standard_id).first()
                create_objective, created = lessonStandardRecommendation.objects.get_or_create(lesson_classroom=classroom_profile, objectives=lesson_match, objectives_standard=standard_match)   
                recomendations.append(create_objective)

    if request.method == "POST":
        form = LearningDemonstrationForm(request.POST, request.FILES)

        if form.is_valid():
            prev = form.save()
            lesson_match.objectives_demonstration.add(prev)
           
            return redirect('select_standards', user_id=user_profile.id, class_id=classroom_profile.id, subject=subject, lesson_id=lesson_id, select_all=False, topic_id='False')
    else:
        form = LearningDemonstrationForm()

    return render(request, 'dashboard/create_objective_2.html', {'user_profile': user_profile, 'recomended_demos': recomended_demos, 'form': form, 'selected_demos': selected_demos, 'current_standards': current_standards, 'recomendations': recomendations, 'lesson_match': lesson_match, 'current_week': current_week, 'grade_list': grade_list, 'classroom_profile': classroom_profile })

#Adds or Removes Selected Standards
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
    return redirect('{}#standards'.format(reverse('select_standards', kwargs={'user_id':user_profile.id, 'class_id':classroom_profile.id, 'subject':subject, 'lesson_id':lesson_id, 'select_all':False, 'topic_id':'False'})))




def SelectKeywords(request, user_id=None, class_id=None, subject=None, lesson_id=None):
    current_week = date.today().isocalendar()[1] 
    user_profile = User.objects.get(id=user_id)

    classroom_profile = classroom.objects.get(id=class_id)
    grade_list = classroom_profile.grade_level.all()

    standard_match = standardSet.objects.get(id=classroom_profile.standards_set_id)

    subjects_list = classroom_profile.subjects.all()
    subject_matches = standardSubjects.objects.filter(id__in=subjects_list)
    

    class_objectives = lessonObjective.objects.all().order_by('subject')
    vocab_list = vocabularyList.objects.filter(lesson_plan__in=class_objectives)
    lesson_activities = lessonFull.objects.filter(lesson_overview__in=class_objectives)
    lesson_match = lessonObjective.objects.get(id=lesson_id)
    lesson_standards = singleStandard.objects.filter(id__in=lesson_match.objectives_standards.all())
    teacher_objective = lesson_match.teacher_objective

    subject = lesson_match.subject
    related_question = googleRelatedQuestions.objects.filter(lesson_plan=lesson_match, is_selected=False)
    related_topics = googleSearchResult.objects.filter(lesson_plan=lesson_match, is_selected=False)

    questions_selected = googleRelatedQuestions.objects.filter(lesson_plan=lesson_match, is_selected=True)
    topics_selected = googleSearchResult.objects.filter(lesson_plan=lesson_match, is_selected=True)
    selected_wiki = wikiTopic.objects.filter(lesson_plan=lesson_match, is_selected=True)


    wiki_topics = wikiTopic.objects.filter(lesson_plan=lesson_match).exclude(is_selected=True).order_by('-relevance')
    matched_backgroud_topics = match_topics(teacher_objective, class_id, lesson_id)
    
    wiki_count = selected_wiki.count()
    google_count = topics_selected.count()
    total = wiki_count + google_count
    
    
    youtube_matches = youtube_results(teacher_objective, lesson_id)
    if youtube_matches:
        youtube_list = youtube_matches[:5]
    else:
        youtube_list = []

    vid_id_list = []
    for result in youtube_list:
        try: 
            link = result['link']
            vid_id = video_id(link)
            description = result['description']
            title = result['title']
            youtube_create, created = youtubeSearchResult.objects.get_or_create(lesson_plan=lesson_match, title=title, description=description, vid_id=vid_id)
            vid_id_list.append(youtube_create)
        except:
            pass

    step = 3
    return render(request, 'dashboard/create_objective.html', {'user_profile': user_profile, 'selected_wiki': selected_wiki, 'vid_id_list': vid_id_list, 'questions_selected': questions_selected, 'topics_selected': topics_selected,  'related_question': related_question, 'related_topics': related_topics, 'wiki_topics': wiki_topics, 'step': step, 'lesson_standards': lesson_standards, 'lesson_match': lesson_match, 'lesson_activities': lesson_activities, 'class_objectives': class_objectives, 'current_week': current_week, 'classroom_profile': classroom_profile})

def SelectTopic(request):
    if request.method == 'GET':
        user_profile = User.objects.filter(username=request.user.username).first()
        user_id = user_profile.id
        topic_id = request.GET['topic_id']
        lesson_id = request.GET['lesson_id']
        lesson_match = lessonObjective.objects.get(id=lesson_id)
        topic_match = topicInformation.objects.get(id=topic_id)
        update_lesson = lesson_match.objectives_topics.add(topic_match)

        return HttpResponse("Success")
    else:
        return HttpResponse("Request method is not a GET")



def UpdateTopics(request, lesson_id):

    user_profile = User.objects.filter(username=request.user.username).first()
    user_id = user_profile.id
    lesson_match = lessonObjective.objects.get(id=lesson_id)

    class_id = lesson_match.lesson_classroom_id
    classroom_profile = classroom.objects.get(id=class_id)
    teacher_objective = lesson_match.teacher_objective
    matched_topics = match_topics(teacher_objective, class_id, lesson_id)


    split_list = []
    if matched_topics:
        for item in matched_topics:
            item_id = item[0][0]
            if item_id not in split_list:
                split_list.append(item_id)

    topic_lists_one = []
    topic_lists = []
    selected_lists = []
    for item in split_list:
        topic = topicInformation.objects.get(id=item)
        topic_word = topic.item
        topic_descriptions = topic.description.all()
        topic_matches = topicDescription.objects.filter(id__in=topic_descriptions)
        description_lists = []
        for tm in topic_matches:
            wording = tm.description
            description_lists.append(wording)
        
        description_lists = '; '.join([str(i) for i in description_lists])
        check_topics = topicInformation.objects.filter(id__in=split_list).exclude(id=topic.id)
        for item in check_topics:
            check_word = item.item
            Ratio = levenshtein_ratio_and_distance(topic_word,check_word,ratio_calc = True)
            if Ratio > .85:
                for desc in topic_descriptions:
                    item.description.add(desc)   
                    if topic.id in split_list:
                        split_list.remove(topic.id)
            else:
                if lesson_match.objectives_topics.filter(id=topic.id).exists():
                        result = { "id":topic.id, "term":topic.item, "description":description_lists, "is_selected":1 }
                        if result not in selected_lists:
                            selected_lists.append(result)
                else:
                    result = { "id":topic.id, "term":topic.item, "description":description_lists, "is_selected":0 }
                    if result not in topic_lists:
                        topic_lists.append(result)


    return render(request, "dashboard/create_objective_3.html", {'user_profile': user_profile, 'lesson_match': lesson_match, 'selected_lists': selected_lists, 'topic_lists': topic_lists, 'classroom_profile': classroom_profile})
        

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
        print(topic_match)
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




def ActivityBuilder(request, user_id=None, class_id=None, subject=None, lesson_id=None, page=None):
    current_week = date.today().isocalendar()[1] 
    user_profile = User.objects.get(id=user_id)
    
    classroom_profile = classroom.objects.get(id=class_id)
    grade_list = classroom_profile.grade_level.all()

    standard_match = standardSet.objects.get(id=classroom_profile.standards_set_id)

    subjects_list = classroom_profile.subjects.all()
    subject_matches = standardSubjects.objects.filter(id__in=subjects_list )                                         
    
    
    class_objectives = lessonObjective.objects.all().order_by('subject')


    lesson_match = lessonObjective.objects.get(id=lesson_id)

    lesson_standards = singleStandard.objects.filter(id__in=lesson_match.objectives_standards.all())
    topic_matches = lesson_match.objectives_topics.all()
    topic_lists_selected = topicInformation.objects.filter(id__in=topic_matches).order_by('item')
    topic_count = topic_lists_selected.count()
    chunks = topic_count/3
    one_end = chunks
    two_end = one_end + chunks 
    three_end = two_end + chunks 

    first_topics = topicInformation.objects.filter(id__in=topic_matches).order_by('item')[0:one_end]
    second_topics = topicInformation.objects.filter(id__in=topic_matches).order_by('item')[one_end:two_end]
    third_topics = topicInformation.objects.filter(id__in=topic_matches).order_by('item')[two_end:three_end]

    text_questions = get_question_text(lesson_id)
    match_textlines_one = get_cluster_text(lesson_id,user_id)
    match_textlines = match_textlines_one[0]
    match_topic_text = match_textlines_one[1]


    topic_results = []
    for item in topic_lists_selected:
        topic_results.append(item.id)

    topic_lists_matched = topicInformation.objects.filter(id__in=topic_results).order_by('item')

    if match_textlines: 
        summarize_text = summ_text(match_textlines)
        sent_text = get_statment_sent(match_textlines)
    else:
        summarize_text = []
        sent_text = []

    teacher_objective = lesson_match.teacher_objective
    
    lesson_results = []

    questions_selected = googleRelatedQuestions.objects.filter(lesson_plan=lesson_match, is_selected=True)
    topics_selected = googleSearchResult.objects.filter(lesson_plan=lesson_match, is_selected=True)

    keywords_selected = keywordResults.objects.filter(lesson_plan=lesson_match, is_selected=True).order_by('-relevance')
    keywords_matched = keywordResults.objects.filter(lesson_plan=lesson_match, is_selected=False).order_by('-relevance')
    matched_topics = match_topics(teacher_objective, class_id, lesson_id)
    
    selected_activities = selectedActivity.objects.filter(lesson_overview=lesson_match, is_selected=True)
    print('Selected-Activities', selected_activities)
    not_selected_activities = selectedActivity.objects.filter(lesson_overview=lesson_match, is_selected=False).order_by('template_id')

    text_update = lessonText.objects.filter(matched_lesson=lesson_match).first()
    
    if text_update:
        pass
    else:
        text_update = lessonText.objects.create(matched_lesson=lesson_match)
    
    if text_update.overview:
        classify_text = get_lesson_sections(text_update.overview, class_id, lesson_id, user_id)

    if text_update.activities:
        split_activities = split_matched_activities(text_update.activities, class_id, lesson_id, user_id)

    if text_update.overview:
        split_text = split_matched_text(text_update.overview) 
        split_terms = split_matched_terms(text_update.lesson_terms, class_id, lesson_id) 
        question_list = []
        for line_topic in topic_matches:
            for description_item in line_topic.description.all():
                sentence = line_topic.item + ' - ' + description_item.description
                results = genQuestion(sentence, line_topic.item)
                if results:
                    question_list.append(results)
                else:
                    pass
        text_match = match_lesson_topics(text_update.overview, class_id, lesson_id) 
        
    else:
        split_text = []
        text_match = [] 
        
        question_list = []
    
    if selected_activities:
        lesson_analytics = label_activities_analytics(lesson_id)
    else:
        lesson_analytics = []

    lessons_wording = text_update.activities
    if topic_lists_selected:
        lesson_activities_matched = get_lessons(lesson_id, user_id)
    else:
        lesson_activities_matched = []

    combined = matched_topics, text_match
    topic_lists = []
    if combined:
        for text_lists in combined:
            if text_lists:
                for item in text_lists:

                    topic = topicInformation.objects.get(id=item[0][0])

                    word_term = topic.item
                    word_split = word_term.split()
                    word_count = len(word_split)
                    if lesson_match.objectives_topics.filter(id=topic.id).exists():
                        pass
                    else:
                        result = topic, word_count 
                        if result in topic_lists:
                            pass
                        else:
                            topic_lists.append(result)

    topic_lists.sort(key=lambda x: x[1])

    generated_questions = []

    youtube_matched = youtubeSearchResult.objects.filter(lesson_plan=lesson_match, is_selected=True)
    
    
    if request.method == "POST":

        form = lessonTextForm(request.POST, request.FILES, instance=text_update)

        if form.is_valid():
            
            prev = form.save()
            prev.is_initial = False
            prev.matched_lesson = lesson_match
            prev.save()
            return redirect('{}#keywords'.format(reverse('activity_builder', kwargs={'user_id':user_profile.id, 'class_id':classroom_profile.id, 'subject':subject, 'lesson_id':lesson_id, 'page': 0})))
    else:

        form = lessonTextForm(instance=text_update)

    page = int(page)
    return render(request, 'dashboard/activity_builder.html', {'user_profile': user_profile, 'page': page, 'match_topic_text': match_topic_text, 'form': form, 'summarize_text': summarize_text, 'lesson_analytics': lesson_analytics, 'generated_questions': generated_questions, 'first_topics': first_topics, 'second_topics': second_topics, 'third_topics': third_topics, 'topic_lists_matched': topic_lists_matched, 'sent_text': sent_text,  'match_textlines': match_textlines, 'text_questions': text_questions, 'selected_activities': selected_activities, 'not_selected_activities':not_selected_activities, 'question_list': question_list, 'lessons_wording': lessons_wording, 'text_update': text_update, 'lesson_results': lesson_results, 'topic_lists_selected': topic_lists_selected, 'topic_lists': topic_lists, 'keywords_selected': keywords_selected, 'youtube_matched': youtube_matched, 'questions_selected': questions_selected, 'topics_selected': topics_selected, 'keywords_matched': keywords_matched, 'lesson_standards': lesson_standards, 'lesson_match': lesson_match, 'class_objectives': class_objectives, 'current_week': current_week, 'classroom_profile': classroom_profile})




def DigitalActivities(request, user_id=None, class_id=None, subject=None, lesson_id=None, worksheet_id=None, page=None, act_id=None, question_id=None):
    current_week = date.today().isocalendar()[1] 
    user_profile = User.objects.get(id=user_id)

    classroom_profile = classroom.objects.get(id=class_id)
    grade_list = classroom_profile.grade_level.all()
    grade_match = gradeLevel.objects.filter(id__in=grade_list).first()
    standard_match = standardSet.objects.get(id=classroom_profile.standards_set_id)

    
    worksheet_title = '%s: %s for week of %s' % (user_profile, classroom_profile, current_week) 
    get_worksheet, created = worksheetFull.objects.get_or_create(created_by=user_profile, title=worksheet_title)
    class_objectives = lessonObjective.objects.all().order_by('subject')
    vocab_list = vocabularyList.objects.filter(lesson_plan__in=class_objectives)
    lesson_activities = lessonFull.objects.filter(lesson_overview__in=class_objectives)
    lesson_match = lessonObjective.objects.get(id=lesson_id)
    subject_match = lesson_match.subject_id
    subject_match_full = standardSubjects.objects.get(id=subject_match) 
    question_match = match_lesson_questions(lesson_match.teacher_objective, class_id, lesson_id)
    lesson_standards = singleStandard.objects.filter(id__in=lesson_match.objectives_standards.all())
    topic_matches = lesson_match.objectives_topics.all()
    topic_lists_selected = topicInformation.objects.filter(id__in=topic_matches).order_by('item')
    topic_count = topic_lists_selected.count()
    chunks = topic_count/3
    one_end = chunks
    two_end = one_end + chunks 
    three_end = two_end + chunks 

    first_topics = topicInformation.objects.filter(id__in=topic_matches).order_by('item')[0:one_end]
    second_topics = topicInformation.objects.filter(id__in=topic_matches).order_by('item')[one_end:two_end]
    third_topics = topicInformation.objects.filter(id__in=topic_matches).order_by('item')[two_end:three_end]
    uploaded_images = lessonPDFImage.objects.filter(matched_lesson=lesson_match)

    uploaded_text = lessonPDFText.objects.filter(matched_lesson=lesson_match)

    text_questions_one = get_question_text(lesson_id)

    quest_match, created = questionType.objects.get_or_create(item='short_answer')
    text_questions = []
    for quest in text_questions_one:
        get_question, created = topicQuestion.objects.get_or_create(subject=subject_match_full, is_admin = False, grade_level=grade_match, Question=quest, question_type=quest_match, standard_set= standard_match, created_by=user_profile)
        text_questions.append(get_question)

    match_textlines_one = get_cluster_text(lesson_id,user_id)
    match_textlines = match_textlines_one[0]
    match_topic_text = match_textlines_one[1]

    topic_results = []
    for item in topic_lists_selected:

        topic_results.append(item.id)

    topic_lists_matched = topicInformation.objects.filter(id__in=topic_results).order_by('item')

    if match_textlines: 
        summarize_text = summ_text(match_textlines)
        sent_text = get_statment_sent(match_textlines)
    else:
        summarize_text = []
        sent_text = []

    teacher_objective = lesson_match.teacher_objective
    
    lesson_results = []

    questions_selected = googleRelatedQuestions.objects.filter(lesson_plan=lesson_match, is_selected=True)
    topics_selected = googleSearchResult.objects.filter(lesson_plan=lesson_match, is_selected=True)

    keywords_selected = keywordResults.objects.filter(lesson_plan=lesson_match, is_selected=True).order_by('-relevance')
    keywords_matched = keywordResults.objects.filter(lesson_plan=lesson_match, is_selected=False).order_by('-relevance')
    matched_topics = match_topics(teacher_objective, class_id, lesson_id)
    
    text_update, created = lessonText.objects.get_or_create(matched_lesson=lesson_match)
    lessons_wording = text_update.activities
    lesson_activities_matched = get_lessons(lesson_id, user_id)
    
    selected_activities = selectedActivity.objects.filter(lesson_overview=lesson_match, is_selected=True)
    not_selected_activities = selectedActivity.objects.filter(lesson_overview=lesson_match, is_selected=False).order_by('bloom')

    if selected_activities:
        lesson_analytics = label_activities_analytics(lesson_id)
    else:
        lesson_analytics = []


    if text_update.activities:
        split_activities = split_matched_activities(text_update.activities, class_id, lesson_id, user_id)

    if text_update.overview:
        split_text = split_matched_text(text_update.overview) 
        split_terms = split_matched_terms(text_update.lesson_terms, class_id, lesson_id) 
        question_list = []
        for line_topic in topic_matches:
            for description_item in line_topic.description.all():
                sentence = line_topic.item + ' - ' + description_item.description
                results = genQuestion(sentence, line_topic.item)
                if results:
                    question_list.append(results)
                else:
                    pass
        text_match = match_lesson_topics(text_update.overview, class_id, lesson_id) 
        if text_match:
            pass 
        else:
            text_match = []
    else:
        split_text = []
        text_match = [] 
        
        question_list = []
    
   
    question_lists = []
    if question_match:
        for item in question_match:
            result_id = item[0][0]
            topic = topicQuestion.objects.get(id=result_id)
            topic_question = topic.Question
            question_type = topic.question_type_id
            type_match = questionType.objects.get(id=question_type)
            type_name = type_match.item
            if 'multi_choice' in type_name: 
                if topicQuestion.objects.filter(original_num=result_id, created_by=user_profile).exists():
                    topic = topicQuestion.objects.filter(original_num=result_id, created_by=user_profile).first()
                else:
                    topic.pk = None 
                    topic.id = None 
                    topic.is_admin = False
                    topic.created_by = user_profile
                    topic.original_num = result_id
                    topic.save()
                question_lists.append(topic)

    combined = text_match + matched_topics 

    topic_lists = []
    if combined:
        for text_lists in combined:

            topic_id = text_lists[0][0]

            topic = topicInformation.objects.get(id=topic_id)

            word_term = topic.item
            word_split = word_term.split()
            word_count = len(word_split)
            if lesson_match.objectives_topics.filter(id=topic.id).exists():
                pass
            else:
                result = topic, word_count 
                if result in topic_lists:
                    pass
                else:
                    topic_lists.append(result)

    topic_lists.sort(key=lambda x: x[1])

    generated_questions = []
    if topic_lists_matched:
        generated_questions_one = generate_questions_topic(topic_lists_matched)

        quest_match, created = questionType.objects.get_or_create(item='fill_in_blank')
        for quest in generated_questions_one:
            one = quest[0]
            two = quest[1]
            three = quest[2]
            
            if three:
                sentence = '%s - %s' % (three, one)
            else:
                sentence = str(one)
            get_question, created = topicQuestion.objects.get_or_create(subject=subject_match_full, is_admin = False, grade_level=grade_match, Question=sentence, Correct=two, question_type=quest_match, standard_set= standard_match, created_by=user_profile)
            generated_questions.append(get_question)


    youtube_matched = youtubeSearchResult.objects.filter(lesson_plan=lesson_match, is_selected=True)
    
    activity_choices = []


    
    worksheet_id = int(worksheet_id)

    if worksheet_id == 0:
        all_questions = list(chain(text_questions, generated_questions, question_lists))
        random.shuffle(all_questions)
        worksheet_preview_one = all_questions[:10]
        matched_worksheet, created = worksheetFull.objects.get_or_create(created_by=user_profile, title=worksheet_title)
        if created:
            for quest in worksheet_preview_one:
                if matched_worksheet.questions.filter(id=quest.id).exists():
                    pass
                else:
                    update_worksheet = matched_worksheet.questions.add(quest)
        else:
            for quest in worksheet_preview_one:
                if matched_worksheet.questions.filter(id=quest.id).exists():
                    pass
                else:
                    update_worksheet = matched_worksheet.questions.add(quest)

            matched_questions = matched_worksheet.questions.all()
        
        all_questions = topicQuestion.objects.filter(id__in=matched_questions)
        worksheet_id = matched_worksheet.id
        
        
    else:
        matched_worksheet = worksheetFull.objects.get(id=worksheet_id)
        matched_questions = matched_worksheet.questions.all()
        all_questions = topicQuestion.objects.filter(id__in=matched_questions)
        worksheet_id = matched_worksheet.id

    worksheet_preview = all_questions[:10]
    
    worksheet_id = matched_worksheet.id

    question_id = int(question_id)
    if question_id == 0:
        
        if request.method == "POST":
   
            form = topicQuestionForm(request.POST, request.FILES)
            form2 = lessonPDFTextForm(request.POST, request.FILES)

            if form2.is_valid():
          
                prev = form2.save()
                
                get_text_image = build_textbook(prev.id, user_id, class_id, lesson_id, current_week)

                return redirect('{}#keywords'.format(reverse('lesson_pdf_upload', kwargs={'user_id':user_id, 'class_id':class_id, 'lesson_id':lesson_id, 'subject':subject})))

            if form.is_valid():
                topicQuestion.objects.get_or_create(subject=subject_match_full, is_admin = False, grade_level=grade_match, Question=sentence, Correct=two, question_type=quest_match, standard_set= standard_match, created_by=user_profile)
                prev = form.save()

                return redirect('{}#keywords'.format(reverse('digital_activities', kwargs={'user_id':user_id, 'class_id':class_id, 'lesson_id':lesson_id, 'subject':subject, 'page':'Current', 'worksheet_id':matched_worksheet.id, 'act_id':0, 'question_id':0})))
        else:
            form = topicQuestionForm()
            data = {'matched_lesson': lesson_match}
            form2 = lessonPDFTextForm(initial=data)
            form2.fields["matched_lesson"].queryset = lessonObjective.objects.filter(id=lesson_id)
    else:
        question_match = topicQuestion.objects.get(id=question_id)

        worksheet_id = int(worksheet_id)
        if request.method == "POST":
   
            form = topicQuestionForm(request.POST, request.FILES, instance=question_match)
            form2 = lessonPDFTextForm(request.POST, request.FILES,)

            if form2.is_valid():
                prev = form2.save()
                
                get_text_image = build_textbook(prev.id, user_id, class_id, lesson_id, current_week)

                return redirect('{}#keywords'.format(reverse('lesson_pdf_upload', kwargs={'user_id':user_id, 'class_id':class_id, 'lesson_id':lesson_id, 'subject':subject})))
        
            if form.is_valid():
                topicQuestion.objects.get_or_create(subject=subject_match_full, is_admin = False, grade_level=grade_match, Question=sentence, Correct=two, question_type=quest_match, standard_set= standard_match, created_by=user_profile)
                prev = form.save()

                return redirect('{}#keywords'.format(reverse('digital_activities', kwargs={'user_id':user_id, 'class_id':class_id, 'lesson_id':lesson_id, 'subject':subject, 'page':'Current', 'worksheet_id':matched_worksheet.id, 'act_id':0, 'question_id':0})))
        else:
            form = topicQuestionForm(instance=question_match)
            data = {'matched_lesson': lesson_match}
            form2 = lessonPDFTextForm(initial=data)
            form2.fields["matched_lesson"].queryset = lessonObjective.objects.filter(id=lesson_id)

    return render(request, 'dashboard/activity_builder_2.html', {'user_profile': user_profile, 'worksheet_preview': worksheet_preview, 'page': page, 'form': form, 'form2': form2, 'question_match': question_match, 'worksheet_id': worksheet_id, 'match_topic_text': match_topic_text, 'subject_match_full': subject_match_full, 'matched_worksheet': matched_worksheet, 'activity_choices': activity_choices, 'lesson_analytics': lesson_analytics, 'generated_questions': generated_questions, 'first_topics': first_topics, 'second_topics': second_topics, 'third_topics': third_topics, 'topic_lists_matched': topic_lists_matched, 'sent_text': sent_text,  'match_textlines': match_textlines, 'text_questions': text_questions, 'selected_activities': selected_activities, 'not_selected_activities':not_selected_activities, 'question_list': question_list, 'lessons_wording': lessons_wording, 'question_lists': question_lists, 'text_update': text_update, 'lesson_results': lesson_results, 'topic_lists_selected': topic_lists_selected, 'topic_lists': topic_lists, 'keywords_selected': keywords_selected, 'youtube_matched': youtube_matched, 'questions_selected': questions_selected, 'topics_selected': topics_selected, 'keywords_matched': keywords_matched, 'lesson_standards': lesson_standards, 'lesson_match': lesson_match, 'lesson_activities': lesson_activities, 'class_objectives': class_objectives, 'current_week': current_week, 'classroom_profile': classroom_profile})



def WorksheetBuilder(request, user_id=None, class_id=None, subject=None, lesson_id=None, worksheet_id=None):
    #second step to the standards upload process
    #name="standards_upload"
    matched_lesson = lessonObjective.objects.get(id=lesson_id)
    user_profile = User.objects.filter(username=request.user.username).first()
    matched_worksheet = worksheetFull.objects.get(id=worksheet_id)

    return render(request, 'dashboard/create_worksheet.html', {'user_profile': user_profile, 'matched_worksheet': matched_worksheet})


def CopyPasteLesson(request, user_id=None, class_id=None, subject=None, lesson_id=None):
    #second step to the standards upload process
    #name="standards_upload"
    matched_lesson = lessonObjective.objects.get(id=lesson_id)
    user_profile = User.objects.filter(username=request.user.username).first()

    if request.method == "POST":
        
        form = lessonPDFTextForm(request.POST, request.FILES,)
        if form.is_valid():
            
            prev = form.save()
            get_text_image = pdf_pull_text(prev.id)
            content = get_text_image

            update_text = lessonPDFText.objects.get(id=prev.id)
            update_text.content = content
            update_text.save()
            pdf_image = update_text.pdf_doc.url
            
            pull_images = pdf_pull_images(prev.id, lesson_id, update_text.id)
            return redirect('{}#keywords'.format(reverse('activity_builder', kwargs={'user_id':user_profile.id, 'class_id':class_id, 'subject':subject, 'lesson_id':lesson_id, 'page': 0})))
    else:
        data = {'matched_lesson': matched_lesson}
        form = lessonPDFTextForm(initial=data)
        form.fields["matched_lesson"].queryset = lessonObjective.objects.filter(id=lesson_id)
    return render(request, 'dashboard/lesson_image_upload.html', {'user_profile': user_profile, 'form': form})


def LessonImageUpload(request, user_id=None, class_id=None, subject=None, lesson_id=None):
    #second step to the standards upload process
    #name="standards_upload"
    matched_lesson = lessonObjective.objects.get(id=lesson_id)
    user_profile = User.objects.filter(username=request.user.username).first()

    if request.method == "POST":
        form = lessonImageUploadForm(request.POST, request.FILES,)
        if form.is_valid():
            prev = form.save()
            image = prev.image_image.url
            get_text_image = pdf_core(prev.id)
            content = get_text_image

            update_text = lessonImageUpload.objects.get(id=prev.id)
            update_text.content = content
            update_text.save()
            return redirect('{}#keywords'.format(reverse('activity_builder', kwargs={'user_id':user_profile.id, 'class_id':class_id, 'subject':subject, 'lesson_id':lesson_id, 'page': 0})))
    else:
        data = {'matched_lesson': matched_lesson}
        form = lessonImageUploadForm(initial=data)
        form.fields["matched_lesson"].queryset = lessonObjective.objects.filter(id=lesson_id)
    return render(request, 'dashboard/lesson_image_upload.html', {'user_profile': user_profile, 'form': form})


def LessonPDFUpload(request, user_id=None, class_id=None, subject=None, lesson_id=None):
    #second step to the standards upload process
    #name="standards_upload"
    current_week = date.today().isocalendar()[1] 
    matched_lesson = lessonObjective.objects.get(id=lesson_id)
    user_profile = User.objects.filter(username=request.user.username).first()
    macthed_textbooks = textBookTitle.objects.filter(uploaded_by=user_profile, lesson_id_num=lesson_id)
    matched_lines = textBookBackground.objects.filter(textbook__in=macthed_textbooks)
    matched_questions = build_questions(matched_lines)
    return render(request, 'dashboard/lesson_image_upload.html', {'user_profile': user_profile, 'matched_lines': matched_lines})


def PracticeTest(request, user_id=None, class_id=None, subject=None, lesson_id=None):
    current_week = date.today().isocalendar()[1] 
    user_profile = User.objects.get(id=user_id)

    classroom_profile = classroom.objects.get(id=class_id)
    grade_list = classroom_profile.grade_level.all()

    standard_match = standardSet.objects.get(id=classroom_profile.standards_set_id)

    subjects_list = classroom_profile.subjects.all()
    subject_matches = standardSubjects.objects.filter(id__in=subjects_list )                                         
    
    
    class_objectives = lessonObjective.objects.all().order_by('subject')
    vocab_list = vocabularyList.objects.filter(lesson_plan__in=class_objectives)
    lesson_activities = lessonFull.objects.filter(lesson_overview__in=class_objectives)
    lesson_match = lessonObjective.objects.get(id=lesson_id)
    question_match = match_lesson_questions(lesson_match.teacher_objective, class_id, lesson_id)
    lesson_standards = singleStandard.objects.filter(id__in=lesson_match.objectives_standards.all())
    topic_matches = lesson_match.objectives_topics.all()
    topic_lists_selected = topicInformation.objects.filter(id__in=topic_matches).order_by('item')
    topic_count = topic_lists_selected.count()
    chunks = topic_count/3
    one_end = chunks
    two_end = one_end + chunks 
    three_end = two_end + chunks 

    first_topics = topicInformation.objects.filter(id__in=topic_matches).order_by('item')[0:one_end]
    second_topics = topicInformation.objects.filter(id__in=topic_matches).order_by('item')[one_end:two_end]
    third_topics = topicInformation.objects.filter(id__in=topic_matches).order_by('item')[two_end:three_end]

    text_questions = get_question_text(lesson_id)
    
    text_questions_two_full = get_cluster_text(lesson_id,user_id)
    if text_questions_two_full:
        match_textlines = text_questions_two_full[0]
        topics_selected = text_questions_two_full[1]
        topic_match = text_questions_two_full[2]
    else:
        match_textlines = []
        topics_selected = []
        topic_match = []

    topic_results = []
    for item in topic_match:
        for y in item[2]:
            topic_results.append(y.id)

    topic_lists_matched = topicInformation.objects.filter(id__in=topic_results).order_by('item')

    if match_textlines: 
        summarize_text = summ_text(match_textlines)
        sent_text = get_statment_sent(match_textlines)
    else:
        summarize_text = []
        sent_text = []

    teacher_objective = lesson_match.teacher_objective
    
    lesson_results = []

    questions_selected = googleRelatedQuestions.objects.filter(lesson_plan=lesson_match, is_selected=True)
    topics_selected = googleSearchResult.objects.filter(lesson_plan=lesson_match, is_selected=True)

    keywords_selected = keywordResults.objects.filter(lesson_plan=lesson_match, is_selected=True).order_by('-relevance')
    keywords_matched = keywordResults.objects.filter(lesson_plan=lesson_match, is_selected=False).order_by('-relevance')
    matched_topics = match_topics(teacher_objective, class_id, lesson_id)
    
    text_update, created = lessonText.objects.get_or_create(matched_lesson=lesson_match)
    lessons_wording = text_update.activities
    lesson_activities_matched = get_lessons(lesson_id, user_id)
    
    selected_activities = selectedActivity.objects.filter(lesson_overview=lesson_match, is_selected=True)
    not_selected_activities = selectedActivity.objects.filter(lesson_overview=lesson_match, is_selected=False).order_by('bloom')

    if text_update.activities:
        split_activities = split_matched_activities(text_update.activities, class_id, lesson_id, user_id)

    if text_update.overview:
        split_text = split_matched_text(text_update.overview) 
        split_terms = split_matched_terms(text_update.lesson_terms, class_id, lesson_id) 
        question_list = []
        for line_topic in topic_matches:
            for description_item in line_topic.description.all():
                sentence = line_topic.item + ' - ' + description_item.description
                results = genQuestion(sentence, line_topic.item)
                if results:
                    question_list.append(results)
                else:
                    pass
        text_match = match_lesson_topics(text_update.overview, class_id, lesson_id) 
        
    else:
        split_text = []
        text_match = [] 
        
        question_list = []
    
    
    question_lists = []
    if question_match:
        for item in question_match:
            result_id = item[0][0]
            topic = topicQuestion.objects.get(id=result_id)
    
            question_lists.append(topic )
    
    if question_match:
        pass
    else:
        question_match = []

    combined = matched_topics, text_match
    topic_lists = []
    if combined:
        for text_lists in combined:
            if text_lists:
                for item in text_lists:

                    topic = topicInformation.objects.get(id=item[0][0])

                    word_term = topic.item
                    word_split = word_term.split()
                    word_count = len(word_split)
                    if lesson_match.objectives_topics.filter(id=topic.id).exists():
                        pass
                    else:
                        result = topic, word_count 
                        if result in topic_lists:
                            pass
                        else:
                            topic_lists.append(result)

    topic_lists.sort(key=lambda x: x[1])

    if topic_lists_matched:
        generated_questions = []
        for item in topic_lists_matched:
            generated_quest = generate_questions_topic(item.id)
            if generated_quest:
                generated_questions.append(generated_quest[0])
    else:
        generated_questions = []

    youtube_matched = youtubeSearchResult.objects.filter(lesson_plan=lesson_match, is_selected=True)
    

    
    step = 4

    return render(request, 'dashboard/practice_test.html', {'user_profile': user_profile, 'generated_questions': generated_questions, 'question_lists': question_lists,  'first_topics': first_topics, 'second_topics': second_topics, 'third_topics': third_topics, 'topic_lists_matched': topic_lists_matched, 'sent_text': sent_text,  'topic_match': topic_match, 'match_textlines': match_textlines, 'text_questions': text_questions, 'selected_activities': selected_activities, 'not_selected_activities':not_selected_activities, 'question_list': question_list, 'lessons_wording': lessons_wording, 'question_lists': question_lists, 'text_update': text_update, 'lesson_results': lesson_results, 'topic_lists_selected': topic_lists_selected, 'topic_lists': topic_lists, 'keywords_selected': keywords_selected, 'youtube_matched': youtube_matched, 'questions_selected': questions_selected, 'topics_selected': topics_selected, 'keywords_matched': keywords_matched, 'step': step, 'lesson_standards': lesson_standards, 'lesson_match': lesson_match, 'lesson_activities': lesson_activities, 'class_objectives': class_objectives, 'current_week': current_week, 'classroom_profile': classroom_profile})



def CreateActivity(request, user_id=None, class_id=None, subject=None, lesson_id=None):
    current_week = date.today().isocalendar()[1] 
    user_profile = User.objects.get(id=user_id)

    classroom_profile = classroom.objects.get(id=class_id)
    grade_list = classroom_profile.grade_level.all()

    standard_match = standardSet.objects.get(id=classroom_profile.standards_set_id)
    classroom_subjects = classroom_profile.subjects.all()
    subject_matches = standardSubjects.objects.filter(id__in=classroom_subjects)                                         
    
    lesson_match = lessonObjective.objects.get(id=lesson_id)
    lesson_standards = singleStandard.objects.filter(id__in=lesson_match.objectives_standards.all())
    topic_matches = lesson_match.objectives_topics.all()
    topic_lists_selected = topicInformation.objects.filter(id__in=topic_matches).order_by('item')
    topic_count = topic_lists_selected.count()
    chunks = topic_count/3
    one_end = chunks
    two_end = one_end + chunks 
    three_end = two_end + chunks 

    first_topics = topicInformation.objects.filter(id__in=topic_matches).order_by('item')[0:one_end]
    second_topics = topicInformation.objects.filter(id__in=topic_matches).order_by('item')[one_end:two_end]
    third_topics = topicInformation.objects.filter(id__in=topic_matches).order_by('item')[two_end:three_end]

    text_questions = get_question_text(lesson_id)
    text_questions_two_full = get_cluster_text(lesson_id,user_id)
    if text_questions_two_full:
        match_textlines = text_questions_two_full[0]
        topics_selected = text_questions_two_full[1]
        topic_match = text_questions_two_full[2]

        topic_results = []
        for item in topic_match:
            for y in item:
                topic_results.append(y.id)

        topic_lists_matched = topicInformation.objects.filter(id__in=topic_results).order_by('item')

        summarize_text = summ_text(match_textlines)
        sent_text = get_statment_sent(match_textlines)
    else:
        topic_lists_matched = []
        sent_text = []
        topic_match = []
        match_textlines = []

    teacher_objective = lesson_match.teacher_objective
    
    lesson_results = []

    questions_selected = googleRelatedQuestions.objects.filter(lesson_plan=lesson_match, is_selected=True)
    topics_selected = googleSearchResult.objects.filter(lesson_plan=lesson_match, is_selected=True)

    keywords_selected = keywordResults.objects.filter(lesson_plan=lesson_match, is_selected=True).order_by('-relevance')
    keywords_matched = keywordResults.objects.filter(lesson_plan=lesson_match, is_selected=False).order_by('-relevance')
    matched_topics = match_topics(teacher_objective, class_id, lesson_id)
    
    text_update, created = lessonText.objects.get_or_create(matched_lesson=lesson_match)
    lessons_wording = text_update.activities
    lesson_activities_matched = get_lessons(lesson_id, user_id)
    
    selected_activities = selectedActivity.objects.filter(lesson_overview=lesson_match, is_selected=True)
    not_selected_activities = selectedActivity.objects.filter(lesson_overview=lesson_match, is_selected=False).order_by('bloom')

    if text_update.activities:
        split_activities = split_matched_activities(text_update.activities, class_id, lesson_id, user_id)

    if text_update.overview:
        split_text = split_matched_text(text_update.overview) 
        split_terms = split_matched_terms(text_update.lesson_terms, class_id, lesson_id) 
        question_list = []
        for line_topic in topic_matches:
            for description_item in line_topic.description.all():
                sentence = line_topic.item + ' - ' + description_item.description
                results = genQuestion(sentence, line_topic.item)
                if results:
                    question_list.append(results)
                else:
                    pass
        text_match = match_lesson_topics(text_update.overview, class_id, lesson_id) 
        question_match = match_lesson_questions(text_update.overview, class_id, lesson_id)
    else:
        split_text = []
        text_match = [] 
        question_match = []
        question_list = []
    
    
    question_lists = []
    if question_match:
        for item in question_match:
            topic = topicQuestion.objects.get(id=item[0])
    
            question_lists.append(topic )
    

    combined = matched_topics, text_match
    topic_lists = []
    if combined:
        for text_lists in combined:
            if text_lists:
                for item in text_lists:

                    topic = topicInformation.objects.get(id=item[0][0])

                    word_term = topic.item
                    word_split = word_term.split()
                    word_count = len(word_split)
                    if lesson_match.objectives_topics.filter(id=topic.id).exists():
                        pass
                    else:
                        result = topic, word_count 
                        if result in topic_lists:
                            pass
                        else:
                            topic_lists.append(result)

    topic_lists.sort(key=lambda x: x[1])

    youtube_matched = youtubeSearchResult.objects.filter(lesson_plan=lesson_match, is_selected=True)
    
    if request.method == "POST":
        form = selectedActivityForm(request.POST, request.FILES)

        if form.is_valid():
            prev = form.save(commit=False)
            prev.created_by = user_profile
            prev.lesson_overview = lesson_match
            activity = prev.lesson_text
            matches = label_activities(activity)
            labels = matches[0]
            work = matches[1]
            prev.bloom = labels[1]
            prev.mi = labels[0]
            prev.verb = labels[2]
            prev.is_selected = True
            prev.work_product = work
            prev.save()
        return redirect('{}#keywords'.format(reverse('activity_builder', kwargs={'user_id':user_profile.id, 'class_id':classroom_profile.id, 'subject':subject, 'lesson_id':lesson_id, 'page': 0})))
    else:
        form = selectedActivityForm()
    
  
    step = 4
    return render(request, 'dashboard/add_activity.html', {'user_profile': user_profile, 'form': form, 'first_topics': first_topics, 'second_topics': second_topics, 'third_topics': third_topics, 'topic_lists_matched': topic_lists_matched, 'sent_text': sent_text,  'topic_match': topic_match, 'match_textlines': match_textlines, 'text_questions': text_questions, 'selected_activities': selected_activities, 'not_selected_activities':not_selected_activities, 'question_list': question_list, 'lessons_wording': lessons_wording, 'question_lists': question_lists, 'text_update': text_update, 'lesson_results': lesson_results, 'topic_lists_selected': topic_lists_selected, 'topic_lists': topic_lists, 'keywords_selected': keywords_selected, 'youtube_matched': youtube_matched, 'questions_selected': questions_selected, 'topics_selected': topics_selected, 'keywords_matched': keywords_matched, 'step': step, 'lesson_standards': lesson_standards, 'lesson_match': lesson_match, 'current_week': current_week, 'classroom_profile': classroom_profile})



def StandardUploadTwo(request):
    #second step to the standards upload process
    #name="standards_upload"
    template = "administrator/upload_textbook.html"

    prompt = {
        'order': 'Order of the CSV should be first name, surname'   
              }
    # GET request returns the value of the data with the specified key.
    if request.method == "GET":
        return render(request, template, prompt)
    csv_file = request.FILES['file']
    # let's check if it is a csv file
    if not csv_file.name.endswith('.csv'):
        messages.error(request, 'THIS IS NOT A CSV FILE')
    data_set = csv_file.read().decode('UTF-8')
    # setup a stream which is when we loop through each line we are able to handle a data in a stream
    io_string = io.StringIO(data_set)
    next(io_string)
    for line in csv.reader(io_string, delimiter=','):
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

    context = { }
    return render(request, template, context)


def TextbookUploadOne(request):
    #second step to the standards upload process
    #name="standards_upload"

    user_profile = User.objects.filter(username=request.user.username).first()

    if request.method == "POST":
        form = textBookTitleForm(request.POST)
        if form.is_valid():
            prev = form.save()
            return redirect('textbook_uplad_two', textbook_id=prev.id)
    else:
        form = textBookTitleForm()
    return render(request, 'administrator/upload_textbook.html', {'form': form })


def TextbookUploadTwo(request, textbook_id=None):
    #second step to the standards upload process
    #name="standards_upload"
    template = "administrator/upload_textbook.html"
    textbook_match = textBookTitle.objects.get(id=textbook_id)

    prompt = {
        'order': 'Order of the CSV should be first name, surname'   
              }
    # GET request returns the value of the data with the specified key.
    if request.method == "GET":
        return render(request, template, prompt)
    csv_file = request.FILES['file']
    # let's check if it is a csv file
    if not csv_file.name.endswith('.csv'):
        messages.error(request, 'THIS IS NOT A CSV FILE')
    data_set = csv_file.read().decode('UTF-8')
    # setup a stream which is when we loop through each line we are able to handle a data in a stream
    io_string = io.StringIO(data_set)
    next(io_string)

    text_id = textbook_match.id

    for line in csv.reader(io_string, delimiter=','):
        get_lemma = stemSentence(line[0])
        obj, created = textBookBackground.objects.get_or_create(textbook=textbook_match, line_text=line[0], line_lemma=get_lemma)
        obj.line_counter = int(str(text_id) + str(obj.id)) 
        obj.save()

    update_matches = match_topic_texts(textbook_match.subject, text_id)
    context = {'step': True}
    return render(request, template, context)

def TopicUploadOne(request):
    #second step to the standards upload process
    #name="standards_upload"
    user_profile = User.objects.filter(username=request.user.username).first()

    path3 = 'planit/files/Math_8 - Topics (1).csv'
    with open(path3) as f:
        for line in f:
            line = line.split(',') 
            Subject = line[0]
            Grade_Level = line[1]
            Standard_Set = line[2]
            topic = line[3].title()
            item = line[4].title()
            Description = line[5]
            topic_type = line[6]
            image_name = line[7]
            
           
            standard_match = standardSet.objects.filter(Location=Standard_Set).first()
            matched_grade = gradeLevel.objects.filter(grade=Grade_Level, standards_set=standard_match).first()
            matched_subject = standardSubjects.objects.filter(subject_title=Subject, standards_set=standard_match, grade_level=matched_grade).first()

            topic_match, created = topicTypes.objects.get_or_create(item=topic_type)
            new_topic, created = topicInformation.objects.get_or_create(subject=matched_subject, grade_level=matched_grade, standard_set=standard_match, topic=topic, item=item, description=Description, image_name=image_name)

            add_topic = new_topic.topic_type.add(topic_match)
            
        
    return redirect('Dashboard', week_of='Current')
    
def TopicUploadTwo(request):
    #second step to the standards upload process
    #name="standards_upload"
    template = "administrator/upload_textbook.html"


    prompt = {
        'order': 'Order of the CSV should be first name, surname'   
              }
    # GET request returns the value of the data with the specified key.
    if request.method == "GET":
        return render(request, template, prompt)
    csv_file = request.FILES['file']
    # let's check if it is a csv file
    if not csv_file.name.endswith('.csv'):
        messages.error(request, 'THIS IS NOT A CSV FILE')
    data_set = csv_file.read().decode('UTF-8')
    # setup a stream which is when we loop through each line we are able to handle a data in a stream
    io_string = io.StringIO(data_set)
    next(io_string)

    for line in csv.reader(io_string, delimiter=','):
        Subject = line[0]
        Grade_Level = line[1]
        Standard_Set = line[2]
        topic = line[3]
        item = line[4]
        Description = line[5]
        topic_type = line[6]
        image_name = line[7]
        
        standard_match = standardSet.objects.filter(Location=Standard_Set).first()
        matched_grade = gradeLevel.objects.filter(grade=Grade_Level, standards_set=standard_match).first()
        matched_subject = standardSubjects.objects.filter(subject_title=Subject, standards_set=standard_match, grade_level=matched_grade).first()
        topic_match, created = topicTypes.objects.get_or_create(item=topic_type)
        new_topic, created = topicInformation.objects.get_or_create(subject=matched_subject, grade_level=matched_grade, standard_set=standard_match, topic=topic, item=item, image_name=image_name)
        new_description, created =  topicDescription.objects.get_or_create(description=Description) 
        add_description = new_topic.description.add(new_description)
        add_topic = new_topic.topic_type.add(topic_match)

    context = {'step': True}
    return render(request, template, context)




def generate_studyguide_pdf(request):

    people = 'Audrey'

    # Rendered
    html_string = render_to_string('dashboard/pdf.html', {'people': people})
    html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
    result = html.write_pdf()

     # Creating http response
    response = HttpResponse(content_type='application/pdf;')
    response['Content-Disposition'] = 'inline; filename=list_people.pdf'
    response['Content-Transfer-Encoding'] = 'binary'
    with tempfile.NamedTemporaryFile(delete=True) as output:
         output.write(result)
         output.flush()
         output = open(output.name, 'rb')
         response.write(output.read())

    return response


def generate_lesson_pdf(request, lesson_id):


    lesson_match = lessonObjective.objects.get(id=lesson_id)
    # Rendered
    text_update = lessonText.objects.get(matched_lesson=lesson_match)
    html_string = render_to_string('dashboard/lesson_pdf.html', {'text_update': text_update})
    html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
    result = html.write_pdf()

     # Creating http response
    response = HttpResponse(content_type='application/pdf;')
    response['Content-Disposition'] = 'inline; filename=Lesson_Plan.pdf'
    response['Content-Transfer-Encoding'] = 'binary'
    with tempfile.NamedTemporaryFile(delete=True) as output:
         output.write(result)
         output.flush()
         output = open(output.name, 'rb')
         response.write(output.read())

    return response

def DigitalWorksheet(request, user_id=None, class_id=None, subject=None, lesson_id=None):
    current_week = date.today().isocalendar()[1] 
    user_profile = User.objects.get(id=user_id)

    classroom_profile = classroom.objects.get(id=class_id)
    grade_list = classroom_profile.grade_level.all()

    standard_match = standardSet.objects.get(id=classroom_profile.standards_set_id)
    classroom_subjects = classroom_profile.subjects.all()

    subject_matches = standardSubjects.objects.filter(id__in=classroom_subjects)                                         
                                             
    
    lesson_match = lessonObjective.objects.get(id=lesson_id)
    topic_matches = lesson_match.objectives_topics.all()
    lesson_standards = singleStandard.objects.filter(id__in=lesson_match.objectives_standards.all())
    topic_lists_selected = topicInformation.objects.filter(id__in=topic_matches).order_by('item')

    if topic_lists_selected:
        generated_questions = []
        for item in topic_lists_selected:
            generated_quest = generate_questions_topic(item.id)
            if generated_quest:
                generated_questions.append(generated_quest[0])
    else:
        generated_questions = []

    return render(request, 'dashboard/worksheet_builder.html', {'user_profile': user_profile, 'lesson_match': lesson_match, 'generated_questions': generated_questions })




def DigitalStudyGuide(request, user_id=None, class_id=None, subject=None, lesson_id=None):
    current_week = date.today().isocalendar()[1] 
    user_profile = User.objects.get(id=user_id)

    classroom_profile = classroom.objects.get(id=class_id)
    grade_list = classroom_profile.grade_level.all()

    standard_match = standardSet.objects.get(id=classroom_profile.standards_set_id)
    classroom_subjects = classroom_profile.subjects.all()

    subject_matches = standardSubjects.objects.filter(id__in=classroom_subjects)                                         
    
    
    class_objectives = lessonObjective.objects.all().order_by('subject')
    vocab_list = vocabularyList.objects.filter(lesson_plan__in=class_objectives)
    lesson_activities = lessonFull.objects.filter(lesson_overview__in=class_objectives)
    lesson_match = lessonObjective.objects.get(id=lesson_id)
    lesson_standards = singleStandard.objects.filter(id__in=lesson_match.objectives_standards.all())
    topic_matches = lesson_match.objectives_topics.all()
    topic_list = topicInformation.objects.filter(id__in=topic_matches)
    teacher_objective = lesson_match.teacher_objective
   
    questions_selected = googleRelatedQuestions.objects.filter(lesson_plan=lesson_match, is_selected=True)
    topics_selected = googleSearchResult.objects.filter(lesson_plan=lesson_match, is_selected=True)
    

    keywords_selected = keywordResults.objects.filter(lesson_plan=lesson_match, is_selected=True).order_by('-relevance')
    keywords_matched = keywordResults.objects.filter(lesson_plan=lesson_match, is_selected=False).order_by('-relevance')

    keywords = []
    
    youtube_matched = youtubeSearchResult.objects.filter(lesson_plan=lesson_match, is_selected=True)
    

    return render(request, 'dashboard/study_guide.html', {'user_profile': user_profile, 'topic_list': topic_list, 'keywords_selected': keywords_selected, 'youtube_matched': youtube_matched, 'questions_selected': questions_selected, 'topics_selected': topics_selected, 'keywords_matched': keywords_matched, 'lesson_standards': lesson_standards, 'lesson_match': lesson_match, 'lesson_activities': lesson_activities, 'class_objectives': class_objectives, 'current_week': current_week, 'classroom_profile': classroom_profile})



def QuestionUploadTwo(request):
    #second step to the standards upload process
    #name="standards_upload"
    template = "administrator/upload_textbook.html"


    prompt = {
        'order': 'Order of the CSV should be first name, surname'   
              }
    # GET request returns the value of the data with the specified key.
    if request.method == "GET":
        return render(request, template, prompt)
    csv_file = request.FILES['file']
    # let's check if it is a csv file
    if not csv_file.name.endswith('.csv'):
        messages.error(request, 'THIS IS NOT A CSV FILE')
    data_set = csv_file.read().decode('UTF-8')
    # setup a stream which is when we loop through each line we are able to handle a data in a stream
    io_string = io.StringIO(data_set)
    next(io_string)

    for line in csv.reader(io_string, delimiter=','):
        subject	= line[0]
        grade_level = line[1]	
        standard_set = line[2]
        topic_type = line[3]	
        item = line[4] 	
        question_type = line[5]  
        question_points = 1		
        Question = line[6] 		
        Correct	= line[8] 	
        Incorrect_One = line[10] 	
        Incorrect_Two = line[12] 		
        Incorrect_Three	= line[14] 
        Story = line[15]
        explanation	= line[16]
        
        
        if Story:
            add_story, created = storySection.objects.get_or_create(Section=Story)
            q_title = str(Question) + '-' + str(subject) + str(add_story.id)
            add_full, created = storyFull.objects.get_or_create(Title=q_title)
            new_story = add_full.section.add(add_story)

        item = get_keywords(Question)
        standard_match = standardSet.objects.filter(Location=standard_set).first()
        matched_grade = gradeLevel.objects.filter(grade=grade_level, standards_set=standard_match).first()
        matched_subject = standardSubjects.objects.filter(subject_title=subject, standards_set=standard_match, grade_level=matched_grade).first()
        topic_match, created = topicTypes.objects.get_or_create(item=topic_type)
        question_type, created = questionType.objects.get_or_create(item=question_type)

        new_question, created = topicQuestion.objects.get_or_create(subject=matched_subject, grade_level=matched_grade, standard_set=standard_match, item=item, question_type=question_type, question_points=question_points, Question=Question, Correct=Correct, Incorrect_One=Incorrect_One, Incorrect_Two=Incorrect_Two, Incorrect_Three=Incorrect_Three, explanation=explanation )

        add_topic = new_question.topic_type.add(topic_match)
        

    context = {'step': True}
    return render(request, template, context)

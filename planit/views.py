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
import sendgrid
from sendgrid.helpers.mail import *
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
from .get_wikipedia import *
from .get_seach_results import *
from .get_misc_info import *
from .fix_types import *
##################| Homepage Views |#####################
#Homepage Landing Page
def Homepage(request):
    
    standards_match = standardSet.objects.all()
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
            return redirect('thank_you', user_id=user_id, waitlist_inv=None)
        else:
            return redirect('registration_full', retry=True, teacher_invite=None)
        
    else:

        form = TeacherForm()
    
    choice = random.choice([1, 2])
    if choice == 1:
        return render(request, 'dashboard/index3.html', {'form': form, 'standards_match': standards_match})
    else:
        return render(request, 'dashboard/index3.html', {'form': form, 'standards_match': standards_match})

#Full Form Regstration if error on pop up modal
def FormFull(request, retry=None):
    standards_match = standardSet.objects.all()
    if retry != False and retry != "False":
        message = 'Something Went Wrong! Please complete your registration again.'
        error_messages = retry
    else:
        message = "Let's Get Started!"
        error_messages = None
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
            standards_set = form.cleaned_data.get('standards_set')
            if standards_set == 0:
                user.standards_set = None
            else:
                standard_match = standardSet.objects.get(id=standards_set.id)
                user.standards_set = standard_match
                user.save()

            school_user_match = school_user.objects.get(user=user_id)
            school_user_match.standards_set = standard_match

            welcome_message = 'Welcome to Class Planit, %s! We will be in touch when your account is activated.' % (username)
        
            #create "empty" teacherInvitations (only created_by and is_waitlist)
            user_match = User.objects.get(id=user_id)
            new_waitlist_inv = teacherInvitations.objects.create(invite_ref= None, created_by= user_match, is_waitlist= True)
            inv_ref = new_waitlist_inv.invite_ref

            to = str(my_number)
            if to:
                try:
                    client = Client(config('TWILIO_ACCOUNT_SID'), config('TWILIO_AUTH_TOKEN'))
                    response = client.messages.create(
                            body=str(welcome_message),
                            to=to, from_=config('TWILIO_PHONE_NUMBER'))
                    message = Mail(
                            from_email='hello@classplanit.co',
                            to_emails=user_email,
                            subject='Welcome to Class Planit',
                            html_content= get_template('homepage/welcome_to_classplanit.html').render({'user': user, 'waitlist_inv': inv_ref}))
                except Exception as e:
                    pass
            try:
                sg = SendGridAPIClient(config('SENDGRID_API_KEY'))
                response = sg.send(message)
                print(response.status_code)
                print(response.body)
                print(response.headers)
            except:
                pass

            return redirect('registration_info', user_id=user_id, waitlist_inv=inv_ref, invited_by=None)

    else:

        form = TeacherForm()
    
    return render(request, 'homepage/registration_full.html', {'form': form, 'message': message, 'error_messages': error_messages, 'standards_match': standards_match})

#Full Form Regstration for invited teachers to be placed on waitlist
def FormFullInv(request, retry=None, invite_id=None):
    if retry != False and retry != "False":
        message = 'Something Went Wrong! Please complete your registration again.'
        error_messages = retry
    else:
        message = "Let's Get Started!"
        error_messages = None

    invite_match = teacherInvitations.objects.filter(invite_ref= invite_id).first()
    invited_by = invite_match.created_by
    invited_by_name = invited_by.first_name, invited_by.last_name

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

            #create "empty" teacherInvitations (only created_by and is_waitlist)
            user_match = User.objects.get(id=user_id)
            new_waitlist_inv = teacherInvitations.objects.create(invite_ref= None, created_by= user_match, is_waitlist= True)
            inv_ref = new_waitlist_inv.invite_ref
        
            to = str(my_number)
            if to:
                try:
                    client = Client(config('TWILIO_ACCOUNT_SID'), config('TWILIO_AUTH_TOKEN'))
                    response = client.messages.create(
                            body=str(welcome_message),
                            to=to, from_=config('TWILIO_PHONE_NUMBER'))
                    message = Mail(
                            from_email='hello@classplanit.co',
                            to_emails=user_email,
                            subject='Welcome to Class Planit',
                            html_content= get_template('homepage/welcome_to_classplanit.html').render({'user': user, 'waitlist_inv': inv_ref}))

                except Exception as e:
                    pass
            try:
                sg = SendGridAPIClient(config('SENDGRID_API_KEY'))
                response = sg.send(message)
                print(response.status_code)
                print(response.body)
                print(response.headers)
            except:
                pass
               
            return redirect('registration_info', user_id=user_id, waitlist_inv=inv_ref, invited_by=invited_by.id)

    else:

        form = TeacherForm()
    
    return render(request, 'homepage/registration_full_inv.html', {'form': form, 'message': message, 'error_messages': error_messages, 'invited_by_name': invited_by_name})

#Full Form Info for waitlist sign ups
def FormInfo(request, user_id=None, waitlist_inv=None, invited_by=None):
    if request.method == "POST":

        form = waitlistUserInfoForm(request.POST)
        if form.is_valid():
            form.save()

            return redirect('thank_you', user_id=user_id, waitlist_inv=waitlist_inv, invited_by=invited_by)

    else:

        form = waitlistUserInfoForm()
    
    return render(request, 'homepage/registration_info.html', {'form': form})


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

#Thanks for submitting the questionnaire
class ThankYouQuestionnaire(TemplateView):
    template_name = 'homepage/thank_you_questionnaire.html' 

    def get(self,request):
        return render(request, 'homepage/thank_you_questionnaire.html', {})

#Thank for Registering Page, we will get back to you
#class ThankYou(TemplateView):
#    template_name = 'homepage/thank_you.html' 
#
#    def get(self,request,user_id,waitlist_inv,invited_by):
#        user_profile = User.objects.get(id=user_id)
#
#        return render(request, 'homepage/thank_you.html', {'user_profile': user_profile, 'waitlist_inv': waitlist_inv })

#Thank for Registering Page, we will get back to you
def ThankYou(request, user_id=None, waitlist_inv=None, invited_by=None): 
    user_profile = User.objects.get(id=user_id)
    
    return render(request, 'homepage/thank_you.html', {'user_profile': user_profile, 'waitlist_inv': waitlist_inv, 'invited_by': invited_by })

#User Login 
def login_user(request):

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('Dashboard', week_of='Current', subject_id='All', classroom_id='All')
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

############################################
#Teacher Functions  
############################################

#classroom list for teacher 

def ClassroomLists(request):
    current_year = datetime.datetime.now().year
    current_week = date.today().isocalendar()[1] 
    user_profile = User.objects.filter(username=request.user.username).first()
    standard_set_match = user_profile.standards_set
    grade_list = gradeLevel.objects.filter(standards_set=standard_set_match).order_by('grade')

    class_summary = get_classroom_summary(user_profile.id, current_year)
    
    
    page = 'Classrooms'

    if request.method == "POST":
        form = classroomForm(request.POST, request.FILES)
        if form.is_valid():
            prev = form.save(commit=False)
            prev.main_teacher = user_profile
            prev.standards_set = standard_set_match
            prev.save()
            
            return redirect('classroom_settings', user_id=user_profile.id, classroom_id=prev.id, view_ref=1, confirmation=0)
    else:
        form = classroomForm()

    return render(request, 'dashboard/classroom_list.html', {'user_profile': user_profile, 'grade_list': grade_list, 'form': form, 'class_summary': class_summary, 'page': page})

def AddStudentToClassroom(request, user_id=None, class_id=None, invite_id=None):
    user_match = User.objects.get(id=user_id)
    classroom_match = classroom.objects.get(id=class_id)
    
    invite_id = int(invite_id)
    if invite_id == 0:
        if request.method == "POST":
            form = studentInvitationForm(request.POST, request.FILES)
            if form.is_valid():
                prev = form.save(commit=False)
                prev.created_by = user_match
                prev.for_classroom = classroom_match
                student_fname = prev.first_name
                student_lname = prev.last_name
                student_grade = prev.grade_level
                new_student = studentProfiles.objects.create(first_name= student_fname, last_name= student_lname, current_grade_level= student_grade, is_enrolled= True )
                update_classroom = classroom_match.student.add(new_student)
                prev.save()
                invitation_match = studentInvitation.objects.get(id=prev.id)

                invite_email = invitation_match.email

                if invite_email:
                    try:
                        message = Mail(
                            from_email='welcome@classplanit.co',
                            to_emails=invite_email,
                            subject="You're Invited",
                            html_content= get_template('dashboard/student_invite_email.html').render({'invitation_match': invitation_match}))
                    except:
                        pass
                try:
                    sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
                    response = sg.send(message)
                    print(response.status_code)
                    print(response.body)
                    print(response.headers)
                except Exception as e:
                    pass

                return redirect('classroom_settings', user_id=user_match.id, classroom_id=class_id, view_ref='Students', confirmation=1)
            else:
                return redirect('classroom_list')
        else:

            return redirect('classroom_list')
    else:
        invite_match = studentInvitation.objects.get(id= invite_id)
        invite_email = invite_match.email
        if invite_email:
            try:
                message = Mail(
                    from_email='welcome@classplanit.co',
                    to_emails=invite_email,
                    subject="You're Invited",
                    html_content= get_template('dashboard/student_invite_email.html').render({'invitation_match': invite_match}))
            except:
                pass
        try:
            sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
            response = sg.send(message)
            print(response.status_code)
            print(response.body)
            print(response.headers)
        except Exception as e:
            pass

        return redirect('classroom_settings', user_id=user_match.id, classroom_id=class_id, view_ref='Students', confirmation=2)

#Sends invite email for support teachers
def AddTeacherToClassroom(request, user_id=None, class_id=None, invite_id=None):
    user_match = User.objects.get(id=user_id)
    if (class_id == None) or (class_id == 'None'):
        return redirect('registration_full', retry=False, invite_id=invite_id)
    else:
        classoom_match = classroom.objects.get(id=class_id)

        invite_id = int(invite_id)
        #invite_id to determine if resend(1) or first send(0)
        if invite_id == 0:
            if request.method == "POST":
                form = teacherInvitationsForm(request.POST, request.FILES)
                if form.is_valid():
                    prev = form.save(commit=False)
                    prev.created_by = user_match
                    prev.for_classroom = classoom_match
                    prev.is_pending = True
                    prev.save()
                    invitation_match = teacherInvitations.objects.get(id=prev.id)

                    invite_email = invitation_match.email

                    if invite_email:
                        try:
                            message = Mail(
                                from_email='welcome@classplanit.co',
                                to_emails=invite_email,
                                subject="You're Invited",
                                html_content= get_template('dashboard/teacher_invite_email.html').render({'invitation_match': invitation_match}))
                        except:
                            pass
                    try:
                        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
                        response = sg.send(message)
                        print(response.status_code)
                        print(response.body)
                        print(response.headers)
                    except Exception as e:
                        pass

                    return redirect('classroom_settings', user_id=user_match.id, classroom_id=class_id, view_ref='Teachers', confirmation=1)
                else:
                    return redirect('classroom_list')
            else:
                return redirect('classroom_list')
        else:
            invite_match = teacherInvitations.objects.get(id= invite_id)
            invite_email = invite_match.email
            if invite_email:
                try:
                    message = Mail(
                        from_email='welcome@classplanit.co',
                        to_emails=invite_email,
                        subject="You're Invited",
                        html_content= get_template('dashboard/teacher_invite_email.html').render({'invitation_match': invite_match}))
                except:
                    pass
            try:
                sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
                response = sg.send(message)
                print(response.status_code)
                print(response.body)
                print(response.headers)
            except Exception as e:
                pass

            return redirect('classroom_settings', user_id=user_match.id, classroom_id=class_id, view_ref='Teachers', confirmation=2)

#Adds or Removes Subjects
def EditClassroomSubjects(request, user_id=None, class_id=None, subject_id=None, action=None):
    user_match = User.objects.get(id=user_id)
    classroom_profile = classroom.objects.get(id=class_id)
    subject_match = standardSubjects.objects.get(id=subject_id)
    
    action = int(action)
    if action == 0:
        classroom_profile.subjects.add(subject_match)
    else:
        classroom_profile.subjects.remove(subject_match)
    
    return redirect('classroom_settings', user_id=user_match.id, classroom_id=class_id, view_ref='Subjects', confirmation=0)

#Adds or Removes Grade Levels, also updates default single_grade
def EditClassroomGradeLevels(request, user_id=None, class_id=None, grade_level_id=None, action=None):
    user_match = User.objects.get(id=user_id)
    classroom_profile = classroom.objects.get(id=class_id)
    grade_level_match = gradeLevel.objects.get(id=grade_level_id)
    
    action = int(action)
    if action == 0:
        classroom_profile.grade_level.add(grade_level_match)
    #updates the default grade level with the grade selected
    elif action == 2:
        current_default = classroom_profile.single_grade
        classroom_profile.single_grade = grade_level_match
        classroom_profile.grade_level.add(current_default)
        classroom_profile.grade_level.remove(grade_level_match)
        classroom_profile.save()
    else:
        classroom_profile.grade_level.remove(grade_level_match)
    
    return redirect('classroom_settings', user_id=user_match.id, classroom_id=class_id, view_ref='Grade-Levels', confirmation=0)


def JoinStudentToClassroom(request, invite_ref=None):
    pass


#view information for a single classroom 
def ClassroomDashboard(request, user_id=None, class_id=None):
    current_year = datetime.datetime.now().year
    user_profile = User.objects.filter(username=request.user.username).first()
    class_profile = classroom.objects.get(id=class_id)
    student_summary = get_classroom_list_summary(user_profile.id, current_year, class_id)

    #get all students in classroom and info
    student_list, no_students = get_student_list(user_id, class_id)
    student_info = get_student_info(student_list)
    
    #gets the classrooms teachers are main teacher on 
    classroom_profiles = classroom.objects.filter(main_teacher=user_profile)
    objective_matches = lessonObjective.objects.filter(lesson_classroom__in=classroom_profiles)
    # gets the subjects and classrooms for the dropdown options and subjects display
    subject_results, classroom_results = get_subject_and_classroom(objective_matches)

    context = { 'user_profile': user_profile, 'student_summary': student_summary, 'class_profile': class_profile,\
                'subject_results': subject_results, 'classroom_results': classroom_results, 'student_list': student_list,\
                'student_info': student_info, 'no_students': no_students}

    return render(request, 'dashboard/classrooms.html', context)

def ClassroomSettingsView(request, user_id=None, classroom_id=None, view_ref=None, confirmation=None): 
    current_year = datetime.datetime.now().year
    user_profile = User.objects.filter(username=request.user.username).first()
    school_user_match = school_user.objects.filter(user=user_profile.id).first()
    if school_user_match.standards_set:
        standard_set_match = school_user_match.standards_set
    else:
        standard_set_match = standardSet.objects.filter(Location='Texas Teks').first()
    class_profile = classroom.objects.get(id=classroom_id)
    student_summary = get_classroom_list_summary(user_profile.id, current_year, classroom_id)

    #get all of the standard subjects from the standards set 
    subject_list = standardSubjects.objects.filter(standards_set=class_profile.standards_set).filter(Q(is_admin=True) | Q(created_by=user_profile))
    current_subjects = class_profile.subjects

    #get all grade levels from standards set
    grade_list = gradeLevel.objects.filter(standards_set=class_profile.standards_set).order_by('grade')
    current_grade_levels = class_profile.grade_level
    current_grade_level_list = gradeLevel.objects.filter(id__in=current_grade_levels.all()).order_by('grade')
    default_grade = class_profile.single_grade

    #get all students and support teachers in classroom
    student_list, no_students = get_student_list(user_id, classroom_id)
    teacher_list = get_teacher_list(user_id, classroom_id)

    #gets the classrooms teachers are main teacher on 
    classroom_profiles = classroom.objects.filter(main_teacher=user_profile)
    # the lessonObjective is a single lesson plan for one subject, one grade, in one classroom
    objective_matches = lessonObjective.objects.filter(lesson_classroom__in=classroom_profiles)
    # gets the subjects and classrooms for the dropdown options and subjects display
    subject_results, classroom_results = get_subject_and_classroom(objective_matches)
    confirmation = int(confirmation)

    if request.method == "POST":
        form_subject = teacherSubjectForm(request.POST, request.FILES)
        if form_subject.is_valid():
            subject_title = form_subject.cleaned_data.get('subject_title')
            new_subject = standardSubjects.objects.create(subject_title=subject_title, standards_set=standard_set_match, created_by=user_profile, is_admin=False)
            single_grade = new_subject.grade_level.add(default_grade)
            for grade in current_grade_level_list:
                new_subject.grade_level.add(grade)
            update_subject = class_profile.subjects.add(new_subject)
            return redirect('classroom_settings', user_id=user_profile.id, classroom_id=class_profile.id, view_ref='Subjects', confirmation=0)
    else:
        form_subject = teacherSubjectForm()

    if request.method == "POST":
        form_class_title = classroomTitleForm(request.POST, request.FILES)
        if form_class_title.is_valid():
            classroom_title = form_class_title.cleaned_data.get('classroom_title')
            class_profile.classroom_title = classroom_title
            class_profile.save()
            return redirect('classroom_settings', user_id=user_profile.id, classroom_id=class_profile.id, view_ref='Classroom-Title', confirmation=0)
    else:
        form_class_title = classroomTitleForm()
    
    context = {'user_profile': user_profile, 'form_subject': form_subject, 'form_class_title': form_class_title, 'view_ref': view_ref,\
               'student_summary': student_summary, 'class_profile': class_profile, 'subject_results': subject_results, 'classroom_results': classroom_results,\
               'confirmation': confirmation, 'subject_list': subject_list, 'current_subjects': current_subjects, 'grade_list': grade_list,\
               'current_grade_levels': current_grade_levels, 'student_list': student_list, 'teacher_list': teacher_list}
    return render(request, 'dashboard/classrooms_settings.html', context)




#view standards that have been addressed so far 
def StandardsTracking(request, user_id=None):
    current_year = datetime.datetime.now().year
    user_profile = User.objects.filter(username=request.user.username).first()
    
    return render(request, 'dashboard/app-analysis.html', {'user_profile': user_profile,})


#Update the week_of to reflect a different active week
def UpdateWeekOf(request, week_of, user_id=None, classroom_id=None, subject_id=None, action=None):
    week_of = int(week_of)
    action = int(action)
    #prev week
    if action == 1:
        active_week = week_of - 1
    #next week
    else:
        active_week = week_of + 1
    
    return redirect('Dashboard', week_of= active_week, subject_id= subject_id, classroom_id= classroom_id )


#Main Teacher Dashboard View labeled as 'Overview'
def Dashboard(request, week_of, subject_id, classroom_id):
    #run to fix the incorrect topic types
    fix_incorrect_types()

    #get active and current week number (active being the week the teacher is on and current meaning the actual week in the calendar)
    week_info = get_week_info(week_of)

    user_profile = User.objects.filter(id=request.user.id).first()

    if user_profile is not None:
        #gets the classrooms teachers are main teacher on 
        classroom_profiles = classroom.objects.filter(main_teacher=user_profile)

        #? we need to as a classroom list where teacher is not the main teacher but classrooms are shared

        # the lessonObjective is a single lesson plan for one subject, one grade, in one classroom
        objective_matches = lessonObjective.objects.filter(week_of=week_info['active_week'], lesson_classroom__in=classroom_profiles)
        
        if subject_id == 'All':
            if classroom_id == 'All':
                active_lessons = objective_matches
            else:
                active_lessons = objective_matches.filter(lesson_classroom_id=classroom_id)
        else:
            if classroom_id == 'All':
                active_lessons = objective_matches.filter(subject_id=subject_id)
            else:
                active_lessons = objective_matches.filter(subject_id=subject_id, lesson_classroom_id=classroom_id)

        # gets the subjects and classrooms for the dropdown options
        subject_results, classroom_results = get_subject_and_classroom(objective_matches)
        
        context = {'user_profile': user_profile, 'current_week': week_info['current_week'], 'active_week': week_info['active_week'], 'objective_matches': objective_matches,\
                    'previous_week': week_info['previous_week'], 'next_week': week_info['next_week'], 'subject_results': subject_results, 'classroom_results': classroom_results, \
                    'active_lessons': active_lessons, 'active_subject_id': subject_id, 'active_classroom_id': classroom_id}
        return render(request, 'dashboard/dashboard.html', context)
    else:
        
        return redirect('login_user')


#This is the form where teachers create a new lessonObjective. 
#The teacher puts in their objective (what they want to teach the students)
def CreateObjective(request, user_id=None, week_of=None):
    if user_id is not None:
        user_profile = User.objects.filter(username=request.user.username).first()
        week_info = get_week_info(week_of)

        user_classrooms = classroom.objects.filter(main_teacher=user_profile)
        subjects = []
        if user_classrooms:
            for classroom_m in user_classrooms:
                s_match = classroom_m.subjects.all()
                subject_match = standardSubjects.objects.filter(id__in=s_match)
                for subject in subject_match:
                    subject_id = subject.id
                    subject_title = subject.subject_title
                    result = subject_id, subject_title
                    if result not in subjects:
                        subjects.append(result)


        if request.method == "POST":
            form = lessonObjectiveForm(request.POST, request.FILES)
            if form.is_valid():
                prev = form.save(commit=False)
                teacher_input = prev.teacher_objective
                
                prev.week_of = week_info['active_week']
                class_match = classroom.objects.get(id=prev.lesson_classroom_id)

                prev.standard_set = class_match.standards_set
                #this is an overide - currently we want one grade per classroom but we will move to multiple grade levels like art which could have 9, 10, 11 grades
                prev.current_grade_level = class_match.single_grade
                prev.save()
                
                return redirect('activity_builder', user_id=user_profile.id, class_id=class_match.id, subject=prev.subject_id, lesson_id=prev.id, page=0)
        else:
            form = lessonObjectiveForm()
    
        context = {'form': form, 'step': 1, 'user_profile': user_profile, 'user_classrooms': user_classrooms, 'subjects': subjects  }
        return render(request, 'dashboard/identify_objectives.html', context)
    else:
        message = 'Sorry, Please login'
        return redirect('login_user', {'message': message})


#redirect from CreateObjective form submission. 
# This page has the tinymce editor as well as the analytics and activity recommendations
def ActivityBuilder(request, user_id=None, class_id=None, subject=None, lesson_id=None, page=None):
    user_profile = User.objects.get(id=user_id)
    
    classroom_profile = classroom.objects.get(id=class_id)
    lesson_match = lessonObjective.objects.get(id=lesson_id)

    lesson_topics = topicInformation.objects.filter(id__in=lesson_match.objectives_topics.all())

    new_text, created = lessonText.objects.get_or_create(matched_lesson=lesson_match)
    
    youtube_search = youtube_results(lesson_match.teacher_objective, lesson_id)
    
    youtube_list = []
    if youtube_search:
        youtube_list = youtube_search[:3]
    
    vid_id_list = []
    for result in youtube_list:
        link = result['link']
        if link:
            vid_id = video_id(link)
            youtube_create, created = youtubeSearchResult.objects.get_or_create(lesson_plan=lesson_match, title=result['title'], link=link, vid_id=vid_id)
            vid_id_list.append(youtube_create)

    context = {'user_profile': user_profile, 'new_text': new_text, 'vid_id_list': vid_id_list, 'classroom_profile': classroom_profile, 'lesson_match': lesson_match}
    return render(request, 'dashboard/activity_builder.html', context)


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


#Creates Digital Worksheets with questions 
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
    topic_images = []
    for tp in topic_lists_selected:
        if tp.image_url:
            pass
        else:
            tp_image = get_possible_images(tp.item, tp.id)
            

    worksheet_theme = worksheetTheme.objects.get(id=1)

    img_id = worksheet_theme.background_image

    background_img = userImageUpload.objects.filter(id=worksheet_theme.background_image_id).first()

    return render(request, 'dashboard/activity_builder_2.html', {'user_profile': user_profile, 'get_worksheet': get_worksheet, 'all_matched_questions': all_matched_questions, 'question_match': question_match, 'question_id': question_id, 'next_q': next_q, 'background_img': background_img, 'worksheet_theme': worksheet_theme, 'current_question': current_question, \
                                                                 'matched_questions': matched_questions, 'subject_match_full': subject_match_full, 'current_week': current_week, 'page': page, 'class_id': class_id, 'subject': subject, 'lesson_id': lesson_id, \
                                                                  'short_answer': short_answer, 'fib':fib, 'multi_choice':multi_choice, 'unknown':unknown})



#Edit already created or recommended Question
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


#create new question from scratch
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

############################################
#Student Functions
############################################


#student begin worksheet 
def StudentWorksheetStart(request, lesson_id=None, worksheet_id=None, question_id=None):
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


#final submit of assigned worksheet
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


#student dashboard 
def StudentMainDashboard(request, user_id=None, lesson_id=None, worksheet_id=None, submit=None):
    form = StudentForm()
    form2 = StudentForm()
    user_profile = User.objects.filter(id=user_id).first()
    return render(request, 'dashboard/student_main.html', {'user_profile': user_profile, 'form': form, 'form2': form2 })


#student registration 
def StudentRegistration(request, ref_id=None, lesson_id=None, worksheet_id=None):
    if len(ref_id) < 7:
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
    else:
        invite_match = studentInvitation.objects.get(invite_ref=ref_id)
        student_match = studentProfile.objects.get(id=invite_match.student_profile_id)
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
                student_match.student_username = user
                student_match.save()
                invite_match.is_pending = False
                invite_match.save()
                if user is not None:
                    login(request, user)
                return redirect('student_main', user_id=user_id)
        else:
            form = StudentForm()
            return render(request, 'dashboard/sign-in.html', {'form': form})


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


#student analytics for parents and students
def StudentPerformance(request, user_id, class_id, week_of):
    all_themes = studentPraiseTheme.objects.all()
    user_profile = User.objects.get(id=user_id)
    current_year = datetime.datetime.now().year
    current_week = date.today().isocalendar()[1]
    start = current_week - 12
    if start < 1:
        start = 1
    

    week_breakdown = get_weekly_brackets(user_id, start, current_week, current_year)
    week_breakdown['low'] =  [ 2, 1, 2, 1, 2, 3, 4, 4, 2, 4, 3, 3]
    week_breakdown['mid'] =  [14,12,11,14,10,12,14,13,13,14,13,15]
    week_breakdown['high'] = [ 4, 7, 7, 5, 8, 5, 2, 3, 5, 2, 4, 2]
    top_lessons = get_demo_ks_brackets(user_id, start, current_week, current_year)
    student_results = get_student_results(user_id, start, current_week, current_year)
    return render(request, 'dashboard/tasks.html', {'user_profile': user_profile, 'all_themes': all_themes, 'week_breakdown': week_breakdown, 'top_lessons': top_lessons, 'student_results': student_results})


####### these functions handle the students answers as they go through the digital worksheet #########
#selected the multiple choice answer in worksheet question
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


#submits fill in the blank answer in worksheet question 
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


#submits short answer in worksheet question 
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


#def VideoReview(request, user_id, video_id):

###### end student answer handling fuctions ##############


############################################
#Upload Functions that allows us to upload csv's of relevant content cleaned in pandas 
############################################

#uploads the standards from each state or region 
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

#uploads key terms 
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


        standard_match = standardSet.objects.filter(Location=Standard_Set).first()
        matched_grade = gradeLevel.objects.filter(grade=Grade_Level, standards_set=standard_match).first()
        matched_subject = standardSubjects.objects.filter(subject_title=Subject, standards_set=standard_match, grade_level=matched_grade).first()
        
        checked = check_topic_type(topic_type)
        corrected_topic = checked[1]
        topic_match, created = topicTypes.objects.get_or_create(item=corrected_topic)
        new_topic, created = topicInformation.objects.get_or_create(subject=matched_subject, grade_level=matched_grade, standard_set=standard_match, topic=topic, item=item)
        new_description, created =  topicDescription.objects.get_or_create(description=Description) 
        add_description = new_topic.description.add(new_description)
        add_topic = new_topic.topic_type.add(topic_match)

    context = {'step': True}
    return render(request, template, context)


#uploads cleaned textbook data for textbook matching
#this is the first step where you create textbook title and select subject and grade 
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


#this is second step when the actual csv is uploaded 
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


############################################
#Ajax Queries from the Activity Builder Page 
############################################


#this is to save the tinymce editor 
def SaveLessonText(request, lesson_id):
    #this is a jquery function that's set on an interval. It pulls in the tinymce and analyzes the text
    user = User.objects.filter(id=request.user.id).first()
    lesson_match = lessonObjective.objects.get(id=lesson_id)
    new_text, created = lessonText.objects.get_or_create(matched_lesson=lesson_match)
    less_class = lesson_match.lesson_classroom_id

    if request.method == 'GET':
        overview = request.GET['overview']
        new_text.overview = overview
        new_text.is_initial = False
        new_text.save()
        #this function is at get_lessons.py
        update_lesson_analytics = get_lesson_sections(overview, less_class, lesson_id, user.id)
        now = datetime.datetime.now().strftime('%H:%M:%S')
        context = {"data": now}
        return JsonResponse(context)
    else:
        return HttpResponse("Request method is not a GET")

######## Selection functions that are called on click from the activity_builder.html ########
def SelectYoutubeVideo(request):
    #adds youtube video to lesson when it is selected 
    if request.method == 'GET':
        user_profile = User.objects.filter(username=request.user.username).first()
        user_id = user_profile.id
        video_id = request.GET['video_id']
        lesson_id = request.GET['lesson_id']
        lesson_match = lessonObjective.objects.get(id=lesson_id)
        video_match = youtubeSearchResult.objects.get(id=video_id)
        video_match.is_selected = True
        video_match.save()
        vid_trans = get_transcript(video_match.vid_id, video_match.id, lesson_id)
        print(video_match.link)
        context = {'title': video_match.title , 'link': video_match.link}

        return JsonResponse(context)
    else:
        return HttpResponse("Request method is not a GET")



def SelectTopic(request):
    #function to add topic to lesson when its selected 
    if request.method == 'GET':
        user_profile = User.objects.filter(username=request.user.username).first()
        user_id = user_profile.id
        topic_id = request.GET['topic_id']
        lesson_id = request.GET['lesson_id']
        lesson_match = lessonObjective.objects.get(id=lesson_id)
        topic_match = topicInformation.objects.get(id=topic_id)
        update_lesson = lesson_match.objectives_topics.add(topic_match)
        

        check_topic = topic_match.topic_type.all()
        if check_topic:
            pass
        else:
            
            result = openai_term_labels(user_id, topic_match, lesson_match.subject, lesson_match.current_grade_level)
            
            result = result.strip("'")
            if result:
                tt_new, created = topicTypes.objects.get_or_create(item=result)
                add_tt = topic_match.topic_type.add(tt_new)

        list_one = []
        list_two = []
        for desc in topic_match.description.all():
            list_one.append(desc)
            list_two.append(desc)

        for desc1 in list_one:
            for desc2 in list_two:
                if desc1.id == desc2.id:
                    pass
                else:
                   
                    is_dup = check_duplicate_strings(desc1.description, desc2.description)
                    
                    if is_dup:
                        topic_match.description.remove(desc2)
        

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
        activity_id = int(activity_id)
        lesson_id = int(lesson_id)
        lesson_match = lessonObjective.objects.get(id=lesson_id)
        activity_match = selectedActivity.objects.get(id=activity_id)

        activity_match.is_selected = True 
        activity_match.save()

        context = {'text': activity_match.lesson_text}

        return JsonResponse(context)
    else:
        return HttpResponse("Request method is not a GET")


def AddSelectedQuestion(request):
    if request.method == 'GET':
        user_profile = User.objects.filter(username=request.user.username).first()
        user_id = user_profile.id
        quest_id = request.GET['quest_id']
        lesson_id = request.GET['lesson_id']
        activity_id = int(quest_id)
        lesson_id = int(lesson_id)
        lesson_match = lessonObjective.objects.get(id=lesson_id)
        quest_match = googleRelatedQuestions.objects.get(id=quest_id)

        quest_match.is_selected = True 
        quest_match.save()


        context = {'question': quest_match.question, 'answer': quest_match.snippet}

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

######## End Selection Functions #################

#remove function that removes receomendations and generates new ones ###################
def RemoveKeyTerms(request, lesson_id, class_id):

    if request.method == 'GET':
        user_profile = User.objects.filter(id=request.user.id).first()
        lesson_match = lessonObjective.objects.get(id=lesson_id)
        teacher_input = lesson_match.teacher_objective
        match_recs = reccomendedTopics.objects.filter(matched_lesson=lesson_match).first()
        match_score = match_recs.single_score.all()
        top_ids = []
        for item in match_score:
            match_recs.single_score.remove(item)
            if item.is_displayed:
                item.is_displayed = False
                item.save()
                top_ids.append(item.single_rec_topics_id)

        if top_ids:
            matched_rt = topicInformation.objects.filter(id__in=top_ids)
            for top in matched_rt:
                add_remove = match_recs.removed_topics.add(top)
                remove_rec = match_recs.rec_topics.remove(top)
        
        
        context = {"message": "your message"}


        return JsonResponse(context)
    else:
        return HttpResponse("Request method is not a GET")

######## End Selection Functions #################


#############################################################
######    Data Analytics and Ai powered functions ###########
#############################################################

########## Analytics Functions that set on  Interval to analze content in editor ##################

#this is the summary on dropdowns that covers diffrentiation, engagement, retention, and alignment
def GetActivitySummary(request, lesson_id):
    if request.method == 'GET':
        user_profile = User.objects.filter(id=request.user.id).first()
        #goes to get_activities.py
        lesson_analytics = label_activities_analytics_small(lesson_id)
        context = {"data": lesson_analytics}
        return JsonResponse(context)
    else:
        return HttpResponse("Request method is not a GET")


#this pulls blooms level for activity 
#learn about blooms here : 
#https://www.teachthought.com/learning/what-is-blooms-taxonomy-a-definition-for-teachers/
def GetBloomsAnalytics(request, lesson_id):
    if request.method == 'GET':
        user_profile = User.objects.filter(id=request.user.id).first()
        #goes to get_lessons.py 
        get_bl_data = label_blooms_activities_analytics(lesson_id)
        context = {"data": get_bl_data}
        return JsonResponse(context)
    else:
        return HttpResponse("Request method is not a GET")


#this pulls the Multiple Intelligence or Learning Styles for Activities 
#find out more: https://www.onatlas.com/blog/multiple-intelligences-theory
def GetMIAnalytics(request, lesson_id):
    if request.method == 'GET':
        user_profile = User.objects.filter(id=request.user.id).first()
        #goes to get_lessons.py
        get_mi_data = label_mi_activities_analytics(lesson_id)
        context = {"data": get_mi_data}
        return JsonResponse(context)
    else:
        return HttpResponse("Request method is not a GET")


#this pulls in Rention Rate Analytics for Activities 
#https://www.educationcorner.com/the-learning-pyramid.html#:~:text=The%20%22learning%20pyramid%22%2C%20sometimes,they%20learn%20through%20teaching%20others.
def GetRetentionAnalytics(request, lesson_id):
    if request.method == 'GET':
        user_profile = User.objects.filter(id=request.user.id).first()
        get_retention_data = retention_activities_analytics(lesson_id)
        context = {"data": get_retention_data, "message": "your message"}

        return JsonResponse(context)
    else:
        return HttpResponse("Request method is not a GET")

#this functions updates the ket terms recommended in the word clouds 
def UpdateKeyTerms(request, lesson_id, class_id):
    if request.method == 'GET':
        user_profile = User.objects.filter(id=request.user.id).first()
        lesson_match = lessonObjective.objects.get(id=lesson_id)
        teacher_input = lesson_match.teacher_objective
        #pulls from acivity_builder.py
        update_term_list = generate_term_recs(teacher_input, class_id, lesson_id, user_profile.id)

        context = {"data": update_term_list, "message": "your message"}

        return JsonResponse(context)
    else:
        return HttpResponse("Request method is not a GET")

#this functions updates the ket terms recommended in the word clouds 
def UpdateBigQuestions(request, lesson_id, class_id):
    if request.method == 'GET':
        user_profile = User.objects.filter(id=request.user.id).first()
        lesson_match = lessonObjective.objects.get(id=lesson_id)
        teacher_input = lesson_match.teacher_objective
        #pulls from acivity_builder.py
        returns_list = get_big_ideas(teacher_input, class_id, lesson_id, user_profile.id)
        context = {"data": returns_list, "message": "your message"}
        return JsonResponse(context)
    else:
        return HttpResponse("Request method is not a GET")

#this function finds the most relevant Standards at the begining of the lesson plan. 
def UpdateStandards(request, lesson_id, class_id):

    if request.method == 'GET':
        user_profile = User.objects.filter(id=request.user.id).first()
        lesson_match = lessonObjective.objects.get(id=lesson_id)
        standards_now = lesson_match.objectives_standards.all()
        
        if standards_now:
            context = {}
            return JsonResponse(context)
        else:
            
            teacher_input = lesson_match.teacher_objective
            
            standards_topics = activity_builder_task(teacher_input, class_id, lesson_id, user_profile.id)

            rec_standards = lessonStandardRecommendation.objects.filter(lesson_classroom=class_id, objectives=lesson_id).first()
            standard_list = []
            if rec_standards:
                standards_list = rec_standards.objectives_standard.all()
                standards_recs = singleStandard.objects.filter(id__in=standards_list)
                for item in standards_recs:
                    line_item = '%s: %s' % (item.standard_objective, item.competency)
                    result = {'id': item.id, 'standard': line_item.capitalize()}
                    standard_list.append(result)
            

            if standard_list:
                context = {"data": standard_list, "message": "your message"}
                return JsonResponse(context)
            else:
                context = {}
                return JsonResponse(context)
    else:
        return HttpResponse("Request method is not a GET")


#this function creates teh activity recommendations found on the right side bar. 
def UpdateLessonActivities(request, lesson_id, class_id):
    if request.method == 'GET':
        user_profile = User.objects.filter(id=request.user.id).first()
        lesson_match = lessonObjective.objects.get(id=lesson_id)
        teacher_input = lesson_match.teacher_objective
        update_activity_list = get_lessons_ajax(lesson_id, user_profile.id)

        context = {"data": update_activity_list, "message": "your message"}

        return JsonResponse(context)
    else:
        return HttpResponse("Request method is not a GET")

#############################################################
######    End Data Analytics and Ai powered functions #######
#############################################################

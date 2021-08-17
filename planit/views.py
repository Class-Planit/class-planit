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
from django.http import JsonResponse
from django.core import serializers
from .get_search import *
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
            school_user_match.first_name = user.first_name
            school_user_match.last_name = user.last_name
            school_user_match.email = user.email
            school_user_match.username = user.username
            school_user_match.save()

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

            return redirect('Dashboard', week_of='Current', subject_id='All', classroom_id='All')

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
               
            
            return redirect('classroom_list')

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
            return redirect('Dashboard', week_of='Current', subject_id='All', classroom_id='All', standard_id='All')
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
    current_date = datetime.datetime.now()
    current_year = datetime.datetime.now().year
    current_week = date.today().isocalendar()[1] 
    user_profile = User.objects.filter(username=request.user.username).first()
    standard_set_match = user_profile.standards_set
    grade_list = gradeLevel.objects.filter(standards_set=standard_set_match).order_by('grade')

    class_summary = get_classroom_summary(user_profile.id, current_year, current_date)
    
    
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
def ClassroomDashboard(request, user_id=None, class_id=None, standard_id=None):
    user_profile = User.objects.get(id=user_id)
    current_date = datetime.datetime.now()
    current_year = datetime.datetime.now().year
    current_academic_year = academicYear.objects.filter(planning_teacher=user_profile, is_active=True).first()
    if current_academic_year:
        pass
    else:
        end_date = current_date + relativedelta(years=1)
        current_academic_year, created = academicYear.objects.get_or_create(start_date=current_date, end_date=end_date, planning_teacher=user_profile)
    
    user_profile = User.objects.filter(username=request.user.username).first()
    class_profile = classroom.objects.get(id=class_id)
    current_week = date.today().isocalendar()[1]
    student_summary = get_classroom_list_summary(user_profile.id, current_year, class_id)

    #get all students in classroom and info
    student_list, no_students = get_student_list(user_id, class_id)
    student_info = get_student_info(student_list, user_id)
    
    understanding_breakdown = get_levels_of_understanding(class_id, current_academic_year, current_week, user_profile)
    #gets the classrooms teachers are main teacher on 
    classroom_profiles = classroom.objects.filter(main_teacher=user_profile)
    objective_matches = lessonObjective.objects.filter(lesson_classroom__in=classroom_profiles)
    # gets the subjects and classrooms for the dropdown options and subjects display
    subject_results, classroom_results = get_subject_and_classroom(objective_matches, user_id)
    num_classrooms = len(classroom_results)
    print(classroom_results)
    print(num_classrooms)

    context = { 'user_profile': user_profile, 'student_summary': student_summary, 'class_profile': class_profile,\
                'subject_results': subject_results, 'classroom_results': classroom_results, 'student_list': student_list,\
                'student_info': student_info, 'no_students': no_students, 'num_classrooms': num_classrooms}

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
    subject_results, classroom_results = get_subject_and_classroom(objective_matches, user_id)
    num_classrooms = len(classroom_results)
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
               'current_grade_levels': current_grade_levels, 'student_list': student_list, 'teacher_list': teacher_list, 'num_classrooms': num_classrooms}
    return render(request, 'dashboard/classrooms_settings.html', context)




#view standards that have been addressed so far 
#user starts narrowing down standards to view by selecting subject and classroom
def StandardsTracking(request, user_id=None):
    current_year = datetime.datetime.now().year
    user_profile = User.objects.filter(username=request.user.username).first()
    
    user_classrooms = classroom.objects.filter(main_teacher=user_profile)
    subjects = []
    classroom_results = []
    if user_classrooms:
        for classroom_m in user_classrooms:
            c_result = classroom_m.id, classroom_m.classroom_title
            classroom_results.append(c_result)
            s_match = classroom_m.subjects.all()
            subject_match = standardSubjects.objects.filter(id__in=s_match)
            for subject in subject_match:
                subject_id = subject.id
                subject_title = subject.subject_title
                result = subject_id, subject_title
                if result not in subjects:
                    subjects.append(result)
    subject_results = subjects

    if request.method == "POST":
        form = standardsTrackingInfoForm(request.POST, request.FILES)
        if form.is_valid():
            prev = form.save(commit=False)
            use_subject = prev.track_subject
            use_subject_id = use_subject.id
            use_classroom = prev.track_classroom
            use_classroom_id = use_classroom.id
            prev.save()
            
            return redirect('narrow_standard_tracker', subject_id=use_subject_id, classroom_id=use_classroom_id)
    else:
        form = standardsTrackingInfoForm()


    print(subject_results)
    print(classroom_results)
    
    return render(request, 'dashboard/app-analysis.html', {'user_profile': user_profile, 'subject_results': subject_results, 'classroom_results': classroom_results})


#After narrowing down the standards tracking with subject and classroom
#displays the skill topics that are linked to multiple standards (has clickable standards)
def NarrowStandardsTracking(request, user_id=None, classroom_id=None, subject_id=None):
    user_profile = User.objects.filter(username=request.user.username).first()
    tracking_subject = standardSubjects.objects.filter(id=subject_id).first()
    tracking_classroom = classroom.objects.filter(id=classroom_id).first()


    standards_set_match = user_profile.standards_set
    grade_level_match = tracking_classroom.single_grade
    #filter for all standards related to the subject and grade level of the classroom
    all_standards = singleStandard.objects.filter(standards_set= standards_set_match, subject=tracking_subject, grade_level= grade_level_match)
    all_standards_info = []
    for current_standard in all_standards:
        skill_topic = current_standard.skill_topic
        standard_objective = current_standard.standard_objective
        found = standard_objective.find(".")
        if found != -1:
            topic = standard_objective[:found]
            standard_objective = standard_objective[(found+2):-27]
        else:
            topic = ""
            standard_objective = standard_objective[:-27]
        standard_id = current_standard.id
        lesson_matches = lessonObjective.objects.filter(objectives_standards=current_standard.id)
        lesson_count = lesson_matches.count()
        standard_info = skill_topic, topic, standard_objective, standard_id, lesson_count
        all_standards_info.append(standard_info)

    all_standards_info.sort(key=lambda x: x[4], reverse=True)

    context = {'user_profile': user_profile, 'tracking_subject': tracking_subject, 'tracking_classroom': tracking_classroom, \
               'all_standards_info': all_standards_info}

    return render(request, 'dashboard/app-analysis-skills.html', context)


#After selecting one specific standard, subject and classroom
#displays the standard and respective info about the standard to user
def SingleStandardsTracking(request, user_id=None, subject_id=None, classroom_id=None, standard_id=None):
    user_profile = User.objects.filter(username=request.user.username).first()
    current_subject = standardSubjects.objects.filter(id=subject_id).first()
    current_classroom = classroom.objects.filter(id=classroom_id).first()
    current_standard = singleStandard.objects.filter(id=standard_id).first()
    current_grade = current_classroom.single_grade_id

    grade_match = gradeLevel.objects.filter(id=current_grade).first()
    standard_objective = current_standard.standard_objective
    similar_standards = singleStandard.objects.filter(standard_objective=standard_objective, grade_level=grade_match).order_by('competency')
    competency_info = []

    for each_standard in similar_standards:
        #for each competency, find the lessons and worksheets associated
        competency = each_standard.competency
        all_lessons = lessonObjective.objects.filter(lesson_classroom=current_classroom, objectives_standards= each_standard)
        worksheet_matches = worksheetFull.objects.filter(lesson_overview__in=all_lessons)
        worksheet_count = worksheet_matches.count()
        workseet_assignments = worksheetClassAssignment.objects.filter(lesson_overview__in=all_lessons)
        if workseet_assignments:
            assignemnt_average = 0
            #assignemnt_average = get_assignment_average(workseet_assignments)
        else:
            assignemnt_average = 0
        

        related_lessons = len(all_lessons)
        standard_id = each_standard.id

        if all_lessons:
            top_lesson = all_lessons[0]
            lesson_week = top_lesson.week_of
        else:
            lesson_week = 'Current'

        result = competency, related_lessons, standard_id, worksheet_count, assignemnt_average, lesson_week
        if result not in competency_info:
            competency_info.append(result)



    context = {'user_profile': user_profile, 'current_subject': current_subject, 'current_classroom': current_classroom, \
               'current_standard': current_standard, 'similar_standards': similar_standards, 'competency_info': competency_info, \
               'subject_id': subject_id, 'classroom_id': classroom_id}

    return render(request, 'dashboard/app-analysis-single.html', context)



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
    
    return redirect('Dashboard', week_of= active_week, subject_id= subject_id, classroom_id=classroom_id, standard_id='All')


#Main Teacher Dashboard View labeled as 'Overview'
def Dashboard(request, week_of, subject_id, classroom_id, standard_id=None):
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
            #subject, class and standard are 'All'
            if classroom_id == 'All':
                active_lessons = objective_matches
            #subject and standard are 'All'
            else:
                active_lessons = objective_matches.filter(lesson_classroom_id=classroom_id)
        else:
            if standard_id == 'All':
                #class and standard are 'All'
                if classroom_id == 'All':
                    active_lessons = objective_matches.filter(subject_id=subject_id)
                #standard is 'All'
                else:
                    active_lessons = objective_matches.filter(subject_id=subject_id, lesson_classroom_id=classroom_id)
            #subject, class and standard are specific (from Standards Tracking)
            else:
                standard_match = singleStandard.objects.filter(id=standard_id).first()
                active_lessons = objective_matches.filter(subject_id=subject_id, lesson_classroom_id=classroom_id, objectives_standards=standard_match)



        # gets the subjects and classrooms for the dropdown options
        subject_results, classroom_results = get_subject_and_classroom_dashboard(objective_matches)
        
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
        print('------------')
        print(week_info)
        print('------------')
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
    week_of = current_week = date.today().isocalendar()[1]

    lesson_id = int(lesson_id)
    if lesson_id == 0:
        return redirect('create_objective', user_id=user_profile.id, week_of=week_of)
    else:
        
        lesson_match = lessonObjective.objects.get(id=lesson_id)
        classroom_match = lesson_match.lesson_classroom_id
        classroom_profile = classroom.objects.filter(id=classroom_match).first()

        lesson_topics = topicInformation.objects.filter(id__in=lesson_match.objectives_topics.all())

        new_text, created = lessonText.objects.get_or_create(matched_lesson=lesson_match)
        
        selected_activities = selectedActivity.objects.filter(lesson_overview=lesson_match, is_selected=True)
        big_questions = googleRelatedQuestions.objects.filter(lesson_plan=lesson_match, is_selected=True)
        youtube_search = youtube_results(lesson_match.teacher_objective, lesson_id)
        
        youtube_list = []
        if youtube_search:
            youtube_list = youtube_search[:3]
        
        vid_id_list = []
        vi_list = []
        for result in youtube_list:
            link = result['link']
            if link:
                vid_id = video_id(link)
                youtube_create, created = youtubeSearchResult.objects.get_or_create(lesson_plan=lesson_match, title=result['title'], link=link, vid_id=vid_id)
                vi_list.append(youtube_create.id)
                vid_id_list.append(youtube_create)


        video_match = youtubeSearchResult.objects.filter(id__in=vi_list, is_selected=True)

        form = UserSearchForm()
        context = {'user_profile': user_profile, 'video_match': video_match, 'lesson_topics': lesson_topics, 'form': form, 'new_text': new_text, 'big_questions': big_questions, 'vid_id_list': vid_id_list, 'classroom_profile': classroom_profile, 'selected_activities': selected_activities, 'lesson_match': lesson_match}
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
    week_of = current_week = date.today().isocalendar()[1] 
    is_new = False
    lesson_id = int(lesson_id)
    matched_questions = []
    question_match = []
    current_question = []
    get_worksheet = worksheetFull.objects.filter(id=worksheet_id).first()
    if get_worksheet:
        question_matches = get_worksheet.questions.all()
    else:
        question_matches = None

    if question_matches:
        all_matched_questions = topicQuestionitem.objects.filter(id__in=question_matches)

        for item in all_matched_questions:
            question = item.Question
            if question:
                pass
            else:
                image = item.Question_Image
                if image:
                    pass
                else:
                    get_worksheet.questions.remove(item) 
                    item.delete()

    classroom_profile = classroom.objects.get(id=class_id)
    grade_list = classroom_profile.grade_level.all()
    grade_match = gradeLevel.objects.filter(id__in=grade_list).first()
    standard_match = standardSet.objects.get(id=classroom_profile.standards_set_id)

    lesson_match = lessonObjective.objects.get(id=lesson_id)
    subject_match = lesson_match.subject_id
    subject_match_full = standardSubjects.objects.get(id=subject_match) 

    worksheet_title = '%s: %s for week of %s' % (user_profile, subject_match_full, current_week)
    get_worksheet, created = worksheetFull.objects.get_or_create(created_by=user_profile, lesson_overview=lesson_match, title=worksheet_title, subject=subject_match_full)
    get_worksheet.lesson_overview = lesson_match
    question_matches = get_worksheet.questions.all()

    check_lesson_questions = topicQuestionitem.objects.filter(id__in=question_matches)

    if check_lesson_questions:
        all_matched_questions = topicQuestionitem.objects.filter(lesson_overview=lesson_match)
        matched_questions = topicQuestionitem.objects.filter(id__in=question_matches)
    else:
        text_questions_one = get_question_text(lesson_id, user_profile)
        matched_questions = topicQuestionitem.objects.filter(id__in=text_questions_one).order_by('?')[:10]
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

        all_matched_questions = topicQuestionitem.objects.filter(id__in=text_questions_one)

    lesson_standards = singleStandard.objects.filter(id__in=lesson_match.objectives_standards.all())
    topic_matches = lesson_match.objectives_topics.all()
    topic_lists_selected = topicInformation.objects.filter(id__in=topic_matches).order_by('item')
    topic_images = []
    for tp in topic_lists_selected:
        if tp.image_url:
            pass
        else:
            tp_image = get_possible_images(tp.item, tp.id)

    if 'None' in question_id:
        question_match = current_question = None
        next_q = 1
        question_id = 0
    elif 'New' in question_id:
        is_new = True
        question_match = current_question =  topicQuestionitem.objects.create(created_by=user_profile, subject=subject_match_full, is_admin=False)
        get_worksheet.questions.add(question_match)
        q = 0 
        next_q = 1
    else:
        if matched_questions:
            q = int(question_id)
            next_q = q + 1
            question_match = current_question = matched_questions[q]
        elif 'New' in question_id:
            is_new = True
            q = 0
            next_q = 1
            question_match = current_question =  topicQuestionitem.objects.create(created_by=user_profile, subject=subject_match_full, is_admin=False)
            get_worksheet.questions.add(question_match)
        else:
            question_match = current_question = None
            next_q = 1
            question_id = 0

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


    
    
    

    if 'False' in act_id:
        pass
    else:
        question_match = current_question = topicQuestionitem.objects.get(id=act_id)

    if question_match:
        question_match_id = question_match.id
    else:
        question_match_id = 0
    #selected_images = userImageUpload.objects.filter()
    recent_uploads = userImageUpload.objects.filter(created_by=user_profile).order_by('-uploaded_date')        

    recent_uploads = recent_uploads[:10]
    worksheet_theme = worksheetTheme.objects.get(id=1)

    img_id = worksheet_theme.background_image

    background_img = userImageUpload.objects.filter(id=worksheet_theme.background_image_id).first()
    form = UserSearchForm()
    return render(request, 'dashboard/activity_builder_2.html', {'user_profile': user_profile, 'week_of': week_of, 'is_new': is_new, 'form': form, 'recent_uploads': recent_uploads, 'get_worksheet': get_worksheet, 'all_matched_questions': all_matched_questions, 'question_match': question_match, 'question_id': question_id, 'next_q': next_q, 'background_img': background_img, 'worksheet_theme': worksheet_theme, 'current_question': current_question, \
                                                                 'matched_questions': matched_questions, 'question_match_id': question_match_id, 'subject_match_full': subject_match_full, 'current_week': current_week, 'page': page, 'class_id': class_id, 'subject': subject, 'lesson_id': lesson_id, \
                                                                  'short_answer': short_answer, 'fib':fib, 'multi_choice':multi_choice, 'unknown':unknown})


def BlankDigitalActivities(request, user_id=None, worksheet_id=None, page=None, question_id=None):
    page = 'Preview'
    current_week = date.today().isocalendar()[1] 
    user_profile = User.objects.filter(id=user_id).first()
    week_of = current_week = date.today().isocalendar()[1] 

    worksheet_match = worksheetFull.objects.filter(id=worksheet_id).first()


    subject_match_full = standardSubjects.objects.get(id=worksheet_match.subject_id) 
    matched_questions = []
    if worksheet_match:
        question_matches = worksheet_match.questions.all()

        if question_matches:
            m_questions = topicQuestionitem.objects.filter(id__in=question_matches)
            for item in m_questions:
                matched_questions.append(item)
        else:
            new_question = topicQuestionitem.objects.create(created_by=user_profile, subject=subject_match_full, Question='Click Here to Add Question', is_admin=False)
            worksheet_match.questions.add(new_question)
            matched_questions.append(new_question)
    else:
        worksheet_title = '%s: %s %s for week of %s' % (user_profile, subject_match_full, current_week)
        worksheet_match = worksheetFull.objects.filter(created_by=user_profile, title=worksheet_title)
        if worksheet_match:
            worksheet_count = worksheet_match.count()
            new_num = worksheet_count + 1 
            worksheet_title = '%s: %s %s for week of %s - (%s)' % (user_profile, subject_match_full, current_week, new_num)
        else:
            worksheet_match = worksheetFull.objects.create(created_by=user_profile, title=worksheet_title, subject=subject_match_full)
            

        new_question = topicQuestionitem.objects.create(created_by=user_profile, subject=subject_match_full, Question='Click Here to Add Question', is_admin=False)
        worksheet_match.questions.add(new_question)
        matched_questions.append(new_question)


    if matched_questions:
        if 'None' in question_id:
            q = 0
        else:
            q = int(question_id)
            question_match = matched_questions[q]

        next_q = q + 1
        
    else:
        question_match = None

    lesson_id = 0
    class_id = 0
    print('==============')
    print(matched_questions)
    print('==============')
    return render(request, 'dashboard/new_worksheet_builder.html', {'page': page, 'week_of': week_of, 'class_id': class_id, 'lesson_id': lesson_id, 'subject_match_full': subject_match_full, 'matched_questions': matched_questions, 'worksheet_match': worksheet_match, 'user_profile': user_profile})

#Edit already created or recommended Question
def EditQuestions(request, user_id=None, class_id=None, subject=None, lesson_id=None, worksheet_id=None, page=None, act_id=None, question_id=None):
    user_profile = User.objects.get(id=user_id)
    worksheet_match = worksheetFull.objects.get(id=worksheet_id)
    question_match = topicQuestionitem.objects.get(id=question_id)
    current_question = topicQuestionitem.objects.get(id=question_id)
    if question_match.is_admin:
        current_question.pk = None
        current_question.save()
        current_question.original_num = question_match.id
        current_question.is_admin = False
        current_question.save()
        worksheet_match.questions.remove(question_match)
        worksheet_match.questions.add(current_question)
    else:
        current_question = question_match


    question_type = question_match.question_type
   
    
    subject_match = standardSubjects.objects.get(id=subject)
    if request.method == "POST":
        form = topicQuestionitemForm(request.POST, request.FILES, instance=current_question)

        if form.is_valid():
            prev = form.save(commit=False)
            prev.save()

            

    return redirect('digital_activities', user_id=user_id, class_id=class_id, lesson_id=lesson_id, subject=1, page='Preview', worksheet_id=worksheet_id, act_id='False', question_id=0)


#create new question from scratch
def NewQuestions(request, user_id=None, class_id=None, subject=None, lesson_id=None, worksheet_id=None, page=None, act_id=None, question_id=None):
    user_profile = User.objects.get(id=user_id)
    worksheet_match = worksheetFull.objects.get(id=worksheet_id)
    current_question = topicQuestionitem.objects.create(created_by=user_profile, is_admin=False)
    worksheet_match.questions.add(current_question)

    subject_match = standardSubjects.objects.get(id=subject)
    if request.method == "POST":
        form = topicQuestionitemForm(request.POST, request.FILES, instance=current_question)

        if form.is_valid():
            prev = form.save(commit=False)
            prev.save()

            
        return redirect('digital_activities', user_id=user_id, class_id=class_id, lesson_id=lesson_id, subject=1, page='Preview', worksheet_id=worksheet_id, act_id='False', question_id=0)


def CreateClassroomAssignment(request, user_id=None, week_of=None, class_id=None, worksheet_id=None, lesson_id=None, assign_id=None, step=None):
    user_profile = User.objects.get(id=user_id)
    worksheet_match = worksheetFull.objects.get(id=worksheet_id)
    all_classrooms = classroom.objects.filter(main_teacher=user_profile)
    selected_classrooms = []
    if 'None' in assign_id:
        pass
    else:
        assignment_match = worksheetClassAssignment.objects.get(id=assign_id)
        s_classrooms = assignment_match.assigned_classrooms.all()
        if s_classrooms:
            selected_classrooms = classroom.objects.filter(id__in=s_classrooms)
            all_classrooms = all_classrooms.exclude(id__in=s_classrooms)
    
    s_theme = worksheet_match.worksheet_theme_id
    if s_theme:
        selected_theme = worksheetTheme.objects.get(id=s_theme)
    else:
        selected_theme = None

    current_year = datetime.datetime.now().year
    current_academic_year = academicYear.objects.filter(planning_teacher=user_profile, is_active=True).first()

    if 'None' in class_id:
        classroom_profile = None
    else:
        class_id = int(class_id)
        if class_id == 0:
            classroom_profile = None
        else:
            classroom_profile = classroom.objects.get(id=class_id)

    print(lesson_id, '=============')
    if 'None' in lesson_id:
        lesson_match = None
    else:
        lesson_id = int(lesson_id)
        if lesson_id == 0:
            lesson_match = None
        else:
            lesson_match = lessonObjective.objects.get(id=lesson_id)

    
    worksheet_themes = worksheetTheme.objects.filter(is_admin=True, is_active=True)
    image_list = []
    for item in worksheet_themes:
        image_result = item.demo_image_id
        image_list.append(image_result)

    
    image_ids = userImageUpload.objects.filter(id__in=image_list)
    if request.method == "POST":
        form = classroomAssignmentForm(request.POST, request.FILES)

        if form.is_valid():
            worksheet_title = form.cleaned_data.get('worksheet_title')
            worksheet_description = form.cleaned_data.get('worksheet_description')
            worksheet_date = form.cleaned_data.get('worksheet_date')

            worksheet_match.title = worksheet_title
            worksheet_match.ws_description = worksheet_description
            worksheet_match.save()

            if lesson_match:
                assignment_match, created = worksheetClassAssignment.objects.get_or_create(lesson_overview=lesson_match, subject=worksheet_match.subject, week_of=week_of, created_by=user_profile, worksheet_full=worksheet_match, academic_year=current_academic_year)
            else:
                assignment_match, created = worksheetClassAssignment.objects.get_or_create(subject=worksheet_match.subject, week_of=week_of, created_by=user_profile, worksheet_full=worksheet_match, academic_year=current_academic_year)

            assignment_match.due_date = worksheet_date
            assignment_match.total_possible = worksheet_match.total_possible
            assignment_match.save()

            return redirect('create_classroom_assignment', user_id=user_profile.id, week_of=week_of, class_id=class_id, worksheet_id=worksheet_id, lesson_id=lesson_id, assign_id=assignment_match.id, step='TWO')
    else:
        form = classroomAssignmentForm()

    context = {'form': form, 'week_of': week_of, 'all_classrooms': all_classrooms, 'selected_classrooms': selected_classrooms, 'selected_theme': selected_theme, 'step': step, 'user_profile': user_profile, 'assign_id': assign_id, 'class_id': class_id, 'subject': worksheet_match.subject, 'worksheet_match': worksheet_match, 'lesson_id': lesson_id, 'worksheet_themes': worksheet_themes, 'image_ids': image_ids}
    return render(request, 'dashboard/create_assignments.html', context)


def AddThemeAssignment(request, user_id=None, week_of=None, class_id=None, worksheet_id=None, lesson_id=None, assign_id=None, step=None, theme_id=None):
    user_profile = User.objects.get(id=user_id)
    worksheet_match = worksheetFull.objects.get(id=worksheet_id)

    theme_match = worksheetTheme.objects.get(id=theme_id)
    worksheet_match.worksheet_theme = theme_match
    worksheet_match.save()
    return redirect('create_classroom_assignment', user_id=user_profile.id, week_of=week_of, class_id=class_id, worksheet_id=worksheet_id, lesson_id=lesson_id, assign_id=assign_id, step='TWO')

def AddClassroomAssignment(request, user_id=None, week_of=None, class_id=None, worksheet_id=None, lesson_id=None, assign_id=None, step=None):
    user_profile = User.objects.get(id=user_id)
    worksheet_match = worksheetClassAssignment.objects.get(id=assign_id)

    classroom_match = classroom.objects.get(id=class_id)

    worksheet_match.assigned_classrooms.add(classroom_match)
    return redirect('create_classroom_assignment', user_id=user_profile.id, week_of=week_of, class_id=classroom_match.id, worksheet_id=worksheet_id, lesson_id=lesson_id, assign_id=assign_id, step='THREE')


############################################
#Student Functions
############################################


#student begin worksheet 
def StudentWorksheetStart(request, lesson_id=None, worksheet_id=None, question_id=None):
    user_profile = User.objects.filter(id=request.user.id).first()
    worksheet_match = worksheetFull.objects.get(id=worksheet_id)
    if user_profile:
        question_matches = worksheet_match.questions.all()
        matched_questions = topicQuestionitem.objects.filter(id__in=question_matches)
        student_profile_match, created  = studentProfiles.objects.get_or_create(student_username=user_profile)
        student_answer_sheet, created = studentWorksheetAnswerFull.objects.get_or_create(student=user_profile, student_profile=student_profile_match, worksheet_assignment=worksheet_match)
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
    matched_questions = topicQuestionitem.objects.filter(id__in=question_matches)
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
    worksheet_id = 0
    lesson_id = 0
    ref_id = 0

    #alerts have the format: 
    #<h6 class="card-title">Sticker recieved!</h6><h6 class="card-subtitle mb-2 text-muted"">From teacher A. Click <a href='#'>here</a> to view</h6>
    #get all alerts for the student
    all_alerts = alertMessage.objects.filter(sent_to=user_profile)
    num_alerts = len(all_alerts)
    if num_alerts > 3:
        top_alerts = all_alerts[0:2]
    else:
        top_alerts = all_alerts



    context = {'user_profile': user_profile, 'ref_id':ref_id, 'worksheet_id': worksheet_id, 'lesson_id':lesson_id, \
               'form': form, 'form2': form2, 'all_alerts': all_alerts, 'top_alerts': top_alerts}

    return render(request, 'dashboard/student_main.html', context)


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
def StudentPerformance(request, user_id, class_id, week_of, standard_id):
    all_themes = studentPraiseTheme.objects.all()
    user_profile = User.objects.get(id=user_id)
    standard_set = user_profile.standards_set
    current_year = datetime.datetime.now().year
    current_week = date.today().isocalendar()[1]
    start = current_week - 12
    if start < 1:
        start = 1
    
    teacher_classes = classroom.objects.filter(main_teacher=user_profile)
    teacher_class_id = classroom.objects.filter(main_teacher=user_profile).values_list('id', flat=True)
    
    if 'All' in standard_id:
        worksheet_matches = worksheetFull.objects.filter(created_by=user_profile)
    else:
        lesson_match = lessonObjective.objects.filter(lesson_classroom__in=teacher_classes, objectives_standards=standard_id)
        print(lesson_match)
        worksheet_matches = worksheetFull.objects.filter(lesson_overview__in=lesson_match)


    worksheet_results = []
    for ws in worksheet_matches:
        ws_info = get_worksheet_performance(ws)
        worksheet_results.append(ws_info)

    all_grades = []
    all_subjects = []

    for t_class in teacher_classes:
        g_levels = t_class.grade_level.all()
        s_levels = t_class.subjects.all()
        if s_levels:
            for sl in s_levels:
                all_subjects.append(sl.id)
        for gl in g_levels:
            all_grades.append(gl.id)  
        s_level = t_class.single_grade
        all_grades.append(s_level.id)

    subject_options = standardSubjects.objects.filter(id__in=all_subjects).order_by('subject_title')
    grade_options = gradeLevel.objects.filter(id__in=all_grades).order_by('grade')

    
    week_breakdown = get_weekly_brackets(user_id, start, current_week, current_year)
    if week_breakdown:
        pass
    else:
        week_breakdown['low'] =  [ 2, 1, 2, 1, 2, 3, 4, 4, 2, 4, 3, 3]
        week_breakdown['mid'] =  [14,12,11,14,10,12,14,13,13,14,13,15]
        week_breakdown['high'] = [ 4, 7, 7, 5, 8, 5, 2, 3, 5, 2, 4, 2]
    
    top_lessons = get_demo_ks_brackets(user_id, start, current_week, current_year)
    student_results = get_student_results(user_id, start, current_week, current_year)

    if request.method == "POST":
        form = worksheetFullForm(request.POST, request.FILES)
        if form.is_valid():
            prev = form.save(commit=False)
            prev.created_by = user_profile
            prev.standards_set = standard_set 
            if user_profile.is_superuser:
                prev.is_admin = True
            else:
                prev.is_admin = False
            prev.save()
            return redirect('new_digital_activities', user_id=user_id, worksheet_id=prev.id, question_id=0, page='Preview')
    else:
        form = worksheetFullForm()
    return render(request, 'dashboard/assignments.html', {'user_profile': user_profile, 'worksheet_results': worksheet_results, 'worksheet_matches': worksheet_matches, 'form': form, 'subject_options': subject_options, 'grade_options': grade_options, 'all_themes': all_themes, 'week_breakdown': week_breakdown, 'top_lessons': top_lessons, 'student_results': student_results})

def SingleAssignment(request, user_id=None, classroom_id=None, worksheet_id=None):
    user_profile = User.objects.filter(username=request.user.username).first()
    worksheet_match = worksheetFull.objects.get(id=worksheet_id)
    classroom_match = classroom.objects.get(id=classroom_id)
    

####### these functions handle the students answers as they go through the digital worksheet #########
#selected the multiple choice answer in worksheet question
def StudentMCSelect(request, user_id=None, lesson_id=None, worksheet_id=None):

    if request.method == 'GET':
        user_profile = User.objects.filter(username=request.user.username).first()
        worksheet_match = worksheetFull.objects.get(id=worksheet_id)
        student_profile_match = studentProfiles.objects.get_or_create(student_username=user_profile)
        student_answer_key, created = studentWorksheetAnswerFull.objects.get_or_create(student=user_profile, student_profile=student_profile_match, worksheet_assignment=worksheet_match)
       
       
        user_id = user_profile.id
        question_id = request.GET['question_id']
        question = request.GET['question']
        answer = request.GET['answer']
        match_question = topicQuestionitem.objects.get(id=question_id)
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
        student_profile_match = studentProfiles.objects.get_or_create(student_username=user_profile)
        student_answer_key, created = studentWorksheetAnswerFull.objects.get_or_create(student=user_profile, student_profile=student_profile_match, worksheet_assignment=worksheet_match)
       
        match_question = topicQuestionitem.objects.get(id=question_id)
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
        student_profile_match = studentProfiles.objects.get_or_create(student_username=user_profile)
        student_answer_key, created = studentWorksheetAnswerFull.objects.get_or_create(student=user_profile, student_profile=student_profile_match, worksheet_assignment=worksheet_match)
       
        match_question = topicQuestionitem.objects.get(id=question_id)
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
        try:
            update_lesson_analytics = get_lesson_sections(overview, less_class, lesson_id, user.id)
            message = 'Saved'
        except:
            message = 'Not Saved'

        now = datetime.datetime.now().strftime('%H:%M:%S')
        sent = ' %s: %s' % (message, now)
        context = {"data": sent}
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
        
        match_recs = reccomendedTopics.objects.filter(matched_lesson=lesson_match).first()
        sing_recs = match_recs.single_score.all()
        sing_match = singleRec.objects.filter(id__in=sing_recs)
        rec_top_match = sing_match.filter(single_rec_topics_id=topic_id).first()
        rec_rec = match_recs.single_score.remove(rec_top_match)
        add_remove = match_recs.removed_topics.add(topic_match)
        remove_rec = match_recs.rec_topics.remove(topic_match)
        
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
        if description_list:
            final = "<ul>%s</ul>" % (description_list)
            if final:
                message = '<strong>%s</strong> has been added!' % (topic_match.item)
                context = {'term': topic_match.item, 'description': final, 'message': message}
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
        sr_full = singleRec.objects.filter(id__in=match_score)
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
                sr_match = sr_full.filter(single_rec_topics=top)
                for sr in sr_match:
                    rec_rec = match_recs.single_score.remove(sr)
                add_remove = match_recs.removed_topics.add(top)
                remove_rec = match_recs.rec_topics.remove(top)
        

        match_recs = reccomendedTopics.objects.filter(matched_lesson=lesson_match).first()
        match_score = match_recs.single_score.all()
        single_recs = singleRec.objects.filter(id__in=match_score)
        match_score_count = match_score.count() 
        update_term_list = []
        if match_score_count >= 10:
            for rec in single_recs[:15]:
                single_rec = rec.single_rec_topics_id
                match_topic = topicInformation.objects.get(id=single_rec)
                descriptions = get_description_string(match_topic.id, user_profile.id)
                result = {'id': match_topic.id, 'term': match_topic.item, 'descriptions': descriptions} 
                if result not in update_term_list:
                    update_term_list.append(result)
        
        else:
            #pulls from acivity_builder.py
            update_term_list = generate_term_recs(teacher_input, class_id, lesson_id, user_profile.id)

        context = {"data": update_term_list, "message": "your message"}

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

#this is the summary on dropdowns that covers diffrentiation, engagement, retention, and alignment
def GetStandardsAnalytics(request, lesson_id):
    if request.method == 'GET':
        user_profile = User.objects.filter(id=request.user.id).first()
        #goes to get_activities.py
        stand_analytics = get_standards_analytics(lesson_id)
        stand_analytics = int(math.ceil(stand_analytics))
        print(stand_analytics)
        context = {"data": stand_analytics}
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


def GetSatndardsAnalytics(request, lesson_id):
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
        match_recs = reccomendedTopics.objects.filter(matched_lesson=lesson_match).first()
        if match_recs:
            match_score = match_recs.single_score.all()
            single_recs = singleRec.objects.filter(id__in=match_score)
            match_score_count = match_score.count() 
        else:
            match_score = None
            match_score_count = 0
        update_term_list = []

        if match_score_count >= 10:
            for rec in single_recs[:15]:
                single_rec = rec.single_rec_topics_id
                match_topic = topicInformation.objects.filter(id=single_rec).first()
                if match_topic:
                    descriptions = get_description_string(match_topic.id, user_profile.id)
                    if descriptions:
                        result = {'id': match_topic.id, 'term': match_topic.item, 'descriptions': descriptions} 
                        if result not in update_term_list:
                            update_term_list.append(result)
        else:
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


def GoogleImageSearch(request, worksheet_id, question_id):

    # request should be ajax and method should be POST.
    if request.method == "POST":
        # get the form data
        form = UserSearchForm(request.POST)
        # save the data and after fetch the object in instance
        if form.is_valid():
            # serialize in new friend object in json
            q = form.cleaned_data.get('search_item')
            search_ref = form.cleaned_data.get('search_ref')
            search_results = get_search_images(q, search_ref)
            # send to client side.
            context = {"data": search_results, "message": "your message"}
            
            return JsonResponse(context)
        else:
            # some form errors occured.
            return JsonResponse({"error": form.errors}, status=400)

    else:
        return HttpResponse("Request method is not a GET")


def SearchKeyTerm(request, lesson_id):
    user_profile = User.objects.filter(id=request.user.id).first()
    class_objectives = lessonObjective.objects.get(id=lesson_id)

    topic_matches = class_objectives.objectives_topics.all()
    topics = topicInformation.objects.filter(id__in=topic_matches)

    # request should be ajax and method should be POST.
    if request.method == "POST":
        # get the form data
        form = UserSearchForm(request.POST)
        # save the data and after fetch the object in instance
        if form.is_valid():
            # serialize in new friend object in json
            q = form.cleaned_data.get('search_item')
            search_ref = form.cleaned_data.get('search_ref')
            search_results = search_wiki_topics(topics, lesson_id, user_profile, q)
            print('------------')
            print(search_results)
            print('------------')
            # send to client side.
            context = {"data": search_results, "message": "your message"}
            
            return JsonResponse(context)
        else:
            # some form errors occured.
            return JsonResponse({"error": form.errors}, status=400)

    else:
        return HttpResponse("Request method is not a GET")


def AddQuestionImage(request, class_id=None, lesson_id=None, subject=None, worksheet_id=None, question_id=None):

    current_date = datetime.datetime.now()
    worksheet_match = worksheetFull.objects.get(id=worksheet_id)
    user_profile = User.objects.filter(username=request.user.username).first()

    question_id = int(question_id)
    question_match = topicQuestionitem.objects.get(id=question_id)
    if request.method == 'GET':
        title = request.GET['title']
        d_url = request.GET['d_url']
        img_ref = request.GET['img_ref']


        create_image, created = userImageUpload.objects.get_or_create(image_url=d_url, title=title, created_by=user_profile, uploaded_date=current_date)
        img_ref = int(img_ref)
        if img_ref == 1:
            question_match.Question_Image = create_image
            question_match.save()
        if img_ref == 2:
            question_match.correct_image = create_image
            question_match.save()

        worksheet_match.questions.add(question_match)
        question_image = str(question_match.Question_Image)
        correct_one = str(question_match.correct_image)
        context = {'question': question_image, 'correct_image': correct_one}

         
        return JsonResponse(context)
 
    else:
        return HttpResponse("Request method is not a GET")
#############################################################
######    End Data Analytics and Ai powered functions #######
#############################################################



def SupAdDash(request):
    user_profile = User.objects.filter(username=request.user.username).first()

    page = 'Dashboard'
    return render(request, 'administrator/admin_dashboard.html', {'user_profile': user_profile, 'page': page})


def AdminActivityPreview(request, act_temp=None, demo_type=None, topic_type=None, subject=None, grade=None):
    user_profile = User.objects.filter(username=request.user.username).first()

    demo_all = LearningDemonstrationTemplate.objects.all().order_by('content')
    act_all = lessonTemplates.objects.all().order_by('wording')

    if 'All' in subject:
        subject_match = standardSubjects.objects.all()
    else:
        subject_match = standardSubjects.objects.filter(id=subject)

    if 'All' in grade:
        grade_match = gradeLevel.objects.all()
    else:
        grade_match = gradeLevel.objects.filter(id=grade)


    if 'All' in topic_type:
        tt_match = topicTypes.objects.all()
    else:
        tt_match = topicTypes.objects.filter(id=topic_type)

    if 'All' in demo_type:
        demo_match = None
        if 'All' in act_temp:
            act_match = lessonTemplates.objects.filter(components__in=tt_match).order_by('?')
            act_s = act_match.first()
            if act_s:
                topic_component = act_s.components.all()
                single_topic_type = topicTypes.objects.filter(id__in=topic_component).first()
                tt = single_topic_type.id
                subject_m = act_s.subject
                grade_m = act_s.grade_level
                topic_match = topicInformation.objects.filter(topic_type=tt)
                demo_match = LearningDemonstrationTemplate.objects.filter(topic_type=tt)
         
        else:
            act_match = lessonTemplates.objects.filter(id=act_temp)
            act_s = lessonTemplates.objects.get(id=act_temp)
            if act_s:
                topic_component = act_s.components.all()
                single_topic_type = topicTypes.objects.filter(id__in=topic_component).first()
                tt = single_topic_type.id
                subject_m = act_s.subject
                grade_m = act_s.grade_level
                topic_match = topicInformation.objects.filter(topic_type=tt)
                demo_match = LearningDemonstrationTemplate.objects.filter(topic_type=tt)

    else:
        demo_match = LearningDemonstrationTemplate.objects.filter(id=demo_type).order_by('?')
        demo_m = demo_match.first()
        topic_component = demo_m.topic_type.all()
        single_topic_type = topicTypes.objects.filter(id__in=topic_component).first()
        tt = single_topic_type.id
        subject_m = demo_m.subject
        grade_m = demo_m.grade_level
        topic_match = topicInformation.objects.filter(topic_type=tt)
        act_match = lessonTemplates.objects.filter(components=tt)

    demo_string = None
    act_string = None
 
   
    single_topic = 'None'
    single_demo = 'None'
    single_act = 'None'

    
    if demo_match and topic_match:
        single_topic = topic_match.order_by('?')[0]
        topic_string = single_topic.item
        topic_component = single_topic.topic_type.all()
        single_topic_type = topicTypes.objects.filter(id__in=topic_component).first()
        tt_comp = single_topic_type.item
        single_demo = demo_match.order_by('?')[0]
        d_string = single_demo.content
        demo_string = d_string.replace(tt_comp, topic_string)
        wording_split = demo_string.split()
        first_word = wording_split[0]
        tokens = nlp(first_word)
        new_verb = tokens[0]._.inflect('VBG')
        demo_full = demo_string.replace(first_word, new_verb) 

        if act_match:
            single_act = act_match.order_by('?')[0]
            sent_string = single_act.wording
            act_string = sent_string.replace('DEMO_KS', demo_full)
        else:
            act_string = None



    page = 'Preview'
    return render(request, 'administrator/admin_dashboard.html', {'user_profile': user_profile, 'act_string': act_string, 'single_topic': single_topic, 'single_demo':single_demo, 'single_act':single_act, 'demo_string': demo_string,  'demo_all': demo_all, 'act_all': act_all,  'page': page, 'act_match': act_match, 'tt_match': tt_match, 'grade_match': grade_match, 'subject_match': subject_match})



def AddSingleTopic(request, top_id=None, act_type=None):
    user_profile = User.objects.filter(username=request.user.username).first()
    page = 'Topic'
    if 'Edit' in act_type:
        top_match = topicInformation.objects.get(id=top_id)
        if request.method == "POST":

            form4 = topicInformationForm(request.POST, instance=top_match)
            if form4.is_valid():
                prev = form4.save()

                return redirect('add_gs', act_id=prev.id, act_type='Topic')

        else:

            form4 = topicInformationForm(instance=top_match)
        return render(request, 'administrator/admin_dashboard.html', {'user_profile': user_profile, 'form4': form4, 'page': page, 'top_match': top_match})

    else:
        if request.method == "POST":

            form4 = topicInformationForm(request.POST)
            if form4.is_valid():
                prev = form4.save()

                return redirect('add_gs', act_id=prev.id, act_type='Topic')

        else:

            form4 = topicInformationForm()
        return render(request, 'administrator/admin_dashboard.html', {'user_profile': user_profile, 'form4': form4, 'page': page, 'all_demos': all_demos})



def AddDemoKSTemplate(request, act_id=None, act_type=None):
    user_profile = User.objects.filter(username=request.user.username).first()
    all_demos = LearningDemonstrationTemplate.objects.all().order_by('content')
    page = 'Demo'
    if 'Edit' in act_type:
        act_match = LearningDemonstrationTemplate.objects.get(id=act_id)
        content_match = act_match.content
        if request.method == "POST":

            form2 = LearningDemonstrationTemplateForm(request.POST, instance=act_match)
            if form2.is_valid():
                prev = form2.save()
                
                other_matches = LearningDemonstrationTemplate.objects.filter(content=content_match).exclude(id=act_id).delete()
                return redirect('add_gs', act_id=prev.id, act_type='Demo')

        else:

            form2 = LearningDemonstrationTemplateForm(instance=act_match)
        return render(request, 'administrator/admin_dashboard.html', {'user_profile': user_profile, 'form2': form2, 'page': page, 'all_demos': all_demos})

    else:
        if request.method == "POST":

            form2 = LearningDemonstrationTemplateForm(request.POST)
            if form2.is_valid():
                prev = form2.save()

                return redirect('add_gs', act_id=prev.id, act_type='Demo')

        else:

            form2 = LearningDemonstrationTemplateForm()
        return render(request, 'administrator/admin_dashboard.html', {'user_profile': user_profile, 'form2': form2, 'page': page, 'all_demos': all_demos})

def AddActivityTemplate(request, act_id=None, act_type=None):
    user_profile = User.objects.filter(username=request.user.username).first()

    all_lessons = lessonTemplates.objects.all().order_by('wording')
    page = 'Activity'
    if 'Edit' in act_type:
        act_match = lessonTemplates.objects.get(id=act_id)        
        content_match = act_match.wording
        
        if request.method == "POST":

            form = lessonTemplatesForm(request.POST, instance=act_match)
            if form.is_valid():
                prev = form.save()
                other_matches = lessonTemplates.objects.filter(wording=content_match).exclude(id=act_id).delete()
                return redirect('add_gs', act_id=prev.id, act_type='Activity')

        else:

            form = lessonTemplatesForm(instance=act_match)
        return render(request, 'administrator/admin_dashboard.html', {'user_profile': user_profile, 'form': form, 'page': page})

    else:
        if request.method == "POST":

            form = lessonTemplatesForm(request.POST)
            if form.is_valid():
                prev = form.save()

                return redirect('add_gs', act_id=prev.id, act_type='Activity')

        else:

            form = lessonTemplatesForm()
        return render(request, 'administrator/admin_dashboard.html', {'user_profile': user_profile, 'all_lessons': all_lessons, 'form': form, 'page': page})


def SelectGradeSubjectAdmin(request, act_id=None, act_type=None):
    user_profile = User.objects.filter(username=request.user.username).first()

    page = 'GradeSubject'
    if 'Demo' in act_type:
        act_match = LearningDemonstrationTemplate.objects.get(id=act_id)
        content_match = act_match.content
        t_types = act_match.topic_type.all()
    elif 'Topic' in act_type:
        act_match = topicInformation.objects.get(id=act_id)
        t_types = act_match.topic_type.all()

        tt_list = topicTypes.objects.filter(id__in=t_types)
        if request.method == "POST":
            
            form3 = multiSelectGSForm(request.POST)
            
            if form3.is_valid():
                prev = form3.save()
                subjects = prev.subject
                grades = prev.grade_level
                
                for grd in grades.all():
                    for sub in subjects.all():
                        act_match = act_match
                        act_match.id = None
                        act_match.save()
                        act_match.grade_level = grd
                        act_match.subject = sub
                        act_match.save()
                        for tt in tt_list:
                            act_match.topic_type.add(tt)
                            
                return redirect('sup_admin_dashboard')
    else:
        act_match = lessonTemplates.objects.get(id=act_id)
        t_types = act_match.components.all()

    tt_list = topicTypes.objects.filter(id__in=t_types)
    if request.method == "POST":

        form3 = multiSelectGSForm(request.POST)
        if form3.is_valid():
            prev = form3.save()
            subjects = prev.subject
            grades = prev.grade_level
            
            for grd in grades.all():
                for sub in subjects.all():
                    current_act = act_match
                    current_act.id = None
                    current_act.save()
                    current_act.grade_level = grd
                    current_act.subject = sub
                    current_act.save()
                    for tt in tt_list:
                        if 'Demo' in act_type: 
                            current_act.topic_type.add(tt)
                        else:
                            current_act.components.add(tt)
            
            
            return redirect('sup_admin_dashboard')

    else:

        form3 = multiSelectGSForm()
    return render(request, 'administrator/admin_dashboard.html', {'user_profile': user_profile, 'form3': form3, 'page': page})



def DeleteAdminPlanning(request, act_id=None, act_type=None):
    user_profile = User.objects.filter(username=request.user.username).first()


    if 'Demo' in act_type:
        act_match = LearningDemonstrationTemplate.objects.get(id=act_id)
        content_match = act_match.content
        other_matches = LearningDemonstrationTemplate.objects.filter(content=content_match).delete()

    else:
        act_match = lessonTemplates.objects.get(id=act_id)
        content_match = act_match.wording
        other_matches = lessonTemplates.objects.filter(wording=content_match).delete()

    return redirect('sup_admin_dashboard')
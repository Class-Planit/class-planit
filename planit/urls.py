try:
    from django.conf.urls import url
except ImportError:
    from django.urls import re_path as url

from django.conf import settings
if getattr(settings, 'POSTMAN_I18N_URLS', False):
    from django.utils.translation import pgettext_lazy
else:
    def pgettext_lazy(c, m): return m

from django.urls import path, include, re_path
from django.conf.urls import url
from django.urls import reverse_lazy
from .views import *



urlpatterns = [

    url(r'^$',
        view=Homepage,
        name='homepage'),

    url(r'^full-form/(?P<retry>[\w\s]+)/',
        view=FormFull,
        name='registration_full'),


    url(r'^questionnaire/',
        view=QuestionnaireFull,
        name='questionnaire_full'),

    url(r'^dashboard/(?P<week_of>[\w\s]+)/',
        view=Dashboard.as_view(),
        name='Dashboard'),

    url(r'^how-it-works/',
        view=HowItWorks.as_view(),
        name='how_it_works'),

    url(r'^services/',
        view=Services.as_view(),
        name='services'),


    url(r'^about/',
        view=AboutUs.as_view(),
        name='about_us'),


    url(r'^thanks/(?P<user_id>[\w\s]+)/',
        view=ThankYou.as_view(),
        name='thank_you'),


    url(r'^create-classroom/(?P<user_id>[\w\s]+)/',
        view=CreateClassroom,
        name='create_classroom'),

    url(r'^create-classroom-two/(?P<user_id>[\w\s]+)/(?P<class_id>[\w\s]+)/',
        view=CreateClassroomTwo,
        name='create_classroom_two'),

    url(r'^thanks-questionnaire/',
        view=ThankYouQuestionnaire.as_view(),
        name='thank_you_questionnaire'),

    url(r'^classroom/(?P<class_id>[\w\s]+)/',
        view=Classrooms.as_view(),
        name='classrooms'),

    url(r'^add-subjects/(?P<user_id>[\w\s]+)/(?P<class_id>[\w\s]+)/(?P<subject_id>[\w\s]+)/',
        view=addSubject,
        name='add_subjects'),


    url(r'^planners/',
        view=LessonPlanner.as_view(),
        name='lesson_planner'),

    url(r'^subject-planners/',
        view=SubjectPlanner.as_view(),
        name='subject_planner'),


    url(r'^classrooms-all/',
        view=ClassroomList.as_view(),
        name='classroom_list'),


    url(r'^sel-topic/$',
        view=SelectTopic,
        name='select_topic'),

    url(r'^up-topic/(?P<lesson_id>[\w\s]+)/',
        view=UpdateTopics,
        name='up_topic'),

    url(r'^account-setip/(?P<user_id>[\w\s]+)/',
        view=AccountSetup,
        name='account_setup'),

    url(r'^create_objective/(?P<user_id>[\w\s]+)/(?P<week_of>[\w\s]+)/',
        view=CreateObjective,
        name='create_objective'),
    

    url(r'^select_standards/(?P<user_id>[\w\s]+)/(?P<class_id>[\w\s]+)/(?P<subject>[\w\s]+)/(?P<lesson_id>[\w\s]+)/(?P<select_all>[\w\s]+)/(?P<topic_id>[\w\s]+)/',
        view=SelectStandards,
        name='select_standards'),


    url(r'^worksheet-builder/(?P<user_id>[\w\s]+)/(?P<class_id>[\w\s]+)/(?P<subject>[\w\s]+)/(?P<lesson_id>[\w\s]+)/(?P<worksheet_id>[\w\s]+)/',
        view=WorksheetBuilder,
        name='worksheet_builder'),



    url(r'^select_standards_two/(?P<user_id>[\w\s]+)/(?P<class_id>[\w\s]+)/(?P<subject>[\w\s]+)/(?P<lesson_id>[\w\s]+)/(?P<select_all>[\w\s]+)/',
        view=SelectKeywordsTwo,
        name='select_standards_two'),

    url(r'^classroom-planbook-edit-standard/(?P<user_id>[\w-]+)/(?P<class_id>[\w-]+)/(?P<subject>[\w-]+)/(?P<lesson_id>[\w-]+)/(?P<standard_id>[\w-]+)/(?P<action>[\w-]+)/$',
        view=EditObjectiveStandards,
        name='edit_objective_standards'),

    url(r'^classroom-planbook-keywords/(?P<user_id>[\w-]+)/(?P<class_id>[\w-]+)/(?P<subject>[\w-]+)/(?P<lesson_id>[\w-]+)/$',
        view=SelectKeywords,
        name='select_keywords'),

    url(r'^classroom-planbook-select-related/(?P<user_id>[\w-]+)/(?P<class_id>[\w-]+)/(?P<subject>[\w-]+)/(?P<lesson_id>[\w-]+)/(?P<type_id>[\w-]+)/(?P<item_id>[\w-]+)/(?P<action>[\w-]+)/$',
        view=SelectRelatedInformation,
        name='select_related'),


    url(r'^activity-builder/(?P<user_id>[\w-]+)/(?P<class_id>[\w-]+)/(?P<subject>[\w-]+)/(?P<lesson_id>[\w-]+)/(?P<page>[\w-]+)/$',
        view=ActivityBuilder,
        name='activity_builder'), 

    url(r'^activity-builder-worksheets/(?P<user_id>[\w-]+)/(?P<class_id>[\w-]+)/(?P<subject>[\w-]+)/(?P<lesson_id>[\w-]+)/(?P<act_id>[\w-]+)/$',
        view=DigitalActivities,
        name='digital_activities'),


    url(r'^upload-lesson-image/(?P<user_id>[\w-]+)/(?P<class_id>[\w-]+)/(?P<subject>[\w-]+)/(?P<lesson_id>[\w-]+)/$',
        view=LessonImageUpload,
        name='lesson_image_upload'),

    url(r'^upload-lesson-pdf/(?P<user_id>[\w-]+)/(?P<class_id>[\w-]+)/(?P<subject>[\w-]+)/(?P<lesson_id>[\w-]+)/$',
        view=LessonPDFUpload,
        name='lesson_pdf_upload'),



    url(r'^practice-test/(?P<user_id>[\w-]+)/(?P<class_id>[\w-]+)/(?P<subject>[\w-]+)/(?P<lesson_id>[\w-]+)/$',
        view=PracticeTest,
        name='practice_test'), 


    url(r'^lesson-activity/(?P<user_id>[\w-]+)/(?P<class_id>[\w-]+)/(?P<subject>[\w-]+)/(?P<lesson_id>[\w-]+)/$',
        view=CreateActivity,
        name='lesson_activity'),

    url(r'^lesson-pdf/(?P<lesson_id>[\w-]+)/$',
        view=generate_lesson_pdf,
        name='lesson_pdf'), 

        
    url(r'^standards_upload/$',
        view=StandardUploadTwo,
        name='standards_upload'),
        

    url(r'^topic_upload/$',
        view=TopicUploadTwo,
        name='topic_upload'),

    url(r'^login/$',
        view=login_user,
        name='login_user'),


    url(r'^question_upload/$',
        view=QuestionUploadTwo,
        name='question_upload'),


    url(r'^textbook_upload/$',
        view=TextbookUploadOne,
        name='textbook_uplad_one'),

    url(r'^textbook_upload_two/(?P<textbook_id>[\w-]+)/$',
        view=TextbookUploadTwo,
        name='textbook_uplad_two'),

    url(r'^print-study-guide/$',
         view=generate_studyguide_pdf,
         name='generate_study_guide'),

    url(r'^digital-study-guide/(?P<user_id>[\w-]+)/(?P<class_id>[\w-]+)/(?P<subject>[\w-]+)/(?P<lesson_id>[\w-]+)/$',
        view=DigitalStudyGuide,
        name='digital_study_guide'),
    
    url(r'^digital-worksheet/(?P<user_id>[\w-]+)/(?P<class_id>[\w-]+)/(?P<subject>[\w-]+)/(?P<lesson_id>[\w-]+)/$',
        view=DigitalWorksheet,
        name='digital_worksheet'),

    path('tinymce/', include('tinymce.urls')),


]
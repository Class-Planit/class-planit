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
from django.views.decorators.csrf import csrf_exempt
from .views import *



urlpatterns = [

     url(r'^$',
        view=Homepage,
        name='homepage'),

    url(r'^hello/$',
        view=HelloView.as_view(),
        name='hello'),

    url(r'^full-form/(?P<retry>.+)/',
        view=FormFull,
        name='registration_full'),

    url(r'^full-form-inv/(?P<retry>[\w\s]+)/(?P<invite_id>[\w\s]+)/',
        view=FormFullInv,
        name='registration_full_inv'),

    url(r'^full-info/(?P<user_id>[\w\s]+)/(?P<waitlist_inv>[\w\s]+)/(?P<invited_by>[\w\s]+)/',
        view=FormInfo,
        name='registration_info'),

    #url(r'^thanks/(?P<user_id>[\w\s]+)/(?P<waitlist_inv>[\w\s]+)/(?P<invited_by>[\w\s]+)/',
    #    view=ThankYou.as_view(),
    #    name='thank_you'),

    url(r'^thanks/(?P<user_id>[\w\s]+)/(?P<waitlist_inv>[\w\s]+)/(?P<invited_by>[\w\s]+)/',
        view=ThankYou,
        name='thank_you'),

    url(r'^questionnaire/',
        view=QuestionnaireFull,
        name='questionnaire_full'),

    url(r'^thanks-questionnaire/',
        view=ThankYouQuestionnaire.as_view(),
        name='thank_you_questionnaire'),

    url(r'^update-week-of/(?P<week_of>[\w-]+)/(?P<user_id>[\w-]+)/(?P<subject_id>[\w-]+)/(?P<classroom_id>[\w-]+)/(?P<action>[\w-]+)/',
       view=UpdateWeekOf,
       name='update_week_of'),

    url(r'^dashboard/(?P<week_of>[\w\s]+)/(?P<subject_id>[\w\s]+)/(?P<classroom_id>[\w\s]+)/(?P<standard_id>[\w\s]+)/',
        view=Dashboard,
        name='Dashboard'),

    url(r'^student-dashboard/(?P<lesson_id>[\w\s]+)/(?P<worksheet_id>[\w\s]+)/(?P<question_id>[\w\s]+)/',
        view=StudentWorksheetStart,
        name='student_dashboard'),

    url(r'^student-main/(?P<user_id>[\w\s]+)/',
        view=StudentMainDashboard,
        name='student_main'),

    url(r'^student-alerts/(?P<user_id>[\w\s]+)/',
        view=StudentAlertDashboard,
        name='student_alerts'),

    url(r'^student-registration/(?P<ref_id>[\w\s]+)/(?P<lesson_id>[\w\s]+)/(?P<worksheet_id>[\w\s]+)/',
        view=StudentRegistration,
        name='student_registration'),

    url(r'^student-login/(?P<lesson_id>[\w\s]+)/(?P<worksheet_id>[\w\s]+)/$',
        view=StudentLogin,
        name='student_login'),


    url(r'^student-submit/(?P<user_id>[\w\s]+)/(?P<lesson_id>[\w\s]+)/(?P<worksheet_id>[\w\s]+)/(?P<submit>[\w\s]+)/',
        view=StudentWorksheetSubmit,
        name='student_submit'),

    url(r'^mc-student-select/(?P<user_id>[\w\s]+)/(?P<lesson_id>[\w\s]+)/(?P<worksheet_id>[\w\s]+)/',
        view=StudentMCSelect,
        name='student_mc_select'),


    url(r'^activity-preview/(?P<act_temp>[\w\s]+)/(?P<demo_type>[\w\s]+)/(?P<topic_type>[\w\s]+)/(?P<subject>[\w\s]+)/(?P<grade>[\w\s]+)/',
        view=AdminActivityPreview,
        name='admin_activity_preview'),

    url(r'^fib-student-answer/(?P<user_id>[\w\s]+)/(?P<lesson_id>[\w\s]+)/(?P<worksheet_id>[\w\s]+)/(?P<question_id>[\w\s]+)/(?P<index_id>[\w\s]+)/',
        view=StudentFIBAnswer,
        name='student_fib_answer'),

    url(r'^sa-student-answer/(?P<user_id>[\w\s]+)/(?P<lesson_id>[\w\s]+)/(?P<worksheet_id>[\w\s]+)/(?P<question_id>[\w\s]+)/(?P<index_id>[\w\s]+)/',
        view=StudentSAAnswer,
        name='student_sa_answer'),

    url(r'^login/$',
        view=login_user,
        name='login_user'),

    url(r'^login-chrome/$',
        view=login_user_chrome,
        name='login_user_chrome'),

    url(r'^build-lesson-doc/(?P<user_id>[\w\s]+)/(?P<lesson_id>[\w\s]+)/$',
        view=build_lesson_doc,
        name='build_doc'),

    url(r'^build-lesson-pdf/(?P<user_id>[\w\s]+)/(?P<lesson_id>[\w\s]+)/$',
        view=build_lesson_pdf,
        name='build_pdf'),

    url(r'^log-out/$',
        view=logout_user,
        name='logout_user'),

    url(r'^how-it-works/',
        view=HowItWorks.as_view(),
        name='how_it_works'),
    
    url(r'^services/',
        view=Services.as_view(),
        name='services'),


    url(r'^about/',
        view=AboutUs.as_view(),
        name='about_us'),

    url(r'^classrooms-all/',
        view=ClassroomLists,
        name='classroom_list'),


    url(r'^add-single-topic/(?P<top_id>[\w-]+)/(?P<act_type>[\w-]+)/',
        view=AddSingleTopic,
        name='single_topic_upload'),

    url(r'^classroom-dashboard/(?P<user_id>[\w-]+)/(?P<class_id>[\w-]+)/(?P<standard_id>[\w\s]+)/',
        view=ClassroomDashboard,
        name='classroom_single'),

    url(r'^classroom-settings/(?P<user_id>[\w-]+)/(?P<classroom_id>[\w-]+)/(?P<view_ref>[\w-]+)/(?P<confirmation>[\w-]+)/',
        view=ClassroomSettingsView,
        name='classroom_settings'),

    url(r'^add-student-to-classroom/(?P<user_id>[\w-]+)/(?P<class_id>[\w-]+)/(?P<invite_id>[\w-]+)/',
        view=AddStudentToClassroom,
        name='add_student_to_classroom'),
        
    url(r'^add-teacher-to-classroom/(?P<user_id>[\w-]+)/(?P<class_id>[\w-]+)/(?P<invite_id>[\w-]+)/',
        view=AddTeacherToClassroom,
        name='add_teacher_to_classroom'),

    url(r'^edit-classroom-subjects/(?P<user_id>[\w-]+)/(?P<class_id>[\w-]+)/(?P<subject_id>[\w-]+)/(?P<action>[\w-]+)/',
        view=EditClassroomSubjects,
        name='edit_classroom_subjects'),

    url(r'^edit-classroom-grade-levels/(?P<user_id>[\w-]+)/(?P<class_id>[\w-]+)/(?P<grade_level_id>[\w-]+)/(?P<action>[\w-]+)/',
        view=EditClassroomGradeLevels,
        name='edit_classroom_grade_levels'),

    url(r'^create_objective/(?P<user_id>[\w\s]+)/(?P<week_of>[\w\s]+)/(?P<classroom_id>[\w\s]+)/(?P<subject_id>[\w\s]+)/',
        view=CreateObjective,
        name='create_objective'),

    url(r'^start-planning-demo/(?P<email>[\w\d@\.-]+)/',
        view=StartPlanningDemo,
        name='start_planning_demo'),

    url(r'^user-profile/(?P<user_id>[\w\s]+)/(?P<message>[\w\s]+)/',
        view=UserProfileView,
        name='user_profile_view'),


    url(r'^update-user-profile/(?P<user_id>[\w\s]+)/',
        view=UpdateUserProfile,
        name='update_user_profile'),


    url(r"^admin_change_password/(?P<user_id>[\w\d@\.-]+)/$",
        view=admin_change_password,
        name="admin_change_password"),

    url(r'^create_objective-with-standard/(?P<user_id>[\w\s]+)/(?P<week_of>[\w\s]+)/(?P<subject_id>[\w\s]+)/(?P<classroom_id>[\w\s]+)/(?P<standard_id>[\w\s]+)/',
        view=CreateObjectiveWithStandard,
        name='create_objective_with_standard'),

    url(r'^student-performance/(?P<user_id>[\w\s]+)/(?P<class_id>[\w\s]+)/(?P<week_of>[\w\s]+)/(?P<standard_id>[\w\s]+)/',
        view=StudentPerformance,
        name='student_performance'),

    url(r'^activity-builder/(?P<user_id>[\w-]+)/(?P<class_id>[\w-]+)/(?P<subject>[\w-]+)/(?P<lesson_id>[\w-]+)/(?P<page>[\w-]+)/$',
        view=ActivityBuilder,
        name='activity_builder'), 

    url(r'^classroom-planbook-edit-standard/(?P<user_id>[\w-]+)/(?P<class_id>[\w-]+)/(?P<subject>[\w-]+)/(?P<lesson_id>[\w-]+)/(?P<standard_id>[\w-]+)/(?P<action>[\w-]+)/$',
        view=EditObjectiveStandards,
        name='edit_objective_standards'),

    url(r'^sel-topic/$',
        view=SelectTopic,
        name='select_topic'),


    url(r'^add-youtube-video/$',
        view=SelectYoutubeVideo,
        name='add_youtube_video'),


    url(r'^add-selected_question/$',
        view=AddSelectedQuestion,
        name='add_selected_question'),

        
    url(r'^standard-tracking/$',
        view=StandardsTracking,
        name='standard_tracker'),


    url(r'^123admin8401/$',
        view=SupAdDash,
        name='sup_admin_dashboard'),

    url(r'^demo-123admin8401/(?P<act_id>[\w-]+)/(?P<act_type>[\w-]+)/$',
        view=AddDemoKSTemplate,
        name='admin_demo_ks'),
    
    url(r'^act-123admin8401/(?P<act_id>[\w-]+)/(?P<act_type>[\w-]+)/$',
        view=AddActivityTemplate,
        name='admin_activity'),

    url(r'^delete-123admin8401/(?P<act_id>[\w-]+)/(?P<act_type>[\w-]+)/$',
        view=DeleteAdminPlanning,
        name='delete_admin_info'),

    url(r'^gs-123admin8401/(?P<act_id>[\w-]+)/(?P<act_type>[\w-]+)/$',
        view=SelectGradeSubjectAdmin,
        name='add_gs'),


    url(r'^narrow-standard-tracking/(?P<subject_id>[\w-]+)/(?P<classroom_id>[\w-]+)/',
        view=NarrowStandardsTracking,
        name='narrow_standard_tracker'),

    url(r'^single-standard-tracking/(?P<subject_id>[\w-]+)/(?P<classroom_id>[\w-]+)/(?P<standard_id>[\w-]+)/',
        view=SingleStandardsTracking,
        name='single_standard_tracker'),

    url(r'^sel-activity/$',
        view=SelectActivity,
        name='select_activity'),

    url(r'^save-text/(?P<lesson_id>[\w-]+)/$',
        view=SaveLessonText,
        name='save_lesson_text'),

    url(r'^save-text-api/(?P<user_id>[\w-]+)/(?P<class_id>[\w-]+)/(?P<lesson_id>[\w-]+)/(?P<grade_id>[\w-]+)/(?P<subject_id>[\w-]+)/$',
        view=SaveLessonTextAPI,
        name='save_lesson_text_api'),


    url(r'^get-blooms/(?P<lesson_id>[\w-]+)/$',
        view=GetBloomsAnalytics,
        name='get_blooms'),

    url(r'^get-activity-summary/(?P<lesson_id>[\w-]+)/$',
        view=GetActivitySummary,
        name='get_activity_summary'),

    url(r'^get-standards_analytics/(?P<lesson_id>[\w-]+)/$',
        view=GetStandardsAnalytics,
        name='get_standards_analytics'),

    url(r'^get-standard-recs/(?P<lesson_id>[\w-]+)/(?P<class_id>[\w-]+)/$',
        view=UpdateStandards,
        name='get_standard'),

    url(r'^get-retention/(?P<lesson_id>[\w-]+)/$',
        view=GetRetentionAnalytics,
        name='get_retention'),

    url(r'^get-mi/(?P<lesson_id>[\w-]+)/$',
        view=GetMIAnalytics,
        name='get_mi'),

    url(r'^sel-standard/(?P<lesson_id>[\w-]+)/$',
        view=SelectStandards,
        name='select_standards'),

    url(r'^updated-term-options/(?P<lesson_id>[\w-]+)/(?P<class_id>[\w-]+)/$',
        view=UpdateKeyTerms,
        name='update_terms_options'),

    url(r'^updated-big-questions/(?P<lesson_id>[\w-]+)/(?P<class_id>[\w-]+)/$',
        view=UpdateBigQuestions,
        name='update_big_questions'),

    url(r'^remove-term-options/(?P<lesson_id>[\w-]+)/(?P<class_id>[\w-]+)/$',
        view=RemoveKeyTerms,
        name='remove_terms_options'),

    url(r'^updated-activity-options/(?P<lesson_id>[\w-]+)/(?P<class_id>[\w-]+)/$',
        view=UpdateLessonActivities,
        name='update_activity_options'),



    url(r'^activity-builder-worksheets/(?P<user_id>[\w-]+)/(?P<class_id>[\w-]+)/(?P<subject>[\w-]+)/(?P<lesson_id>[\w-]+)/(?P<page>[\w-]+)/(?P<worksheet_id>[\w-]+)/(?P<act_id>[\w-]+)/(?P<question_id>[\w-]+)/$',
        view=DigitalActivities,
        name='digital_activities'),


    url(r'^create-classroom-assignment/(?P<user_id>[\w-]+)/(?P<week_of>[\w-]+)/(?P<class_id>[\w-]+)/(?P<worksheet_id>[\w-]+)/(?P<lesson_id>[\w-]+)/(?P<assign_id>[\w-]+)/(?P<step>[\w-]+)/$',
        view=CreateClassroomAssignment,
        name='create_classroom_assignment'),

    url(r'^add-theme-assignment/(?P<user_id>[\w-]+)/(?P<week_of>[\w-]+)/(?P<class_id>[\w-]+)/(?P<worksheet_id>[\w-]+)/(?P<lesson_id>[\w-]+)/(?P<assign_id>[\w-]+)/(?P<step>[\w-]+)/(?P<theme_id>[\w-]+)/$',
        view=AddThemeAssignment,
        name='add_theme_assignment'),

    url(r'^add-classroom-assignment/(?P<user_id>[\w-]+)/(?P<week_of>[\w-]+)/(?P<class_id>[\w-]+)/(?P<worksheet_id>[\w-]+)/(?P<lesson_id>[\w-]+)/(?P<assign_id>[\w-]+)/(?P<step>[\w-]+)/$',
        view=AddClassroomAssignment,
        name='add_classroom_assignment'),

    url(r'^new-worksheet-builder/(?P<user_id>[\w-]+)/(?P<worksheet_id>[\w-]+)/(?P<page>[\w-]+)/(?P<question_id>[\w-]+)/$',
        view=BlankDigitalActivities,
        name='new_digital_activities'),


    url(r'^edit-question/(?P<user_id>[\w-]+)/(?P<class_id>[\w-]+)/(?P<subject>[\w-]+)/(?P<lesson_id>[\w-]+)/(?P<page>[\w-]+)/(?P<worksheet_id>[\w-]+)/(?P<act_id>[\w-]+)/(?P<question_id>[\w-]+)/$',
        view=EditQuestions,
        name='edit_question'),

    url(r'^new-question/(?P<user_id>[\w-]+)/(?P<class_id>[\w-]+)/(?P<subject>[\w-]+)/(?P<lesson_id>[\w-]+)/(?P<page>[\w-]+)/(?P<worksheet_id>[\w-]+)/(?P<act_id>[\w-]+)/(?P<question_id>[\w-]+)/$',
        view=NewQuestions,
        name='add_new_question'),

    url(r'^standards_upload/$',
        view=StandardUploadTwo,
        name='standards_upload'),


    url(r'^search-image/(?P<worksheet_id>[\w-]+)/(?P<question_id>[\w-]+)/$',
        view=GoogleImageSearch,
        name='google_image_search'),


    url(r'^search-wiki/(?P<lesson_id>[\w-]+)/$',
        view=SearchKeyTerm,
        name='search_key_term'),


    url(r'^add-question-image/(?P<class_id>[\w-]+)/(?P<lesson_id>[\w-]+)/(?P<subject>[\w-]+)/(?P<worksheet_id>[\w-]+)/(?P<question_id>[\w-]+)/$', 
        view=AddQuestionImage,
        name='add_question_image'),


    url(r'^topic_upload/$',
        view=TopicUploadTwo,
        name='topic_upload'),

    url(r'^textbook_upload/$',
        view=TextbookUploadOne,
        name='textbook_uplad_one'),
        
    url(r'^textbook_upload_two/(?P<textbook_id>[\w-]+)/$',
        view=TextbookUploadTwo,
        name='textbook_uplad_two'),

]
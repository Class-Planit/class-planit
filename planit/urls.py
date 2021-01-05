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
        view=Homepage.as_view(),
        name='Homepage'),

    url(r'^dashboard/(?P<week_of>[\w\s]+)/',
        view=Dashboard.as_view(),
        name='Dashboard'),

    url(r'^classrooms/',
        view=Classrooms.as_view(),
        name='classrooms'),

    url(r'^planners/',
        view=LessonPlanner.as_view(),
        name='lesson_planner'),

    url(r'^subject-planners/',
        view=SubjectPlanner.as_view(),
        name='subject_planner'),


    url(r'^create_objective/(?P<user_id>[\w\s]+)/(?P<week_of>[\w\s]+)/',
        view=CreateObjective,
        name='create_objective'),
    

    url(r'^select_standards/(?P<user_id>[\w\s]+)/(?P<class_id>[\w\s]+)/(?P<subject>[\w\s]+)/(?P<lesson_id>[\w\s]+)/',
        view=SelectStandards,
        name='select_standards'),

    url(r'^classroom-planbook-edit-standard/(?P<user_id>[\w-]+)/(?P<class_id>[\w-]+)/(?P<subject>[\w-]+)/(?P<lesson_id>[\w-]+)/(?P<standard_id>[\w-]+)/(?P<action>[\w-]+)/$',
        view=EditObjectiveStandards,
        name='edit_objective_standards'),

    url(r'^classroom-planbook-keywords/(?P<user_id>[\w-]+)/(?P<class_id>[\w-]+)/(?P<subject>[\w-]+)/(?P<lesson_id>[\w-]+)/$',
        view=SelectKeywords,
        name='select_keywords'),

    url(r'^classroom-planbook-select-related/(?P<user_id>[\w-]+)/(?P<class_id>[\w-]+)/(?P<subject>[\w-]+)/(?P<lesson_id>[\w-]+)/(?P<type_id>[\w-]+)/(?P<item_id>[\w-]+)/(?P<action>[\w-]+)/$',
        view=SelectRelatedInformation,
        name='select_related'),

    url(r'^classroom-planbook-keywords-two/(?P<user_id>[\w-]+)/(?P<class_id>[\w-]+)/(?P<subject>[\w-]+)/(?P<lesson_id>[\w-]+)/$',
        view=SelectKeywordsTwo,
        name='select_keywords_two'),    


    url(r'^activity-builder/(?P<user_id>[\w-]+)/(?P<class_id>[\w-]+)/(?P<subject>[\w-]+)/(?P<lesson_id>[\w-]+)/$',
        view=ActivityBuilder,
        name='activity_builder'), 

        
    url(r'^standards_upload/$',
        view=StandardUploadTwo,
        name='standards_upload'),
        

]
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

    url(r'^get-started/$',
        view=GetStarted.as_view(),
        name='get_started'),
    
    url(r'^print/$',
        view=generate_pdf,
        name='generate_pdf'),

    url(r'^sign-up/$',
        view=Signup,
        name='sign_form'),

    url(r'^profile/(?P<user_id>[\w-]+)/$',
        view=MyProfile,
        name='my_profile'),
    
    url(r'^classroom-settings/(?P<user_id>[\w-]+)/(?P<class_id>[\w-]+)/$',
        view=ClassroomSettings,
        name='classroom_settings'),

    url(r'^classroom-assignments/(?P<user_id>[\w-]+)/(?P<class_id>[\w-]+)/(?P<subject>[\w-]+)/$',
        view=ClassroomAssignments,
        name='classroom_assignments'),

    url(r'^classroom-planbook/(?P<user_id>[\w-]+)/(?P<class_id>[\w-]+)/(?P<subject>[\w-]+)/$',
        view=ClassroomPlanbook,
        name='classroom_planbook'),

    url(r'^classroom-students/(?P<user_id>[\w-]+)/(?P<class_id>[\w-]+)/(?P<student_id>[\w-]+)/$',
        view=ClassroomStudents,
        name='classroom_students'),
    
    url(r'^classroom-analytics/(?P<user_id>[\w-]+)/(?P<class_id>[\w-]+)/(?P<subject>[\w-]+)/$',
        view=ClassroomAnalytics,
        name='classroom_analytics'),

]


ClassroomAssignments, ClassroomPlanbook, ClassroomStudents, ClassroomAnalytics
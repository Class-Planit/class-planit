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

]
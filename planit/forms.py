from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.forms.models import inlineformset_factory, BaseModelFormSet
from django.forms import ModelChoiceField
from django.utils.translation import ugettext_lazy as _
from django.db import transaction
from .models import *
import datetime
from datetime import datetime

from phonenumber_field.formfields import PhoneNumberField


class lessonObjectiveForm(forms.ModelForm):

    class Meta:
        model = lessonObjective
        fields = '__all__'
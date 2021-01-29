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
from tinymce.widgets import TinyMCE

class  lessonTextForm(forms.ModelForm):

    class Meta:
        model = lessonText
        fields = '__all__'


class lessonObjectiveForm(forms.ModelForm):

    class Meta:
        model = lessonObjective
        fields = '__all__'

class classroomForm(forms.ModelForm):

    class Meta:
        model = classroom
        fields = '__all__'


class textBookTitleForm(forms.ModelForm):

    class Meta:
        model = textBookTitle
        fields = '__all__'

class TeacherForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')
    phone_number = forms.CharField(max_length=30, required=False, help_text='Optional.')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone_number', 'password1', 'password2')

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_teacher = True
        user.save()
        teacher = school_user.objects.create(user=user)
        return user
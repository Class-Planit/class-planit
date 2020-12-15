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


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')
    phone_number = PhoneNumberField(required=False, help_text='Enter your mobile phone number beginging with country code')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'phone_number', 'email', 'password1', 'password2')


class ClassroomForm(forms.ModelForm):

    class Meta:
        model = classroom
        fields = '__all__'


class academicYearForm(forms.ModelForm):

    class Meta:
        model = academicYear
        fields = '__all__'

class lessonObjectiveForm(forms.ModelForm):

    class Meta:
        model = lessonObjective
        fields = '__all__'
    
class vocabularyWordForm(forms.ModelForm):

    class Meta:
        model = vocabularyWord
        fields = '__all__'    

class lessonSectionForm(forms.ModelForm):

    class Meta:
        model = lessonSection
        fields = '__all__'  

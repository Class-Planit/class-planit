from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.forms.models import inlineformset_factory, BaseModelFormSet
from django.forms import ModelChoiceField, RadioSelect
from django.utils.translation import ugettext_lazy as _
from django.db import transaction
from .models import *
import datetime
from datetime import datetime
from multiselectfield import MultiSelectField
from phonenumber_field.formfields import PhoneNumberField
from tinymce.widgets import TinyMCE



class SelectQuestionsForm(forms.Form):
    
    selected_questions = forms.MultipleChoiceField(required=False, widget=forms.CheckboxSelectMultiple)



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


class teacherQuestionnaireForm(forms.ModelForm):

    class Meta:
        model = teacherQuestionnaire
        fields = '__all__'

class lessonPDFTextForm(forms.ModelForm):

    class Meta:
        model = lessonPDFText
        fields = '__all__'

class LearningDemonstrationForm(forms.ModelForm):

    class Meta:
        model = LearningDemonstration
        fields = '__all__'


class topicInformationForm(forms.ModelForm):

    class Meta:
        model = topicInformation
        fields = '__all__'


class lessonImageUploadForm(forms.ModelForm):

    class Meta:
        model = lessonImageUpload
        fields = '__all__'



class selectedActivityForm(forms.ModelForm):

    class Meta:
        model = selectedActivity
        fields = '__all__'


class textBookTitleForm(forms.ModelForm):

    class Meta:
        model = textBookTitle
        fields = '__all__'

class TeacherForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'example: EdnaK'}))
    first_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={'placeholder': 'example: Edna'}), help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={'placeholder': 'example: Krabappel'}), help_text='Optional.')
    email = forms.EmailField(max_length=254, widget=forms.TextInput(attrs={'placeholder': 'example@none.com'}), help_text='Required. Inform a valid email address.')
    phone_number = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'placeholder': '+12345678900'}),required=False, help_text='Optional.')

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
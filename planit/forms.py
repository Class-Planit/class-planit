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

from phonenumber_field.formfields import PhoneNumberField
from tinymce.widgets import TinyMCE


class teacherSubjectForm(forms.Form):
    subject_title = forms.CharField()


class classroomAssignmentForm(forms.Form):
    worksheet_title = forms.CharField(max_length=150, required=False,)
    worksheet_description = forms.CharField(max_length=150, required=False,)
    worksheet_date = forms.CharField(max_length=150, required=False,)

class UserSearchForm(forms.Form):
    search_item = forms.CharField()
    search_ref = forms.CharField()

class classroomTitleForm(forms.Form):
    classroom_title = forms.CharField()

class standardsTrackingInfoForm(forms.ModelForm):
    class Meta:
        model = standardsTrackingInfo
        fields = '__all__'

class  lessonTextForm(forms.ModelForm):

    class Meta:
        model = lessonText
        fields = '__all__'

class  LearningDemonstrationTemplateForm(forms.ModelForm):

    class Meta:
        model = LearningDemonstrationTemplate
        fields = '__all__'

class  topicInformationForm(forms.ModelForm):

    class Meta:
        model = topicInformation
        fields = '__all__'


class  lessonTemplatesForm(forms.ModelForm):

    class Meta:
        model = lessonTemplates
        fields = '__all__'

class  multiSelectGSForm(forms.ModelForm):
    grade_level = forms.ModelMultipleChoiceField(queryset = gradeLevel.objects.all(), required=False, widget=forms.CheckboxSelectMultiple)
    subject = forms.ModelMultipleChoiceField(queryset = standardSubjects.objects.all(), required=False, widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = multiSelectGS
        fields = '__all__'



class  studentProfilesForm(forms.ModelForm):

    class Meta:
        model = studentProfiles
        fields = '__all__'

class  studentInvitationForm(forms.ModelForm):

    class Meta:
        model = studentInvitation
        fields = '__all__'


class  teacherInvitationsForm(forms.ModelForm):

    class Meta:
        model = teacherInvitations
        fields = '__all__'


class  topicQuestionitemForm(forms.ModelForm):

    class Meta:
        model = topicQuestionitem
        fields = ('Question', 'Correct', 'Incorrect_One', 'Incorrect_Two')


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


class worksheetFullForm(forms.ModelForm):

    class Meta:
        model = worksheetFull
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

class waitlistUserInfoForm(forms.ModelForm):

    class Meta:
        model = waitlistUserInfo
        fields = '__all__'

class TeacherForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username...'}))
    first_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={'placeholder': 'First Name...'}), help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={'placeholder': 'Last Name...'}), help_text='Optional.')
    email = forms.EmailField(max_length=254, widget=forms.TextInput(attrs={'placeholder': 'Email...'}), help_text='Required. Inform a valid email address.')
    phone_number = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'placeholder': 'Phone...'}),required=False, help_text='Optional.')


    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone_number', 'password1', 'password2', 'standards_set', 'city', 'state')

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_teacher = True
        user.save()
        teacher = school_user.objects.create(user=user)
        return user

class StudentForm(UserCreationForm):
    username = forms.CharField()
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()
    phone_number = forms.CharField()

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone_number', 'password1', 'password2')

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_student = True
        user.save()
        teacher = school_user.objects.create(user=user)
        return user
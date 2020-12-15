from django.db import models
from django.utils.timezone import now
from dateutil.relativedelta import relativedelta
from datetime import date
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from .generator import token_generator
from phonenumber_field.modelfields import PhoneNumberField
import datetime
datetime.date.today()

# Create your models here.

class User(AbstractUser):
    is_parent = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_destrict = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    is_pending = models.BooleanField(default=False)




class school_user(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='user_role')
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    username = models.CharField(max_length=30)
    email = models.EmailField(blank=True,
                              null=True)
    phone_number = PhoneNumberField(blank=True,
                                    null=True)
    use_whatsapp = models.BooleanField(default=False)
    user_image = models.ImageField(upload_to='images/',
                                   blank=True,
                                   null=True)

    def __str__(self):
        return "%s" % (self.username)


class standardSet(models.Model):
    Location = models.TextField(max_length=500)

    def __str__(self):
        return "%s" % (self.Location)


    

    def __str__(self):
        return "%s" % (self.Location)

class gradeLevel(models.Model):
    grade = models.CharField(max_length=30)
    grade_labels = models.CharField(max_length=50,
                                   blank=True,
                                   null=True)
    standards_set = models.ForeignKey(standardSet,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    grade_image = models.ImageField(upload_to='images/grades/',
                                    blank=True,
                                    null=True)

    def __str__(self):
        return "%s" % (self.grade_labels)




class academicYear(models.Model):
    start_date = models.DateField(blank=True,
                                   null=True)
    end_date = models.DateField(blank=True,
                                   null=True)
    is_active = models.BooleanField(default=True)
    planning_teacher = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True)

    def __str__(self):
        return "%s - %s" % (self.start_date, self.end_date)


class studentProfiles(models.Model):
    student_ref = models.CharField(_('Student Reference'),
                                   max_length=255,
                                   blank=True,
                                   null=True)
    first_name = models.CharField(max_length=50,
                                  blank=True,
                                  null=True)
    last_name = models.CharField(max_length=50,
                                 blank=True,
                                 null=True)
    middle_names = models.CharField(max_length=200,
                                    blank=True,
                                    null=True)
    current_grade_level = models.ForeignKey(gradeLevel,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    date_of_birth = models.DateField(blank=True,
                                     null=True)
    gender = models.CharField(max_length=30,
                              blank=True,
                              null=True,)
    is_enrolled = models.BooleanField(default=False)
    is_suspended = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    is_pending = models.BooleanField(default=False)
    student_username = models.ForeignKey(User,
                                         on_delete=models.SET_NULL,
                                         blank=True,
                                         null=True,
                                         related_name='student_username')

    @property
    def age(self):
        today = date.today()
        result = difference_in_years = relativedelta(
            today, self.date_of_birth).years
        return (result)

    def save(self, *args, **kwargs):
        # This to check if it creates a new or updates an old instance
        if self.pk is None:
            self.student_ref = token_generator.make_token(8)
        super(student_profiles, self).save(*args, **kwargs)

    def __str__(self):
        return '%s %s' % (self.first_name, self.last_name)


class classroom(models.Model):
    classroom_title = models.CharField(max_length=100)
    grade_level = models.ManyToManyField(gradeLevel,
                                     blank=True,
                                     related_name='grade_level')
    main_teacher = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True,
                               related_name='main_teacher')
    support_teachers = models.ManyToManyField(User,
                                     blank=True,
                                     related_name='support_teacher')
    academic_year = models.ForeignKey(academicYear,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    student = models.ManyToManyField(studentProfiles,
                                     blank=True,
                                     related_name='student')
    is_active = models.BooleanField(default=True)
    standards_set = models.ForeignKey(standardSet,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)


    def __str__(self):
        return "%s" % (self.classroom_title)

class standardSubjects(models.Model):
    subject_title = models.CharField(max_length=100)
    standards_set = models.ForeignKey(standardSet,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    created_by = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True)
    is_admin = models.BooleanField(default=False)
    grade_level = models.ManyToManyField(gradeLevel,
                                     blank=True,
                                     related_name='subject_grades')

    def __str__(self):
        return "%s" % (self.subject_title)
                        
class classroomSubjects(models.Model):
    subject_classroom = models.ForeignKey(classroom,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    subjects = models.ManyToManyField(standardSubjects,
                                     blank=True)

    def __str__(self):
        return "%s" % (self.subject_classroom)


class singleStandard(models.Model):
    standards_set = models.ForeignKey(standardSet,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    subject = models.ForeignKey(standardSubjects,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    grade_level = models.ForeignKey(gradeLevel,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    standard_identifier = models.CharField(max_length=100,
                               blank=True,
                               null=True)
    skill_topic = models.TextField(max_length=200)
    standard_objective = models.CharField(max_length=1000,
                               blank=True,
                               null=True)
    competency = models.TextField(max_length=1000)
    
    def __str__(self):
        return "%s : %s - %s" % (self.skill_topic, self.standard_objective, self.competency)




class lessonObjective(models.Model):
    lesson_classroom = models.ForeignKey(classroom,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    subject = models.ForeignKey(standardSubjects,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    week_of = models.CharField(max_length=10,
                               blank=True,
                               null=True)
    is_skill = models.BooleanField(default=False)
    objective_title = models.CharField(max_length=200,
                               blank=True,
                               null=True)
    teacher_objective = models.CharField(max_length=1500,
                               blank=True,
                               null=True)
    objectives_standards = models.ManyToManyField(singleStandard,
                                     blank=True,
                                     related_name='objectives_standards',
                               null=True)

    def __str__(self):
        return "%s" % (self.objective_title)

class lessonStandardRecommendation(models.Model):
    lesson_classroom = models.ForeignKey(classroom,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    objectives = models.ForeignKey(lessonObjective,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    objectives_standard = models.ForeignKey(singleStandard,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    is_selected = models.BooleanField(default=False)

    def __str__(self):
        return "%s" % (self.id)

class googleSearchResult(models.Model):
    is_selected = models.BooleanField(default=False)
    lesson_plan = models.ForeignKey(lessonObjective,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    title = models.CharField(max_length=100)
    link = models.CharField(max_length=500)
    snippet = models.CharField(max_length=1000)

    def __str__(self):
        return "%s" % (self.id)

class keywordResults(models.Model):
    is_selected = models.BooleanField(default=False)
    lesson_plan = models.ForeignKey(lessonObjective,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    word = models.CharField(max_length=100)


    def __str__(self):
        return "%s" % (self.id)

class googleRelatedQuestions(models.Model):
    is_selected = models.BooleanField(default=False)
    lesson_plan = models.ForeignKey(lessonObjective,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    question = models.CharField(max_length=500)
    link = models.CharField(max_length=500)
    snippet = models.CharField(max_length=1000)

class weeklyObjectives(models.Model):
    week_of = models.CharField(max_length=10)
    subject_classroom = models.ForeignKey(classroom,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    objectives = models.ManyToManyField(lessonObjective,
                                     blank=True)

    def __str__(self):
        return "%s" % (self.subject_classroom)

    
class vocabularyWord(models.Model):
    word = models.CharField(max_length=50)
    p_o_s = models.CharField(max_length=50,
                                       blank=True,
                                       null=True)
    definition = models.CharField(max_length=500,
                                       blank=True,
                                       null=True)
    sentence = models.CharField(max_length=300,
                                       blank=True,
                                       null=True)
    audio_file = models.FileField(blank=True,
                                  null=True)
    question_image = models.ImageField(upload_to='images/words/',
                                       blank=True,
                                       null=True)                              
    def __str__(self):
        return "%s" % (self.word)


class vocabularyList(models.Model):
    vocab_words = models.ManyToManyField(vocabularyWord,
                                     blank=True)
    week_of = models.CharField(max_length=10)
    subject = models.ForeignKey(standardSubjects,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    lesson_plan = models.ForeignKey(lessonObjective,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    created_by = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True)
                            
    def __str__(self):
        return "%s - %s" % (self.created_by, self.week_of)

class mainQuestion(models.Model):
    question = models.CharField(max_length=500)
    answer = models.CharField(max_length=1000,
                                       blank=True,
                                       null=True)                             
    def __str__(self):
        return "%s" % (self.question)

class questionList(models.Model):
    main_questions = models.ManyToManyField(mainQuestion,
                                     blank=True)
    week_of = models.CharField(max_length=10)
    subject = models.ForeignKey(standardSubjects,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    lesson_plan = models.ForeignKey(lessonObjective,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    created_by = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True)
                            
    def __str__(self):
        return "%s - %s" % (self.created_by, self.week_of)

class lessonSection(models.Model):
    order_num = models.CharField(max_length=5,
                                       blank=True,
                                       null=True)
    title = models.CharField(max_length=150,
                                       blank=True,
                                       null=True)
    content = models.CharField(max_length=1000,
                                       blank=True,
                                       null=True)
    
    def __str__(self):
        return "%s" % (self.title)


class lessonSectionTemplate(models.Model):
    title = models.CharField(max_length=300,
                                       blank=True,
                                       null=True)
    lesson_section = models.ManyToManyField(lessonSection,
                                     blank=True)
    created_by = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True)
    is_admin = models.BooleanField(default=False)
    
    def __str__(self):
        return "%s" % (self.title)


class teacherLessonTemplates(models.Model):
    planning_teacher = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True)
    lesson_section = models.ManyToManyField(lessonSectionTemplate,
                                     blank=True)
    
    def __str__(self):
        return "%s" % (self.planning_teacher)

class bloomsLevel(models.Model):
    title = models.CharField(max_length=20,
                                       blank=True,
                                       null=True)
    group = models.CharField(max_length=50,
                                       blank=True,
                                       null=True)
    color = models.CharField(max_length=50,
                                       blank=True,
                                       null=True)


    def __str__(self):
        return "%s" % (self.title)

class learningStyle(models.Model):
    title = models.CharField(max_length=20,
                                       blank=True,
                                       null=True)
    group = models.CharField(max_length=50,
                                       blank=True,
                                       null=True)
    color = models.CharField(max_length=50,
                                       blank=True,
                                       null=True)


    def __str__(self):
        return "%s" % (self.title)

class lessonFull(models.Model):
    lesson_overview = models.ForeignKey(lessonObjective,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    title = models.CharField(max_length=300,
                                       blank=True,
                                       null=True)
    lesson_section = models.ManyToManyField(lessonSection,
                                     blank=True)
    subject = models.ForeignKey(standardSubjects,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    vocabulary_list = models.ForeignKey(vocabularyList,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    main_questions = models.ForeignKey(questionList,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    blooms = models.ManyToManyField(bloomsLevel,
                                     blank=True)
    styles = models.ManyToManyField(learningStyle,
                                     blank=True)

    
    def __str__(self):
        return "%s" % (self.id)
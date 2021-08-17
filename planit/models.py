from django.db import models
from django.utils.timezone import now
from dateutil.relativedelta import relativedelta
from datetime import date
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from .generator import token_generator
from phonenumber_field.modelfields import PhoneNumberField
from tinymce.models import HTMLField
from tinymce import models as tinymce_models
import datetime
datetime.date.today()

# Create your models here.

class standardSet(models.Model):
    Location = models.TextField(max_length=500)

    def __str__(self):
        return "%s" % (self.Location)

class User(AbstractUser):
    is_parent = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_destrict = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    is_pending = models.BooleanField(default=False)
    is_demo = models.BooleanField(default=False)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    standards_set = models.ForeignKey(standardSet,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)



class school_user(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='user_role')
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    username = models.CharField(max_length=30)
    email = models.EmailField(blank=True,
                              null=True)
    phone_number = models.CharField(max_length=30,
                                    blank=True,
                                    null=True)
    use_whatsapp = models.BooleanField(default=False)
    user_image = models.ImageField(upload_to='images/',
                                   blank=True,
                                   null=True)
    standards_set = models.ForeignKey(standardSet,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)

    def __str__(self):
        return "%s" % (self.user)

 
class userImageUpload(models.Model):
    title	= models.CharField(max_length=20,
                        blank=True,
                        null=True)
    uploaded_image = models.ImageField(upload_to='images/question/',
                                        blank=True,
                                        null=True) 
    image_url = models.URLField(max_length=500,
                                blank=True,
                                null=True)
    created_by = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True)
    uploaded_date = models.DateField(blank=True,
                                   null=True)

    def get_remote_image(self):
        if self.image_url and not self.uploaded_image:
            result = urllib.urlretrieve(self.uploaded_image)
            self.uploaded_image.save(
                    os.path.basename(self.image_url),
                    File(open(result[0]))
                    )
            self.save()

    def __str__(self):
        return "%s" % (self.image_url)


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


class waitlistUserInfo(models.Model):
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    grade_levels = models.CharField(max_length=100)
    subjects = models.CharField(max_length=100)
    school_name = models.CharField(max_length=100)

class teacherQuestionnaire(models.Model):

    current_grade = models.CharField(max_length=100,
                                  blank=True,
                                  null=True)
    current_state = models.CharField(max_length=100,
                                  blank=True,
                                  null=True)
    current_planning = models.TextField(max_length=1000,
                                  blank=True,
                                  null=True)
    happy_scale = models.CharField(max_length=50,
                                  blank=True,
                                  null=True)
    lesson_good = models.TextField(max_length=1000,
                                  blank=True,
                                  null=True)
    lesson_bad = models.TextField(max_length=1000,
                                  blank=True,
                                  null=True)
    ideal_feature = models.TextField(max_length=1000,
                                  blank=True,
                                  null=True)

    def __str__(self):
        return "%s" % (self.happy_scale)



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
    student_pin = models.IntegerField(default = 0,
                               blank=True,
                               null=True)
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
        super(studentProfiles, self).save(*args, **kwargs)

    def __str__(self):
        return '%s %s' % (self.first_name, self.last_name)

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

 
class classroom(models.Model):
    classroom_title = models.CharField(max_length=100)
    grade_level = models.ManyToManyField(gradeLevel,
                                     blank=True,
                                     related_name='grade_level')
    single_grade = models.ForeignKey(gradeLevel,
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True,
                               related_name='single_grade')
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
    subjects = models.ManyToManyField(standardSubjects,
                                     blank=True)


    def __str__(self):
        return "%s" % (self.classroom_title)


class alertMessage(models.Model):
    created_by = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True,
                               related_name='created_alert')
    sent_to = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True,
                               related_name='recieved_alert')
    sent_date = models.DateField(blank=True,
                                   null=True)
    is_viewed = models.BooleanField(default=False)
    html_message = models.CharField(max_length=255,
                                  blank=True,
                                  null=True)
    
    def __str__(self):
        return "%s" % (self.html_message)


class studentInvitation(models.Model):
    invite_ref = models.CharField(_('Student Reference'),
                                   max_length=255,
                                   blank=True,
                                   null=True)
    first_name = models.CharField(max_length=50,
                                  blank=True,
                                  null=True)
    last_name = models.CharField(max_length=50,
                                 blank=True,
                                 null=True)
    grade_level = models.ForeignKey(gradeLevel,
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True)
    email = models.EmailField(blank=True,
                              null=True)
    for_classroom = models.ForeignKey(classroom,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    created_by = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True)
    student_profile = models.ForeignKey(studentProfiles,
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True)
    is_pending = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        # This to check if it creates a new or updates an old instance
        if self.pk is None:
            self.invite_ref= token_generator.make_token(8)
        super(studentInvitation, self).save(*args, **kwargs)

    def __str__(self):
        return "%s - %s" % (self.invite_ref, self.email)

class teacherInvitation(models.Model):
    invite_ref = models.CharField(_('Teacher Reference'),
                                   max_length=255,
                                   blank=True,
                                   null=True)
    first_name = models.CharField(max_length=50,
                                  blank=True,
                                  null=True)
    last_name = models.CharField(max_length=50,
                                 blank=True,
                                 null=True)
    email = models.EmailField(blank=True,
                              null=True)
    for_classroom = models.ForeignKey(classroom,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    created_by = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True,
                               related_name='created_by')
    new_user= models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True,
                               related_name='new_user')
    is_pending = models.BooleanField(default=True)
    is_waitlist = models.BooleanField(default=False)
    

    def save(self, *args, **kwargs):
        # This to check if it creates a new or updates an old instance
        if self.pk is None:
            self.invite_ref= token_generator.make_token(8)
        super(teacherInvitation, self).save(*args, **kwargs)

    def __str__(self):
        return "%s - %s" % (self.invite_ref, self.email)
   
class teacherInvitations(models.Model):
    invite_ref = models.CharField(_('Teacher Reference'),
                                   max_length=255,
                                   blank=True,
                                   null=True)
    first_name = models.CharField(max_length=50,
                                  blank=True,
                                  null=True)
    last_name = models.CharField(max_length=50,
                                 blank=True,
                                 null=True)
    email = models.EmailField(blank=True,
                              null=True)
    for_classroom = models.ForeignKey(classroom,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    created_by = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True,
                               related_name='created_by1')
    new_user= models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True,
                               related_name='new_user1')
    is_pending = models.BooleanField(default=True)
    is_waitlist = models.BooleanField(default=False)
    

    def save(self, *args, **kwargs):
        # This to check if it creates a new or updates an old instance
        if self.pk is None:
            self.invite_ref= token_generator.make_token(8)
        super(teacherInvitations, self).save(*args, **kwargs)

    def __str__(self):
        return "%s - %s" % (self.invite_ref, self.email)
   
class textBookTitle(models.Model):
    title = models.TextField(max_length=500)
    grade_level = models.ManyToManyField(gradeLevel,
                                     blank=True,
                                     related_name='book_grade')
    standards_set = models.ForeignKey(standardSet,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    subject = models.ForeignKey(standardSubjects,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    uploaded_by = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True)
    lesson_id_num = models.IntegerField(default = 0,
                               blank=True,
                               null=True)
    is_admin = models.BooleanField(default=False)
    wiki_page = tinymce_models.HTMLField(blank=True,
                               null=True)
    prim_topic_id = models.IntegerField(default = 0,
                               blank=True,
                               null=True)

    def __str__(self):
        return "%s" % (self.title)

class textBookBackground(models.Model):
    textbook = models.ForeignKey(textBookTitle,
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True)
    line_counter = models.IntegerField(default = 0,
                               blank=True,
                               null=True)
    page_counter = models.IntegerField(default = 0,
                               blank=True,
                               null=True)
    section = models.CharField(max_length=500,
                                  blank=True,
                                  null=True)
    header = models.CharField(max_length=500,
                                  blank=True,
                                  null=True)
    line_text = models.CharField(max_length=1000,
                                  blank=True,
                                  null=True)
    line_lemma = models.CharField(max_length=1000,
                                  blank=True,
                                  null=True)
    term_created = models.BooleanField(default=False)

    def __str__(self):
        return "%s" % (self.line_counter)


class standardsTrackingInfo(models.Model):
    track_subject = models.ForeignKey(standardSubjects,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    track_classroom = models.ForeignKey(classroom,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)


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
    is_admin = models.BooleanField(default=True)
    created_by = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True)
    
    def __str__(self):
        return "%s - %s" % (self.standard_objective, self.competency)

class topicTypes(models.Model):
    item = models.CharField(max_length=200,
                                       blank=True,
                                       null=True)	
    description = models.CharField(max_length=350,
                                       blank=True,
                                       null=True)
    
    def __str__(self):
        return "%s" % (self.item)

class questionType(models.Model):
    item = models.CharField(max_length=200,
                                       blank=True,
                                       null=True)	
    
    def __str__(self):
        return "%s" % (self.item)

class topicDescription(models.Model):
    topic_id = models.IntegerField(default = 0,
                               blank=True,
                               null=True)
    description = models.CharField(max_length=1000,
                                       blank=True,
                                       null=True)	
    created_by = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True)
    is_admin = models.BooleanField(default=True)
    is_gen = models.BooleanField(default=False)
    
    def __str__(self):
        return "%s" % (self.description)


class topicInformation(models.Model):
    subject	= models.ForeignKey(standardSubjects,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    grade_level = models.ForeignKey(gradeLevel,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True) 	
    standard_set = models.ForeignKey(standardSet,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)	
    topic = models.CharField(max_length=500,
                                       blank=True,
                                       null=True)	
    item = models.CharField(max_length=200,
                                       blank=True,
                                       null=True)	
    description	= models.ManyToManyField(topicDescription,
                                     blank=True)
    topic_type = models.ManyToManyField(topicTypes,
                                     blank=True)
    image_name = models.CharField(max_length=500,
                                        blank=True,
                                       null=True)
    image_url = models.URLField(max_length=500,
                                blank=True,
                                null=True)
    image_file = models.ImageField(upload_to='images/topic/',
                                       blank=True,
                                       null=True) 
    text_index	= models.ManyToManyField(textBookBackground,
                                     blank=True)
    created_by = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True)
    is_admin = models.BooleanField(default=True)
    from_wiki = models.BooleanField(default=False)
    is_secondary = models.BooleanField(default=False)
    topic_id = models.IntegerField(default = 0,
                               blank=True,
                               null=True)
    

    def get_remote_image(self):
        if self.image_url and not self.image_file:
            result = urllib.urlretrieve(self.image_url)
            self.image_file.save(
                    os.path.basename(self.image_url),
                    File(open(result[0]))
                    )
            self.save()

    def __str__(self):
        return "%s" % (self.item)



class LearningDemonstrationTemplate(models.Model):  
    content = models.CharField(max_length=1000,
                                       blank=True,
                                       null=True)
    topic_type = models.ManyToManyField(topicTypes,
                                     blank=True)
    subject = models.ForeignKey(standardSubjects,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    grade_level = models.ForeignKey(gradeLevel,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    is_plural = models.BooleanField(default=False)
    is_multi = models.BooleanField(default=False)

    def __str__(self):
        return "%s" % (self.content)


class LearningDemonstration(models.Model):  
    content = models.CharField(max_length=1000,
                                       blank=True,
                                       null=True)
    created_by = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True)
    topic_id = models.IntegerField(default = 0,
                               blank=True,
                               null=True)
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return "%s" % (self.content)


class classroomLists(models.Model):
    lesson_classroom = models.ForeignKey(classroom,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    students = models.ManyToManyField(studentProfiles,
                                     blank=True,
                                     related_name='classroom_students',
                               null=True)  
    year = models.IntegerField(default = 0,
                               blank=True,
                               null=True)
    academic_year = models.ForeignKey(academicYear,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)

    def __str__(self):
        return "%s" % (self.id)

class lessonObjective(models.Model):
    lesson_classroom = models.ForeignKey(classroom,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    subject = models.ForeignKey(standardSubjects,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    current_grade_level = models.ForeignKey(gradeLevel,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    week_of = models.IntegerField(default = 0,
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
    objectives_demonstration = models.ManyToManyField(LearningDemonstration,
                                     blank=True,
                                     related_name='objectives_demonstration',
                               null=True)
    objectives_topics = models.ManyToManyField(topicInformation,
                                     blank=True,
                                     related_name='objectives_topic',
                                     null=True)
    standard_set = models.ForeignKey(standardSet,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)

    def __str__(self):
        return "%s" % (self.id)



class lessonPDFImage(models.Model):
    textbook = models.ForeignKey(textBookTitle,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    page_counter = models.IntegerField(default = 0,
                               blank=True,
                               null=True)
    matched_lesson = models.ForeignKey(lessonObjective,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    image_image = models.ImageField(upload_to='images/words/',
                                       blank=True,
                                       null=True) 

    def __str__(self):
        return "%s" % (self.id)

class singleRec(models.Model):
    single_rec_topics = models.ForeignKey(topicInformation,
                                     on_delete=models.SET_NULL,
                                     blank=True,
                                     null=True)
    sim_score = models.CharField(max_length=100,
                                       blank=True,
                                       null=True)
    is_displayed = models.BooleanField(default=False)

                               
    def __str__(self):
        return "%s-%s" % (self.single_rec_topics, self.sim_score)

class reccomendedTopics(models.Model):
    matched_lesson = models.ForeignKey(lessonObjective,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    single_score = models.ManyToManyField(singleRec,
                                     blank=True,
                                     null=True)
    rec_topics = models.ManyToManyField(topicInformation,
                                     blank=True,
                                     related_name='reccomended_topics',
                                     null=True)
    removed_topics = models.ManyToManyField(topicInformation,
                                     blank=True,
                                     related_name='removed_topics',
                                     null=True)
    searched_level = models.IntegerField(default = 1,
                               blank=True,
                               null=True)

    def __str__(self):
        return "%s" % (self.id)

class lessonImageUpload(models.Model):
    matched_lesson = models.ForeignKey(lessonObjective,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    image_image = models.ImageField(upload_to='images/words/',
                                       blank=True,
                                       null=True)  
    content = models.CharField(max_length=2000,
                                       blank=True,
                                       null=True)


    def __str__(self):
        return "%s" % (self.id)


class lessonPDFImage(models.Model):
    matched_lesson = models.ForeignKey(lessonObjective,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    image_image = models.ImageField(upload_to='images/words/',
                                       blank=True,
                                       null=True)  


    def __str__(self):
        return "%s" % (self.id)


class lessonPDFText(models.Model):
    matched_lesson = models.ForeignKey(lessonObjective,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    pdf_doc = models.FileField(upload_to='file/',
                                       blank=True,
                                       null=True)
    pdf_images = models.ManyToManyField(lessonPDFImage,
                                     blank=True)
    content = models.CharField(max_length=25000,
                                       blank=True,
                                       null=True)


    def __str__(self):
        return "%s" % (self.id)


class lessonText(models.Model):
    matched_lesson = models.ForeignKey(lessonObjective,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    is_initial = models.BooleanField(default=True)
    overview = tinymce_models.HTMLField(blank=True,
                               null=True)
    introduction = tinymce_models.HTMLField(blank=True,
                               null=True)
    activities = tinymce_models.HTMLField(blank=True,
                               null=True)
    lesson_terms = tinymce_models.HTMLField(blank=True,
                               null=True)
    is_plural = models.BooleanField(default=False)
    is_multi = models.BooleanField(default=False)


    def __str__(self):
        return "%s" % (self.id)

class lessonStandardRecommendation(models.Model):
    lesson_classroom = models.ForeignKey(classroom,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    objectives = models.ForeignKey(lessonObjective,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    objectives_standard = models.ManyToManyField(singleStandard,
                                     blank=True)

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

class youtubeLine(models.Model):
    vid_id = models.CharField(max_length=1000)
    line_num = models.IntegerField(default = 0,
                               blank=True,
                               null=True)
    transcript_text = models.CharField(max_length=500)

    def __str__(self):
        return "%s" % (self.transcript_text)

class youtubeSearchResult(models.Model):
    is_selected = models.BooleanField(default=False)
    lesson_plan = models.ForeignKey(lessonObjective,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    link = models.CharField(max_length=500,
                               blank=True,
                               null=True)
    vid_id = models.CharField(max_length=1000)
    transcript_lines = models.ManyToManyField(youtubeLine,
                                     blank=True)


    def __str__(self):
        return "%s" % (self.title)

class keywordResults(models.Model):
    is_selected = models.BooleanField(default=False)
    lesson_plan = models.ForeignKey(lessonObjective,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    word = models.CharField(max_length=100,
                               blank=True,
                               null=True)
    p_o_s = models.CharField(max_length=50,
                                       blank=True,
                                       null=True)
    definition = models.CharField(max_length=600,
                               blank=True,
                               null=True)
    sentence = models.CharField(max_length=600,
                               blank=True,
                               null=True)
    relevance = models.IntegerField(default = 0,
                               blank=True,
                               null=True)


    def __str__(self):
        return "%s" % (self.word)

class wikiTopic(models.Model):
    textbook_match = models.ForeignKey(textBookTitle,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    is_selected = models.BooleanField(default=False)
    lesson_plan = models.ForeignKey(lessonObjective,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    topic = models.CharField(max_length=1000)
    term = models.CharField(max_length=300,
                               blank=True,
                               null=True)
    relevance = models.IntegerField(default = 0,
                               blank=True,
                               null=True)


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
    relevance = models.IntegerField(default = 0,
                               blank=True,
                               null=True)



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
    synonyms = models.CharField(max_length=300,
                                       blank=True,
                                       null=True)
    antonyms = models.CharField(max_length=300,
                                       blank=True,
                                       null=True)     
    matched_standard = models.ManyToManyField(singleStandard,
                                     blank=True)
                     
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



class multipleIntelligence(models.Model):
    mi = models.CharField(max_length=200,
                        blank=True,
                        null=True)	
    mi_label = models.CharField(max_length=100,
                        blank=True,
                        null=True)	
    
    def __str__(self):
        return "%s" % (self.mi)



class lessonProduct(models.Model):
    mi = models.ForeignKey(multipleIntelligence,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True) 	
    product = models.CharField(max_length=200,
                        blank=True,
                        null=True)
    topic_type = models.ManyToManyField(topicTypes,
                                     blank=True)

    def __str__(self):
        return "%s" % (self.product)



class shortStorySection(models.Model):
    title = models.CharField(max_length=500,
                        blank=True,
                        null=True)
    text = models.CharField(max_length=5000,
                        blank=True,
                        null=True)

    def __str__(self):
        return "%s" % (self.title)


class shortStory(models.Model):
    title = models.CharField(max_length=500,
                        blank=True,
                        null=True)
    author = models.CharField(max_length=200,
                        blank=True,
                        null=True)
    story_sections = models.ManyToManyField(shortStorySection,
                                     blank=True,
                                     related_name='objectives_standards')
    story_image = models.ImageField(upload_to='images/story/',
                                       blank=True,
                                       null=True) 

    def __str__(self):
        return "%s" % (self.title)

class lessonTemplates(models.Model):
    wording = models.CharField(max_length=1000,
                        blank=True,
                        null=True)
    single_topic = models.ForeignKey(topicTypes,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True) 
    components = models.ManyToManyField(topicTypes,
                                     blank=True,
                                     related_name='multi_topics')
    story = models.ForeignKey(shortStory,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True) 
    verb = models.CharField(max_length=100,
                        blank=True,
                        null=True)
    work_product = models.CharField(max_length=300,
                        blank=True,
                        null=True)
    grouping = models.CharField(max_length=500,
                        blank=True,
                        null=True)
    ks_demo = models.ForeignKey(LearningDemonstrationTemplate,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True) 
    models.CharField(max_length=1000,
                        blank=True,
                        null=True)
    bloom = models.IntegerField(default = 0,
                               blank=True,
                               null=True)
    mi = models.IntegerField(default = 0,
                               blank=True,
                               null=True)
    is_plural = models.BooleanField(default=False)
    is_multi = models.BooleanField(default=False)
    grade_level = models.ForeignKey(gradeLevel,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    subject = models.ForeignKey(standardSubjects,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)

    def __str__(self):
        return "%s" % (self.wording)


class multiSelectGS(models.Model):
    grade_level = models.ManyToManyField(gradeLevel,
                                     blank=True,
                                     related_name='select_grades')
    
    subject = models.ManyToManyField(standardSubjects,
                                     blank=True,
                                     related_name='select_subjects')


class selectedActivity(models.Model):
    created_by = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True)
    lesson_overview = models.ForeignKey(lessonObjective,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    lesson_text = models.CharField(max_length=1500,
                        blank=True,
                        null=True)
    story = models.ForeignKey(shortStory,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True) 
    verb = models.CharField(max_length=100,
                        blank=True,
                        null=True)
    work_product = models.CharField(max_length=300,
                        blank=True,
                        null=True)
    ks_demo = models.CharField(max_length=1000,
                        blank=True,
                        null=True)
    bloom = models.IntegerField(default = 0,
                               blank=True,
                               null=True)
    mi = models.IntegerField(default = 0,
                               blank=True,
                               null=True)
    ret_rate = models.IntegerField(default = 0,
                               blank=True,
                               null=True)
    template_id = models.IntegerField(default = 0,
                               blank=True,
                               null=True)
    demo_num = models.IntegerField(default = 0,
                               blank=True,
                               null=True)
    is_admin = models.BooleanField(default=False)
    is_selected = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    objectives_topics = models.ManyToManyField(topicInformation,
                                     blank=True,
                                     related_name='activitiy_topic',
                                     null=True)
    mi_labels = models.CharField(max_length=50,
                        blank=True,
                        null=True)
    bl_labels = models.CharField(max_length=50,
                        blank=True,
                        null=True)
    bl_color = models.CharField(max_length=50,
                        blank=True,
                        null=True)
    mi_color = models.CharField(max_length=50,
                        blank=True,
                        null=True)
    mi_icon  = models.CharField(max_length=50,
                        blank=True,
                        null=True)
    

    def __str__(self):
        return "%s" % (self.lesson_text)





class storySection(models.Model):
    Title = models.CharField(max_length=1000,
                        blank=True,
                        null=True)
    Section = models.CharField(max_length=10000,
                        blank=True,
                        null=True)
    Section_Image = models.ImageField(upload_to='images/story/',
                                       blank=True,
                                       null=True)

    def __str__(self):
        return "%s" % (self.Title)

class storyFull(models.Model):
    Title = models.CharField(max_length=500,
                        blank=True,
                        null=True)
    section = models.ManyToManyField(storySection,
                                     blank=True) 
    
    def __str__(self):
        return "%s" % (self.Title)

class topicQuestionitem(models.Model):
    lesson_overview = models.ForeignKey(lessonObjective,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    subject	= models.ForeignKey(standardSubjects,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    grade_level = models.ForeignKey(gradeLevel,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True) 	
    standard_set = models.ForeignKey(standardSet,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    created_by = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True)
    topic_type = models.ManyToManyField(topicTypes,
                                     blank=True)	
    topic_story = models.ManyToManyField(storyFull,
                                     blank=True)
    linked_text = models.ForeignKey(textBookBackground,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True) 
    linked_topic = models.ForeignKey(topicInformation,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True) 
    item = models.CharField(max_length=200,
                                       blank=True,
                                       null=True)	
    question_type = models.ForeignKey(questionType,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True) 
    question_points = models.IntegerField(default = 1,
                               blank=True,
                               null=True)		
    Question = models.CharField(max_length=2500,
                        blank=True,
                        null=True)	
    Question_Image = models.ForeignKey(userImageUpload,
                               on_delete=models.SET_NULL,
                               blank=True,
                               related_name='question_image',
                               null=True) 	
    Correct	= models.CharField(max_length=1000,
                        blank=True,
                        null=True)
    correct_image = models.ForeignKey(userImageUpload,
                               on_delete=models.SET_NULL,
                               blank=True,
                               related_name='correct_image',
                               null=True)	
    Incorrect_One = models.CharField(max_length=1000,
                        blank=True,
                        null=True)	
    in_one_image = models.ForeignKey(userImageUpload,
                               on_delete=models.SET_NULL,
                               blank=True,
                               related_name='Incorrect_One_image',
                               null=True) 	
    Incorrect_Two = models.CharField(max_length=1000,
                        blank=True,
                        null=True)	
    in_two_image = models.ForeignKey(userImageUpload,
                               on_delete=models.SET_NULL,
                               blank=True,
                               related_name='Incorrect_Two_image',
                               null=True) 	 	
    Incorrect_Three	= models.CharField(max_length=1000,
                        blank=True,
                        null=True)
    in_three_image = models.ForeignKey(userImageUpload,
                               on_delete=models.SET_NULL,
                               blank=True,
                               related_name='Incorrect_Three_image',
                               null=True) 	
    explanation	= models.CharField(max_length=1500,
                        blank=True,
                        null=True)
    is_admin = models.BooleanField(default=True)
    original_num = models.IntegerField(default = 0,
                               blank=True,
                               null=True)
    trans_line_num = models.IntegerField(default = 0,
                               blank=True,
                               null=True)
    is_video = models.BooleanField(default=False)	

    def __str__(self):
        return "%s" % (self.Question)


class topicQuestion(models.Model):
    lesson_overview = models.ForeignKey(lessonObjective,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    subject	= models.ForeignKey(standardSubjects,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    grade_level = models.ForeignKey(gradeLevel,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True) 	
    standard_set = models.ForeignKey(standardSet,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    created_by = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True)
    topic_type = models.ManyToManyField(topicTypes,
                                     blank=True)	
    topic_story = models.ManyToManyField(storyFull,
                                     blank=True)
    linked_text = models.ForeignKey(textBookBackground,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True) 
    linked_topic = models.ForeignKey(topicInformation,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True) 
    item = models.CharField(max_length=200,
                                       blank=True,
                                       null=True)	
    question_type = models.ForeignKey(questionType,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True) 
    question_points = models.IntegerField(default = 1,
                               blank=True,
                               null=True)		
    Question = models.CharField(max_length=2500,
                        blank=True,
                        null=True)	
	
    Correct	= models.CharField(max_length=1000,
                        blank=True,
                        null=True)

    Incorrect_One = models.CharField(max_length=1000,
                        blank=True,
                        null=True)	
 	
    Incorrect_Two = models.CharField(max_length=1000,
                        blank=True,
                        null=True)	
    	 	
    Incorrect_Three	= models.CharField(max_length=1000,
                        blank=True,
                        null=True)
    	
    explanation	= models.CharField(max_length=1500,
                        blank=True,
                        null=True)
    is_admin = models.BooleanField(default=True)
    original_num = models.IntegerField(default = 0,
                               blank=True,
                               null=True)
    trans_line_num = models.IntegerField(default = 0,
                               blank=True,
                               null=True)
    is_video = models.BooleanField(default=False)	

    def __str__(self):
        return "%s" % (self.Question)

class worksheetSection(models.Model):
    section_title	= models.CharField(max_length=200,
                        blank=True,
                        null=True)
    directions	= models.CharField(max_length=1000,
                        blank=True,
                        null=True)
    section_image = models.ImageField(upload_to='images/question/',
                                       blank=True,
                                       null=True) 
    questions = models.ManyToManyField(topicQuestionitem,
                                     blank=True)

    def __str__(self):
        return "%s" % (self.section_title)

class userNickname(models.Model):
    name = models.CharField(max_length=30,
                        blank=True,
                        null=True)
    is_firstname = models.BooleanField(default=True)

    def __str__(self):
        return "%s" % (self.name)



class worksheetTheme(models.Model):
    demo_image = models.ForeignKey(userImageUpload,
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True,
                               related_name='demo_image')
    background_image = models.ForeignKey(userImageUpload,
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True,
                               related_name='background_image')
    title = models.CharField(max_length=50,
                        blank=True,
                        null=True)
    icon_image = models.ManyToManyField(userImageUpload,
                                     blank=True,
                                     related_name='icon_image')
    first_name = models.ManyToManyField(userNickname,
                                     blank=True,
                                     related_name='first_name')
    last_name = models.ManyToManyField(userNickname,
                                     blank=True,
                                     related_name='last_name')
    primary	= models.CharField(max_length=12,
                        blank=True,
                        null=True)
    background_color = models.CharField(max_length=12,
                        blank=True,
                        null=True)
    secondary = models.CharField(max_length=12,
                        blank=True,
                        null=True)
    link = models.CharField(max_length=12,
                        blank=True,
                        null=True)
    is_admin = models.BooleanField(default=False)
    is_seasonal = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return "%s" % (self.title)

class worksheetFull(models.Model):
    created_by = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True)
    worksheet_theme = models.ForeignKey(worksheetTheme,
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True)
    lesson_overview = models.ForeignKey(lessonObjective,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    is_admin = models.BooleanField(default=False)
    is_complete = models.BooleanField(default=False)
    is_assigned = models.BooleanField(default=False)
    title	= models.CharField(max_length=200,
                        blank=True,
                        null=True)
    ws_description = models.CharField(max_length=500,
                        blank=True,
                        null=True)
    worksheet_image = models.ForeignKey(userImageUpload,
                               on_delete=models.SET_NULL,
                               blank=True,
                               related_name='worksheet_image',
                               null=True)
    questions = models.ManyToManyField(topicQuestionitem,
                                     blank=True)
    total_possible = models.IntegerField(default = 0,
                               blank=True,
                               null=True)
    grade_level = models.ForeignKey(gradeLevel,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    standards_set = models.ForeignKey(standardSet,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    subject = models.ForeignKey(standardSubjects,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)

                                

    def __str__(self):
        return "%s" % (self.title)



class matchedTopics(models.Model):
    lesson_overview = models.ForeignKey(lessonObjective,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    objectives_topics = models.ManyToManyField(topicInformation,
                                     blank=True,
                                     related_name='objectives_activity_topic',
                                     null=True)

    def __str__(self):
        return "%s" % (self.id)

class studentQuestionAnswer(models.Model):
    worksheet_assignment = models.ForeignKey(worksheetFull,
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True)
    student = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True)
    nickname = models.CharField(max_length=200,
                        blank=True,
                        null=True)
    question_num = models.ForeignKey(topicQuestionitem,
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True)
    question = models.CharField(max_length=200,
                        blank=True,
                        null=True)
    correct = models.CharField(max_length=200,
                        blank=True,
                        null=True)
    answer = models.CharField(max_length=200,
                        blank=True,
                        null=True)
    is_graded = models.BooleanField(default=False)
    is_correct = models.BooleanField(default=False)
    

    def __str__(self):
        return "%s" % (self.id)

class studentWorksheetAnswerFull(models.Model):
    worksheet_assignment = models.ForeignKey(worksheetFull,
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True)
    week_of = models.IntegerField(default = 0,
                               blank=True,
                               null=True)
    student = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='student_info',
                               blank=True,
                               null=True)
    student_profile = models.ForeignKey(studentProfiles,
                               on_delete=models.CASCADE,
                               related_name='student_info',
                               blank=True,
                               null=True)
    nickname = models.CharField(max_length=200,
                        blank=True,
                        null=True)
    student_answers = models.ManyToManyField(studentQuestionAnswer,
                                     blank=True,
                                     related_name='student_answers',
                                     null=True)
    correct_points = models.IntegerField(default = 0,
                               blank=True,
                               null=True)
    total_possible = models.IntegerField(default = 0,
                               blank=True,
                               null=True)
    score = models.IntegerField(default = 0,
                               blank=True,
                               null=True)
    is_graded = models.BooleanField(default=False)
    is_passing = models.BooleanField(default=False)
    is_submitted = models.BooleanField(default=False)
    assignment_num = models.IntegerField(default = 0,
                               blank=True,
                               null=True)
    completion_date = models.DateField(blank=True,
                                   null=True)
    assigned_by = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               blank=True,
                               related_name='assigned_by',
                               null=True)
    assigned_date = models.DateField(blank=True,
                                   null=True)
    due_date = models.DateField(blank=True,
                                   null=True)
    
    def __str__(self):
        return "%s" % (self.id)


class worksheetClassAssignment(models.Model):
    lesson_overview = models.ForeignKey(lessonObjective,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    week_of = models.IntegerField(default = 0,
                               blank=True,
                               null=True)
    subject = models.ForeignKey(standardSubjects,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    created_by = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True)
    worksheet_full = models.ForeignKey(worksheetFull,
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True)
    total_possible = models.IntegerField(default = 0,
                               blank=True,
                               null=True)
    assigned_classrooms = models.ManyToManyField(classroom,
                                     blank=True)
    student_answers = models.ManyToManyField(studentWorksheetAnswerFull,
                                     blank=True)
    due_date = models.DateField(blank=True,
                                   null=True)
    academic_year = models.ForeignKey(academicYear,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)
    
    def __str__(self):
        return "%s" % (self.id)


class studentPraiseTheme(models.Model):
    user_image = models.ImageField(upload_to='images/praise/',
                                   blank=True,
                                   null=True)
    theme_title = models.CharField(max_length=200,
                        blank=True,
                        null=True)
    
    
    def __str__(self):
        return "%s" % (self.id)

class studentPraise(models.Model):
    theme_id = models.IntegerField(default = 0,
                               blank=True,
                               null=True)
    created_by = models.IntegerField(default = 0,
                               blank=True,
                               null=True)
    student = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               blank=True,
                               null=True)
    sent_date = models.DateField(blank=True,
                                   null=True)
    week_of = models.IntegerField(default = 0,
                               blank=True,
                               null=True)

    def __str__(self):
        return "%s" % (self.id)
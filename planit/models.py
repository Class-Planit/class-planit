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


class gradeLevel(models.Model):
    grade = models.CharField(max_length=30)
    grade_labels = models.CharField(max_length=50,
                                   blank=True,
                                   null=True)
    standards_set = models.ForeignKey(standardSet,
                               on_delete=models.SET_NULL,
                               blank=True,
                               null=True)

    def __str__(self):
        return "%s" % (self.grade)

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
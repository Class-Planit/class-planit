# Generated by Django 3.1.4 on 2021-05-19 00:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('planit', '0067_worksheetfull_lesson_overview'),
    ]

    operations = [
        migrations.CreateModel(
            name='classroomList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('academic_year', models.DateField(blank=True, null=True)),
                ('lesson_classroom', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='planit.classroom')),
                ('students', models.ManyToManyField(blank=True, null=True, related_name='classroom_students', to='planit.studentProfiles')),
            ],
        ),
    ]

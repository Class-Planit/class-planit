# Generated by Django 3.1.4 on 2021-05-23 16:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('planit', '0069_auto_20210519_0121'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentworksheetanswerfull',
            name='correct_points',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='studentworksheetanswerfull',
            name='score',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='studentworksheetanswerfull',
            name='total_possible',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='studentworksheetanswerfull',
            name='week_of',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='worksheetfull',
            name='total_possible',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.CreateModel(
            name='worksheetClassAssignment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('week_of', models.IntegerField(blank=True, default=0, null=True)),
                ('total_possible', models.IntegerField(blank=True, default=0, null=True)),
                ('due_date', models.DateField(blank=True, null=True)),
                ('assigned_classrooms', models.ManyToManyField(blank=True, to='planit.classroom')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('lesson_overview', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='planit.lessonobjective')),
                ('student_answers', models.ManyToManyField(blank=True, to='planit.studentWorksheetAnswerFull')),
                ('subject', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='planit.standardsubjects')),
                ('worksheet_full', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='planit.worksheetfull')),
            ],
        ),
    ]

# Generated by Django 3.1.4 on 2021-05-12 23:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('planit', '0059_topicquestion_lesson_overview'),
    ]

    operations = [
        migrations.AddField(
            model_name='topicquestion',
            name='linked_topic',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='planit.topicinformation'),
        ),
    ]
# Generated by Django 3.1.4 on 2021-06-04 03:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planit', '0075_auto_20210604_0002'),
    ]

    operations = [
        migrations.AddField(
            model_name='selectedactivity',
            name='objectives_topics',
            field=models.ManyToManyField(blank=True, null=True, related_name='activitiy_topic', to='planit.topicInformation'),
        ),
    ]

# Generated by Django 3.1.4 on 2021-05-13 00:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planit', '0060_topicquestion_linked_topic'),
    ]

    operations = [
        migrations.AddField(
            model_name='topicdescription',
            name='topic_id',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
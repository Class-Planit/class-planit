# Generated by Django 3.1.4 on 2021-01-27 17:22

from django.db import migrations
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('planit', '0025_selectedactivity_is_selected'),
    ]

    operations = [
        migrations.AddField(
            model_name='lessontext',
            name='introduction',
            field=tinymce.models.HTMLField(blank=True, null=True),
        ),
    ]

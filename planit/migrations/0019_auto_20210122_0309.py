# Generated by Django 3.1.4 on 2021-01-22 03:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planit', '0018_lessontext_is_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lessontext',
            name='is_initial',
            field=models.BooleanField(default=True),
        ),
    ]
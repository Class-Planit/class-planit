# Generated by Django 3.1.4 on 2021-08-19 22:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planit', '0008_lessonobjective_shared_classroom'),
    ]

    operations = [
        migrations.AddField(
            model_name='alertmessage',
            name='assignment_number',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='alertmessage',
            name='praise_number',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
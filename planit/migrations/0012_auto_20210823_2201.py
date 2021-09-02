# Generated by Django 3.1.4 on 2021-08-23 22:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planit', '0011_school_user_teaching_experience'),
    ]

    operations = [
        migrations.AddField(
            model_name='school_user',
            name='school_city',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='school_user',
            name='school_country',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='school_user',
            name='school_name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
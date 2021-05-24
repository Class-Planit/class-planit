# Generated by Django 3.1.4 on 2021-05-24 01:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('planit', '0074_studentpraise_week_of'),
    ]

    operations = [
        migrations.AddField(
            model_name='classroomlist',
            name='year',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='classroomlist',
            name='academic_year',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='planit.academicyear'),
        ),
    ]

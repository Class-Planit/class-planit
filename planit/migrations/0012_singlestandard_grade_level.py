# Generated by Django 3.1.4 on 2020-12-10 17:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('planit', '0011_auto_20201210_1722'),
    ]

    operations = [
        migrations.AddField(
            model_name='singlestandard',
            name='grade_level',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='planit.gradelevel'),
        ),
    ]

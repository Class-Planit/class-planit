# Generated by Django 3.1.4 on 2021-01-22 02:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('planit', '0016_lessontext'),
    ]

    operations = [
        migrations.AddField(
            model_name='lessontext',
            name='matched_lesson',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='planit.lessonobjective'),
        ),
    ]

# Generated by Django 3.1.4 on 2021-03-14 05:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planit', '0051_learningdemonstration_topic_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='selectedactivity',
            name='template_id',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
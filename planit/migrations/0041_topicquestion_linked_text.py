# Generated by Django 3.1.4 on 2021-03-05 15:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('planit', '0040_auto_20210302_1635'),
    ]

    operations = [
        migrations.AddField(
            model_name='topicquestion',
            name='linked_text',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='planit.textbookbackground'),
        ),
    ]

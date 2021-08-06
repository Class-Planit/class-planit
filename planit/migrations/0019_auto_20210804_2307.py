# Generated by Django 3.2.4 on 2021-08-04 23:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planit', '0018_textbookbackground_term_created'),
    ]

    operations = [
        migrations.AlterField(
            model_name='topicinformation',
            name='image_name',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='topicinformation',
            name='image_url',
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
    ]

# Generated by Django 3.1.4 on 2020-12-16 18:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planit', '0030_keywordresults_relevance'),
    ]

    operations = [
        migrations.AddField(
            model_name='keywordresults',
            name='definition',
            field=models.CharField(blank=True, max_length=600, null=True),
        ),
        migrations.AddField(
            model_name='keywordresults',
            name='p_o_s',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='keywordresults',
            name='sentence',
            field=models.CharField(blank=True, max_length=600, null=True),
        ),
        migrations.AlterField(
            model_name='keywordresults',
            name='word',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]

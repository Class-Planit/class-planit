# Generated by Django 3.1.4 on 2021-03-08 15:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planit', '0045_lessontemplates_grouping'),
    ]

    operations = [
        migrations.AddField(
            model_name='selectedactivity',
            name='ks_demo',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]
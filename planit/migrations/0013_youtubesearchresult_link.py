# Generated by Django 3.1.4 on 2021-01-18 03:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planit', '0012_auto_20210117_1921'),
    ]

    operations = [
        migrations.AddField(
            model_name='youtubesearchresult',
            name='link',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]

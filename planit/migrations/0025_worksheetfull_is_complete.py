# Generated by Django 3.2.4 on 2021-08-06 19:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planit', '0024_auto_20210806_1756'),
    ]

    operations = [
        migrations.AddField(
            model_name='worksheetfull',
            name='is_complete',
            field=models.BooleanField(default=False),
        ),
    ]

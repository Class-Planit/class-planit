# Generated by Django 3.1.4 on 2020-12-07 22:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planit', '0002_auto_20201206_1805'),
    ]

    operations = [
        migrations.AddField(
            model_name='gradelevel',
            name='grade_image',
            field=models.ImageField(blank=True, null=True, upload_to='images/grades/'),
        ),
    ]

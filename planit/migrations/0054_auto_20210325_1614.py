# Generated by Django 3.1.4 on 2021-03-25 16:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('planit', '0053_auto_20210318_0454'),
    ]

    operations = [
        migrations.AlterField(
            model_name='textbookbackground',
            name='textbook',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='planit.textbooktitle'),
        ),
    ]

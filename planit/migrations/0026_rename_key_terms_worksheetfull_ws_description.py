# Generated by Django 3.2.4 on 2021-08-06 19:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('planit', '0025_worksheetfull_is_complete'),
    ]

    operations = [
        migrations.RenameField(
            model_name='worksheetfull',
            old_name='key_terms',
            new_name='ws_description',
        ),
    ]

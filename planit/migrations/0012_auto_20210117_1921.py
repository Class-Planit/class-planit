# Generated by Django 3.1.4 on 2021-01-17 19:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planit', '0011_lessontemplates_story'),
    ]

    operations = [
        migrations.AddField(
            model_name='lessontemplates',
            name='bloom',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='lessontemplates',
            name='mi',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='lessontemplates',
            name='verb',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='lessontemplates',
            name='work_product',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
    ]

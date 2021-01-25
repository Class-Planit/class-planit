# Generated by Django 3.1.4 on 2021-01-10 00:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planit', '0002_auto_20210110_0000'),
    ]

    operations = [
        migrations.CreateModel(
            name='lessonTemplates',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('wording', models.CharField(blank=True, max_length=1000, null=True)),
                ('components', models.CharField(blank=True, max_length=300, null=True)),
            ],
        ),
    ]
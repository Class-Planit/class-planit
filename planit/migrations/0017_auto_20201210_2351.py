# Generated by Django 3.1.4 on 2020-12-10 23:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('planit', '0016_auto_20201210_2239'),
    ]

    operations = [
        migrations.AddField(
            model_name='lessonfull',
            name='title',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.CreateModel(
            name='lessonSectionTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=300, null=True)),
                ('is_admin', models.BooleanField(default=False)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('lesson_section', models.ManyToManyField(blank=True, to='planit.lessonSection')),
            ],
        ),
    ]

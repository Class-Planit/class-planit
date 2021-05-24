# Generated by Django 3.1.4 on 2021-05-23 22:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('planit', '0071_studentworksheetanswerfull_assignment_num'),
    ]

    operations = [
        migrations.CreateModel(
            name='studentPraiseTheme',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_image', models.ImageField(blank=True, null=True, upload_to='images/praise/')),
                ('theme_title', models.CharField(blank=True, max_length=200, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='studentworksheetanswerfull',
            name='completion_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='studentPraise',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('theme_id', models.IntegerField(blank=True, default=0, null=True)),
                ('created_by', models.IntegerField(blank=True, default=0, null=True)),
                ('due_date', models.DateField(blank=True, null=True)),
                ('student', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
# Generated by Django 3.2.4 on 2021-08-10 16:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('planit', '0003_auto_20210810_0521'),
    ]

    operations = [
        migrations.AddField(
            model_name='singlestandard',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='singlestandard',
            name='is_admin',
            field=models.BooleanField(default=True),
        ),
    ]

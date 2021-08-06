# Generated by Django 3.2.4 on 2021-08-05 18:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('planit', '0019_auto_20210804_2307'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='city',
            field=models.CharField(default=0, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='standards_set',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='planit.standardset'),
        ),
        migrations.AddField(
            model_name='user',
            name='state',
            field=models.CharField(default=0, max_length=100),
            preserve_default=False,
        ),
    ]
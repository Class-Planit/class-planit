# Generated by Django 3.2.4 on 2021-08-04 20:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('planit', '0015_alter_singlerec_sim_score'),
    ]

    operations = [
        migrations.AddField(
            model_name='lessontemplates',
            name='single_topic',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='planit.topictypes'),
        ),
    ]

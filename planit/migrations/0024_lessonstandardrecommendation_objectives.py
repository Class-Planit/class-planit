# Generated by Django 3.1.4 on 2020-12-14 23:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('planit', '0023_auto_20201214_2234'),
    ]

    operations = [
        migrations.AddField(
            model_name='lessonstandardrecommendation',
            name='objectives',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='planit.lessonobjective'),
        ),
    ]

# Generated by Django 3.2.4 on 2021-07-11 19:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('planit', '0084_textbookbackground_term_created'),
    ]

    operations = [
        migrations.AddField(
            model_name='lessonobjective',
            name='standard_set',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='planit.standardset'),
        ),
    ]
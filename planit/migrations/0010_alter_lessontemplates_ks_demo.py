# Generated by Django 3.2.4 on 2021-07-26 17:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('planit', '0009_singlerec_is_displayed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lessontemplates',
            name='ks_demo',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='planit.learningdemonstrationtemplate'),
        ),
    ]
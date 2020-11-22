# Generated by Django 2.1 on 2020-11-15 21:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nubip', '0018_auto_20201115_2157'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='passport',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='phone_number',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='scoring_score',
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='additional_info',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='info'),
        ),
    ]
# Generated by Django 2.1 on 2020-11-21 21:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nubip', '0029_auto_20201121_2124'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='reportuserevent',
            unique_together={('report_event', 'report_user')},
        ),
    ]
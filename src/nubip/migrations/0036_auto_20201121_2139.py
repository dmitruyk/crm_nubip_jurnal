# Generated by Django 2.1 on 2020-11-21 21:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nubip', '0035_reportdataevent_report_data_user_data'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='reportuserevent',
            unique_together=set(),
        ),
    ]

# Generated by Django 2.1 on 2020-11-21 19:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nubip', '0021_userprofile_academic_group'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='membergroup',
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name='membergroup',
            name='member_group',
        ),
        migrations.RemoveField(
            model_name='membergroup',
            name='member_user',
        ),
        migrations.DeleteModel(
            name='MemberGroup',
        ),
    ]

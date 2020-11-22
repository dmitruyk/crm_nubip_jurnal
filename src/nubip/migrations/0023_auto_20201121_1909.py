# Generated by Django 2.1 on 2020-11-21 19:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('nubip', '0022_auto_20201121_1907'),
    ]

    operations = [
        migrations.CreateModel(
            name='MemberGroup',
            fields=[
                ('id', models.UUIDField(editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'Учасники',
            },
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='academic_group',
        ),
        migrations.AddField(
            model_name='academicgroup',
            name='member',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL, verbose_name='Учасник'),
        ),
        migrations.AddField(
            model_name='membergroup',
            name='member_group',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='nubip.AcademicGroup', verbose_name='Учасник'),
        ),
        migrations.AddField(
            model_name='membergroup',
            name='member_user',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL, verbose_name='Учасник'),
        ),
        migrations.AlterUniqueTogether(
            name='membergroup',
            unique_together={('member_group', 'member_user')},
        ),
    ]

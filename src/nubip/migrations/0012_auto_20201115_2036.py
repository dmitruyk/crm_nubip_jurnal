# Generated by Django 2.1 on 2020-11-15 20:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('nubip', '0011_auto_20201029_1322'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='academic_group',
        ),
        migrations.AddField(
            model_name='academicgroup',
            name='events',
            field=models.ManyToManyField(to='nubip.Event'),
        ),
        migrations.AddField(
            model_name='academicgroup',
            name='member',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL, verbose_name='Учасник'),
        ),
    ]

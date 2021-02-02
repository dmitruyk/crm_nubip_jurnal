# Generated by Django 3.1.5 on 2021-01-20 21:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('nubip', '0049_gev'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gev',
            name='user',
        ),
        migrations.AddField(
            model_name='gev',
            name='gev_event',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='report_user_gev', to='nubip.event'),
        ),
    ]
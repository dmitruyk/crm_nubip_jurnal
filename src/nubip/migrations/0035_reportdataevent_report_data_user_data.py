# Generated by Django 2.1 on 2020-11-21 21:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('nubip', '0034_remove_reportuserevent_report_data_event'),
    ]

    operations = [
        migrations.AddField(
            model_name='reportdataevent',
            name='report_data_user_data',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='report_data_user_data', to='nubip.ReportUserEvent'),
        ),
    ]

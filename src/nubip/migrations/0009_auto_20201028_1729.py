# Generated by Django 2.1 on 2020-10-28 17:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('nubip', '0008_event'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='StudentGroup',
            new_name='AcademicGroup',
        ),
        migrations.AlterModelOptions(
            name='event',
            options={'verbose_name': 'Розклад', 'verbose_name_plural': 'Розклад занять'},
        ),
        migrations.AddField(
            model_name='event',
            name='academic_group',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='nubip.AcademicGroup', verbose_name='Академічна група'),
        ),
        migrations.AddField(
            model_name='event',
            name='name',
            field=models.CharField(blank=True, default=None, max_length=25, null=True, verbose_name='Назва'),
        ),
    ]

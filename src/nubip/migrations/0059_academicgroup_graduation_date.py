# Generated by Django 3.1.5 on 2021-08-26 08:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nubip', '0058_auto_20210826_0820'),
    ]

    operations = [
        migrations.AddField(
            model_name='academicgroup',
            name='graduation_date',
            field=models.DateField(blank=True, default=None, help_text='Місяць число рік', null=True, verbose_name='Lата закінчення навчання'),
        ),
    ]

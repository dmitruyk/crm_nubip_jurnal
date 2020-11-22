# Generated by Django 2.1 on 2020-11-22 17:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('nubip', '0037_auto_20201121_2154'),
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.UUIDField(editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(blank=True, default=None, max_length=30, null=True, verbose_name='department_name')),
                ('head', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='department_head', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Кафера',
            },
        ),
        migrations.AddField(
            model_name='academicgroup',
            name='department',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='nubip.Department', verbose_name='Учасник'),
        ),
    ]
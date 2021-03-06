# Generated by Django 2.1 on 2020-10-26 19:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('nubip', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentGroup',
            fields=[
                ('id', models.UUIDField(editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(default=None, max_length=25, verbose_name='Назва')),
            ],
            options={
                'verbose_name_plural': 'Академічна група',
            },
        ),
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('headman', 'Староста'), ('curator', 'Куратор'), ('teacher', 'Викладач'), ('head_assistant', 'Заступник директора'), ('head', 'Директор')], max_length=10, verbose_name='role'),
        ),
        migrations.AddField(
            model_name='studentgroup',
            name='member',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL, verbose_name='Учасник'),
        ),
    ]

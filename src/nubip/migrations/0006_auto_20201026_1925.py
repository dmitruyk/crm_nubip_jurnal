# Generated by Django 3.1.2 on 2020-10-26 19:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nubip', '0005_auto_20201026_1912'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(blank=True, max_length=150, verbose_name='first name'),
        ),
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('headman', 'Староста'), ('curator', 'Куратор'), ('teacher', 'Викладач'), ('head_assistant', 'Заступник директора'), ('head', 'Директор')], max_length=20, verbose_name='role'),
        ),
    ]
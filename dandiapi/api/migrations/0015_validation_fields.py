# Generated by Django 3.2.4 on 2021-07-26 15:52

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('api', '0014_alter_stagingapplication_skip_authorization'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='asset',
            name='validation_error',
        ),
        migrations.RemoveField(
            model_name='version',
            name='validation_error',
        ),
        migrations.AddField(
            model_name='asset',
            name='validation_errors',
            field=models.JSONField(default=list),
        ),
        migrations.AddField(
            model_name='version',
            name='validation_errors',
            field=models.JSONField(default=list),
        ),
    ]
# Generated by Django 4.1.4 on 2023-04-10 21:09

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='ProcessedS3Log',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                (
                    'name',
                    models.CharField(
                        max_length=36,
                        validators=[
                            django.core.validators.RegexValidator(
                                '^\\d{4}-(\\d{2}-){5}[A-F0-9]{16}$'
                            )
                        ],
                    ),
                ),
                ('embargoed', models.BooleanField()),
            ],
            options={
                'unique_together': {('name', 'embargoed')},
            },
        ),
    ]
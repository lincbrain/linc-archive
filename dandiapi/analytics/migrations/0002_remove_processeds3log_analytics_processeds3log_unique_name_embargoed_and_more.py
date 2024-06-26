# Generated by Django 4.1.13 on 2024-03-20 15:59
from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('analytics', '0001_initial_v2'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='processeds3log',
            name='analytics_processeds3log_unique_name_embargoed',
        ),
        migrations.RenameField(
            model_name='processeds3log',
            old_name='embargoed',
            new_name='historically_embargoed',
        ),
        migrations.AlterField(
            model_name='processeds3log',
            name='historically_embargoed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddConstraint(
            model_name='processeds3log',
            constraint=models.UniqueConstraint(
                fields=('name', 'historically_embargoed'),
                name='analytics_processeds3log_unique_name_embargoed',
            ),
        ),
    ]

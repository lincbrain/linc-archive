# Generated by Django 4.1.13 on 2025-03-12 17:14
from __future__ import annotations

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('zarr', '0004_zarrarchive_embargoed_delete_embargoedzarrarchive'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='zarrarchive',
            name='embargoed',
        ),
    ]

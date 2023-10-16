# Generated by Django 4.1.11 on 2023-10-16 16:37

from django.db import migrations
import django_extensions.db.fields


class Migration(migrations.Migration):
    dependencies = [
        ('api', '0043_asset_asset_metadata_no_computed_keys_or_published'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='embargoedupload',
            name='modified',
        ),
        migrations.RemoveField(
            model_name='upload',
            name='modified',
        ),
        migrations.AlterField(
            model_name='embargoedupload',
            name='created',
            field=django_extensions.db.fields.CreationDateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='upload',
            name='created',
            field=django_extensions.db.fields.CreationDateTimeField(auto_now_add=True),
        ),
    ]

# Generated by Django 3.1.7 on 2021-03-23 13:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_unique_asset_blob_etag_size'),
    ]

    operations = [
        migrations.RenameField(
            model_name='upload',
            old_name='upload_id',
            new_name='multipart_upload_id',
        ),
        migrations.RenameField(
            model_name='upload',
            old_name='uuid',
            new_name='upload_id',
        ),
        migrations.RenameField(
            model_name='assetblob',
            old_name='uuid',
            new_name='blob_id',
        ),
        migrations.RenameField(
            model_name='asset',
            old_name='uuid',
            new_name='asset_id',
        ),
    ]
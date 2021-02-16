# Generated by Django 3.1.6 on 2021-02-16 22:22

from django.db import migrations, models


def set_asset_blob_size(apps, schema_editor):
    AssetBlob = apps.get_model('api', 'AssetBlob')  # noqa: N806
    db_alias = schema_editor.connection.alias
    for asset_blob in AssetBlob.objects.using(db_alias).all():
        asset_blob.size = asset_blob.blob.size
        asset_blob.save()


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_metadata_indexes'),
    ]

    operations = [
        migrations.AddField(
            model_name='assetblob',
            name='size',
            field=models.BigIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.RunPython(set_asset_blob_size),
    ]

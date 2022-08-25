# Generated by Django 4.0.6 on 2022-07-18 01:46

from django.conf import settings
from django.db import migrations, models, transaction


def populate_empty_asset_schema_versions(apps, _):
    Asset = apps.get_model('api', 'Asset')

    with transaction.atomic():
        for asset in Asset.objects.filter(metadata__schemaVersion__isnull=True).iterator():
            asset.metadata.setdefault('schemaVersion', settings.DANDI_SCHEMA_VERSION)
            asset.save(update_fields=['metadata'])


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0030_alter_embargoedzarruploadfile_blob_and_more'),
    ]

    operations = [
        migrations.RunPython(populate_empty_asset_schema_versions),
        migrations.AddConstraint(
            model_name='asset',
            constraint=models.CheckConstraint(
                check=models.Q(('metadata__schemaVersion__isnull', False)),
                name='asset_metadata_has_schema_version',
            ),
        ),
        migrations.AddConstraint(
            model_name='version',
            constraint=models.CheckConstraint(
                check=models.Q(('metadata__schemaVersion__isnull', False)),
                name='version_metadata_has_schema_version',
            ),
        ),
    ]
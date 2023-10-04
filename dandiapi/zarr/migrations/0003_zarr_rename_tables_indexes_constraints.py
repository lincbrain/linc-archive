# Generated by Django 4.1.11 on 2023-10-04 15:34

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('zarr', '0002_remove_zarruploadfile_zarr_archive_and_more'),
    ]

    # This renaming is necessary as there is a mismatch between what Django thinks the name of
    # database indexes/constraints are, and what they actually are.
    operations = [
        # Tables
        migrations.AlterModelTable(name='zarrarchive', table=None),
        migrations.AlterModelTable(name='embargoedzarrarchive', table=None),
        # Sequences
        migrations.RunSQL(
            'ALTER SEQUENCE api_zarrarchive_id_seq RENAME to zarr_zarrarchive_id_seq;'
        ),
        migrations.RunSQL(
            'ALTER SEQUENCE api_embargoedzarrarchive_id_seq RENAME to '
            'zarr_embargoedzarrarchive_id_seq;'
        ),
        # zarr_id unique constraint
        migrations.RunSQL(
            'ALTER TABLE zarr_zarrarchive RENAME CONSTRAINT "api_zarrarchive_zarr_id_key" to '
            '"zarr_zarrarchive_zarr_id_key";'
        ),
        migrations.RunSQL(
            'ALTER TABLE zarr_embargoedzarrarchive RENAME CONSTRAINT '
            '"api_embargoedzarrarchive_zarr_id_key" to "zarr_embargoedzarrarchive_zarr_id_key";'
        ),
        # primary key index
        migrations.RunSQL('ALTER INDEX "api_zarrarchive_pkey" RENAME TO "zarr_zarrarchive_pkey";'),
        migrations.RunSQL(
            'ALTER INDEX "api_embargoedzarrarchive_pkey" RENAME TO '
            '"zarr_embargoedzarrarchive_pkey";'
        ),
        # dandiset_id index
        migrations.RunSQL(
            'ALTER INDEX "api_zarrarchive_dandiset_id_68510762" RENAME TO '
            '"zarr_zarrarchive_dandiset_id_68510762";'
        ),
        migrations.RunSQL(
            'ALTER INDEX "api_embargoedzarrarchive_dandiset_id_b61f0a08" RENAME TO '
            '"zarr_embargoedzarrarchive_dandiset_id_b61f0a08";'
        ),
        # dandiset_id foreign key constraint
        migrations.RunSQL(
            'ALTER TABLE zarr_zarrarchive RENAME CONSTRAINT '
            '"api_zarrarchive_dandiset_id_68510762_fk" TO '
            '"zarr_zarrarchive_dandiset_id_68510762_fk";'
        ),
        migrations.RunSQL(
            'ALTER TABLE zarr_embargoedzarrarchive RENAME CONSTRAINT '
            '"api_embargoedzarrarchive_dandiset_id_b61f0a08_fk" TO '
            '"zarr_embargoedzarrarchive_dandiset_id_b61f0a08_fk";'
        ),
        # Constraints defined in Django
        migrations.RunSQL(
            'ALTER TABLE zarr_zarrarchive RENAME CONSTRAINT '
            '"api-zarrarchive-consistent-checksum-status" TO '
            '"zarr-zarrarchive-consistent-checksum-status";'
        ),
        migrations.RunSQL(
            'ALTER TABLE zarr_zarrarchive RENAME CONSTRAINT "api-zarrarchive-unique-name" TO '
            '"zarr-zarrarchive-unique-name";'
        ),
        migrations.RunSQL(
            'ALTER TABLE zarr_embargoedzarrarchive RENAME CONSTRAINT '
            '"api-embargoedzarrarchive-consistent-checksum-status" TO '
            '"zarr-embargoedzarrarchive-consistent-checksum-status";'
        ),
        migrations.RunSQL(
            'ALTER TABLE zarr_embargoedzarrarchive RENAME CONSTRAINT '
            '"api-embargoedzarrarchive-unique-name" TO "zarr-embargoedzarrarchive-unique-name";'
        ),
    ]

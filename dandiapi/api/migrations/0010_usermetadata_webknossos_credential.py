# Generated by Django 4.1.13 on 2024-07-07 20:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_remove_embargoedassetblob_dandiset_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='usermetadata',
            name='webknossos_credential',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
    ]
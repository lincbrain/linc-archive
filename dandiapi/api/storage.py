from typing import Any
from urllib.parse import urlsplit, urlunsplit

from django.conf import settings
from django.core.files.storage import Storage, get_storage_class
from minio_storage.policy import Policy
from minio_storage.storage import MinioStorage, create_minio_client_from_settings
from storages.backends.s3boto3 import S3Boto3Storage


class DeconstructableMinioStorage(MinioStorage):
    """
    A MinioStorage which is deconstructable by Django.

    This does not require a minio_client argument to the constructor.
    """

    def __init__(self, *args, **kwargs):
        # A minio.api.Minio instance cannot be serialized by Django. Since all constructor
        # arguments are serialized by the @deconstructible decorator, passing a Minio client as a
        # constructor argument causes makemigrations to fail.
        kwargs['minio_client'] = create_minio_client_from_settings()
        super().__init__(*args, **kwargs)


class VerbatimNameStorageMixin:
    """A Storage mixin, storing files without transforming their original filename."""

    # The basic S3Boto3Storage does not implement generate_filename or get_valid_name,
    # so upon FileField save, the following call stack normally occurs:
    #   FieldFile.save
    #   FileField.generate_filename
    #   Storage.generate_filename
    #   Storage.get_valid_name
    # Storage.generate_filename attempts to normalize the filename as a path.
    # Storage.get_valid_name uses django.utils.text.get_valid_filename,
    # which cleans spaces and other characters.
    # Since these are designed around filesystem safety, not S3 key safety, it's
    # simpler to do sanitization before saving.
    def generate_filename(self, filename: str) -> str:
        return filename


class VerbatimNameS3Storage(VerbatimNameStorageMixin, S3Boto3Storage):
    pass


class VerbatimNameMinioStorage(VerbatimNameStorageMixin, DeconstructableMinioStorage):
    pass


def create_s3_storage(bucket_name: str) -> Storage:
    """
    Return a new Storage instance, compatible with the default Storage class.

    This abstracts over differences between S3Boto3Storage and MinioStorage,
    allowing either to be used as an additional non-default Storage.
    """
    # For production, calling django.core.files.storage.get_storage_class is fine
    # to return the storage class of S3Boto3Storage.
    default_storage_class = get_storage_class()

    if issubclass(default_storage_class, S3Boto3Storage):
        storage = VerbatimNameS3Storage(bucket_name=bucket_name)
        # Required to upload to the sponsored bucket
        storage.default_acl = 'bucket-owner-full-control'
    elif issubclass(default_storage_class, MinioStorage):
        base_url = None
        if getattr(settings, 'MINIO_STORAGE_MEDIA_URL', None):
            # If a new base_url is set for the media storage, it's safe to assume one should be
            # set for this storage too.
            base_url_parts = urlsplit(settings.MINIO_STORAGE_MEDIA_URL)
            # Reconstruct the URL with an updated path
            base_url = urlunsplit(
                (
                    base_url_parts.scheme,
                    base_url_parts.netloc,
                    f'/{bucket_name}',
                    base_url_parts.query,
                    base_url_parts.fragment,
                )
            )

        # The MinioMediaStorage used as the default storage is cannot be used
        # as an ad-hoc non-default storage, as it does not allow bucket_name to be
        # explicitly set.
        storage = VerbatimNameMinioStorage(
            bucket_name=bucket_name,
            base_url=base_url,
            # All S3Boto3Storage URLs are presigned, and the bucket typically is not public
            presign_urls=True,
            auto_create_bucket=True,
            auto_create_policy=True,
            policy_type=Policy.read,
            # Required to upload to the sponsored bucket
            object_metadata={'x-amz-acl': 'bucket-owner-full-control'},
        )
        # TODO: generalize policy_type?
        # TODO: filename transforming?
        # TODO: content_type
    else:
        raise Exception(f'Unknown storage: {default_storage_class}')

    return storage


def get_storage() -> Storage:
    return create_s3_storage(settings.DANDI_DANDISETS_BUCKET_NAME)


def get_storage_prefix(instance: Any, filename: str) -> str:
    return f'{settings.DANDI_DANDISETS_BUCKET_PREFIX}{filename}'


def get_embargo_storage() -> Storage:
    return create_s3_storage(settings.DANDI_DANDISETS_EMBARGO_BUCKET_NAME)


def get_embargo_storage_prefix(instance: Any, filename: str) -> str:
    return f'{settings.DANDI_DANDISETS_BUCKET_PREFIX}{filename}'

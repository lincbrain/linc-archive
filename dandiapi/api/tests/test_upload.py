import uuid

from django.core.files.base import ContentFile
import pytest
import requests

from dandiapi.api.models import AssetBlob, Upload

from .fuzzy import HTTP_URL_RE, UUID_RE, Re


def mb(bytes_size: int) -> int:
    return bytes_size * 2 ** 20


@pytest.mark.django_db
def test_blob_read(api_client, asset_blob):

    assert api_client.post(
        '/api/blobs/digest/',
        {'algorithm': 'dandi:dandi-etag', 'value': asset_blob.etag},
        format='json',
    ).data == {
        'uuid': str(asset_blob.uuid),
        'etag': asset_blob.etag,
        'sha256': asset_blob.sha256,
        'size': asset_blob.size,
    }


@pytest.mark.django_db
def test_blob_read_bad_algorithm(api_client, asset_blob):

    resp = api_client.post(
        '/api/blobs/digest/',
        {'algorithm': 'sha256', 'value': asset_blob.sha256},
        format='json',
    )
    assert resp.status_code == 400
    assert resp.data == 'Unsupported Digest Algorithm'


@pytest.mark.django_db
def test_blob_read_does_not_exist(api_client):

    resp = api_client.post(
        '/api/blobs/digest/',
        {'algorithm': 'dandi:dandi-etag', 'value': 'not etag'},
        format='json',
    )
    assert resp.status_code == 404


@pytest.mark.django_db
def test_upload_initialize(api_client, user):
    api_client.force_authenticate(user=user)

    content_size = 123

    resp = api_client.post(
        '/api/uploads/initialize/',
        {
            'contentSize': content_size,
            'digest': {'algorithm': 'dandi:dandi-etag', 'value': 'f' * 32 + '-1'},
        },
        format='json',
    )
    assert resp.data == {
        'uuid': UUID_RE,
        'multipart_upload': {
            'object_key': Re('blobs/[a-z0-9]{3}/[a-z0-9]{3}/[a-z0-9\\-]+'),
            'upload_id': UUID_RE,
            'parts': [
                {
                    'part_number': 1,
                    'size': content_size,
                    'upload_url': HTTP_URL_RE,
                }
            ],
        },
    }

    Upload.objects.get(uuid=resp.data['uuid'])


@pytest.mark.django_db
def test_upload_initialize_existing_asset_blob(api_client, user, asset_blob):
    api_client.force_authenticate(user=user)

    resp = api_client.post(
        '/api/uploads/initialize/',
        {
            'contentSize': asset_blob.size,
            'digest': {'algorithm': 'dandi:dandi-etag', 'value': asset_blob.etag},
        },
        format='json',
    )
    assert resp.status_code == 409
    assert resp.data == 'Blob already exists.'
    assert resp.get('Location') == str(asset_blob.uuid)
    assert not Upload.objects.all().exists()


@pytest.mark.django_db
def test_upload_initialize_unauthorized(api_client):
    assert (
        api_client.post(
            '/api/uploads/initialize/',
            {},
            format='json',
        ).status_code
        == 401
    )


@pytest.mark.django_db
def test_upload_complete(api_client, user, upload):
    api_client.force_authenticate(user=user)

    content_size = 123

    assert api_client.post(
        f'/api/uploads/{upload.uuid}/complete/',
        {
            'parts': [{'part_number': 1, 'size': content_size, 'etag': 'test-etag'}],
        },
        format='json',
    ).data == {
        'complete_url': HTTP_URL_RE,
        'body': Re(r'.*'),
    }


@pytest.mark.django_db
def test_upload_complete_unauthorized(api_client, upload):
    assert (
        api_client.post(
            f'/api/uploads/{upload.uuid}/complete/',
            {},
            format='json',
        ).status_code
        == 401
    )


@pytest.mark.django_db
@pytest.mark.parametrize('content_size', [10, mb(10), mb(12)], ids=['10B', '10MB', '12MB'])
def test_upload_initialize_and_complete(api_client, user, content_size):
    api_client.force_authenticate(user=user)

    # Get the presigned upload URL
    initialization = api_client.post(
        '/api/uploads/initialize/',
        {
            'contentSize': content_size,
            'digest': {'algorithm': 'dandi:dandi-etag', 'value': 'f' * 32 + '-1'},
        },
        format='json',
    ).data

    uuid = initialization['uuid']
    parts = initialization['multipart_upload']['parts']

    # Send the data directly to the object store
    transferred_parts = []
    part_number = 1
    for part in parts:
        part_transfer = requests.put(part['upload_url'], data=b'X' * part['size'])
        etag = part_transfer.headers['etag']
        transferred_parts.append({'part_number': part_number, 'size': part['size'], 'etag': etag})
        part_number += 1

    # Get the presigned complete URL
    completion = api_client.post(
        f'/api/uploads/{uuid}/complete/',
        {
            'parts': transferred_parts,
        },
        format='json',
    ).data

    # Complete the upload to the object store
    completion_response = requests.post(completion['complete_url'], data=completion['body'])
    assert completion_response.status_code == 200

    # Verify object was uploaded
    upload = Upload.objects.get(uuid=uuid)
    assert AssetBlob.blob.field.storage.exists(upload.blob.name)


@pytest.mark.django_db
def test_upload_validate(api_client, user, upload):
    api_client.force_authenticate(user=user)

    resp = api_client.post(f'/api/uploads/{upload.uuid}/validate/')
    assert resp.status_code == 200
    assert resp.data == {
        'uuid': str(upload.uuid),
        'etag': upload.etag,
        'sha256': None,
        'size': upload.size,
    }

    # Verify that a new AssetBlob was created
    asset_blob = AssetBlob.objects.get(uuid=upload.uuid)
    assert asset_blob.blob.name == upload.blob.name

    # Verify that the Upload was deleted
    assert not Upload.objects.all().exists()


@pytest.mark.django_db
def test_upload_validate_upload_missing(api_client, user, upload):
    api_client.force_authenticate(user=user)

    upload.blob.delete(upload.blob.name)

    resp = api_client.post(f'/api/uploads/{upload.uuid}/validate/')
    assert resp.status_code == 400
    assert resp.data == ['Object does not exist.']

    assert not AssetBlob.objects.all().exists()
    assert Upload.objects.all().exists()


@pytest.mark.django_db
def test_upload_validate_wrong_size(api_client, user, upload):
    api_client.force_authenticate(user=user)

    upload.blob.save(upload.blob.name, ContentFile(b'not 100 bytes'))

    resp = api_client.post(f'/api/uploads/{upload.uuid}/validate/')
    assert resp.status_code == 400
    assert resp.data == ['Size does not match.']

    assert not AssetBlob.objects.all().exists()
    assert Upload.objects.all().exists()


@pytest.mark.django_db
def test_upload_validate_wrong_etag(api_client, user, upload):
    api_client.force_authenticate(user=user)

    upload.etag = uuid.uuid4()
    upload.save()

    resp = api_client.post(f'/api/uploads/{upload.uuid}/validate/')
    assert resp.status_code == 400
    assert resp.data == ['ETag does not match.']

    assert not AssetBlob.objects.all().exists()
    assert Upload.objects.all().exists()


@pytest.mark.django_db
def test_upload_validate_existing_assetblob(api_client, user, upload, asset_blob_factory):
    api_client.force_authenticate(user=user)

    asset_blob = asset_blob_factory(etag=upload.etag, size=upload.size)

    resp = api_client.post(f'/api/uploads/{upload.uuid}/validate/')
    assert resp.status_code == 200
    assert resp.data == {
        'uuid': str(asset_blob.uuid),
        'etag': asset_blob.etag,
        'sha256': asset_blob.sha256,
        'size': asset_blob.size,
    }

    assert AssetBlob.objects.all().count() == 1
    assert not Upload.objects.all().exists()

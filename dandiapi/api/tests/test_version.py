from datetime import datetime

from django.contrib.auth.models import User
from guardian.shortcuts import assign_perm
import pytest

from dandiapi.api import tasks
from dandiapi.api.models import Asset, Version

from .fuzzy import TIMESTAMP_RE, URN_RE, VERSION_ID_RE


@pytest.mark.django_db
def test_version_make_version_nosave(dandiset):
    # Without saving, the output should be reproducible
    version_str_1 = Version.make_version(dandiset)
    version_str_2 = Version.make_version(dandiset)
    assert version_str_1 == version_str_2
    assert version_str_1 == VERSION_ID_RE


@pytest.mark.django_db
def test_version_make_version_save(mocker, dandiset, published_version_factory):
    # Given an existing version at the current time, a different one should be allocated
    make_version_spy = mocker.spy(Version, 'make_version')
    version_1 = published_version_factory(dandiset=dandiset)
    make_version_spy.assert_called_once()

    version_str_2 = Version.make_version(dandiset)
    assert version_1.version != version_str_2


@pytest.mark.django_db
def test_draft_version_metadata_computed(draft_version, version_metadata):
    original_metadata = version_metadata.metadata
    draft_version.metadata = version_metadata

    # Save the version to add computed properties to the metadata
    draft_version.save()

    expected_metadata = {
        **original_metadata,
        'manifestLocation': [
            (
                f'https://api.dandiarchive.org/api/dandisets/{draft_version.dandiset.identifier}'
                f'/versions/draft/assets/'
            )
        ],
        'name': version_metadata.name,
        'identifier': f'DANDI:{draft_version.dandiset.identifier}',
        'version': draft_version.version,
        'id': f'DANDI:{draft_version.dandiset.identifier}/{draft_version.version}',
        'url': (
            f'https://dandiarchive.org/dandiset/'
            f'{draft_version.dandiset.identifier}/{draft_version.version}'
        ),
        '@context': 'https://raw.githubusercontent.com/dandi/schema/master/releases/0.4.4/context.json',  # noqa: E501
        'assetsSummary': {
            'numberOfBytes': 0,
            'numberOfFiles': 0,
            'schemaKey': 'AssetsSummary',
        },
    }
    expected_metadata['citation'] = draft_version.citation(expected_metadata)

    assert draft_version.metadata == expected_metadata


@pytest.mark.django_db
def test_published_version_metadata_computed(published_version, version_metadata):
    original_metadata = version_metadata.metadata
    published_version.metadata = version_metadata

    # Save the version to add computed properties to the metadata
    published_version.save()

    expected_metadata = {
        **original_metadata,
        'manifestLocation': [
            (
                f'http://localhost:9000/test-dandiapi-dandisets/test-prefix/dandisets'
                f'/{published_version.dandiset.identifier}/{published_version.version}/assets.yaml'
            )
        ],
        'name': version_metadata.name,
        'identifier': f'DANDI:{published_version.dandiset.identifier}',
        'version': published_version.version,
        'id': f'DANDI:{published_version.dandiset.identifier}/{published_version.version}',
        'url': (
            f'https://dandiarchive.org/dandiset/'
            f'{published_version.dandiset.identifier}/{published_version.version}'
        ),
        '@context': 'https://raw.githubusercontent.com/dandi/schema/master/releases/0.4.4/context.json',  # noqa: E501
        'assetsSummary': {
            'numberOfBytes': 0,
            'numberOfFiles': 0,
            'schemaKey': 'AssetsSummary',
        },
    }
    expected_metadata['citation'] = published_version.citation(expected_metadata)

    assert published_version.metadata == expected_metadata


@pytest.mark.django_db
def test_version_metadata_citation(version):
    name = version.metadata['name'].rstrip('.')
    year = datetime.now().year
    url = f'https://dandiarchive.org/dandiset/{version.dandiset.identifier}/{version.version}'
    assert (
        version.metadata['citation']
        == f'{name} ({year}). (Version {version.version}) [Data set]. DANDI archive. {url}'
    )


@pytest.mark.django_db
def test_version_metadata_citation_no_contributors(version):
    version.metadata['contributor'] = []
    version.save()

    name = version.metadata['name'].rstrip('.')
    year = datetime.now().year
    url = f'https://dandiarchive.org/dandiset/{version.dandiset.identifier}/{version.version}'
    assert (
        version.metadata['citation']
        == f'{name} ({year}). (Version {version.version}) [Data set]. DANDI archive. {url}'
    )


@pytest.mark.django_db
def test_version_metadata_citation_contributor_not_in_citation(version):
    version.metadata['contributor'] = [
        {'name': 'Jane Doe'},
        {'name': 'John Doe', 'includeInCitation': False},
    ]
    version.save()

    name = version.metadata['name'].rstrip('.')
    year = datetime.now().year
    url = f'https://dandiarchive.org/dandiset/{version.dandiset.identifier}/{version.version}'
    assert (
        version.metadata['citation']
        == f'{name} ({year}). (Version {version.version}) [Data set]. DANDI archive. {url}'
    )


@pytest.mark.django_db
def test_version_metadata_citation_contributor(version):
    version.metadata['contributor'] = [{'name': 'Doe, Jane', 'includeInCitation': True}]
    version.save()

    name = version.metadata['name'].rstrip('.')
    year = datetime.now().year
    url = f'https://dandiarchive.org/dandiset/{version.dandiset.identifier}/{version.version}'
    assert (
        version.metadata['citation']
        == f'Doe, Jane ({year}) {name} (Version {version.version}) [Data set]. '
        f'DANDI archive. {url}'
    )


@pytest.mark.django_db
def test_version_metadata_citation_multiple_contributors(version):
    version.metadata['contributor'] = [
        {'name': 'John Doe', 'includeInCitation': True},
        {'name': 'Jane Doe', 'includeInCitation': True},
    ]
    version.save()

    name = version.metadata['name'].rstrip('.')
    year = datetime.now().year
    url = f'https://dandiarchive.org/dandiset/{version.dandiset.identifier}/{version.version}'
    assert (
        version.metadata['citation']
        == f'John Doe; Jane Doe ({year}) {name} (Version {version.version}) [Data set]. '
        f'DANDI archive. {url}'
    )


@pytest.mark.django_db
def test_version_metadata_context(version):
    version.metadata['schemaVersion'] = '6.6.6'
    version.save()

    assert version.metadata['@context'] == (
        'https://raw.githubusercontent.com/dandi/schema/master/releases/6.6.6/context.json'
    )


@pytest.mark.django_db
def test_version_metadata_assets_summary_missing(version, asset):
    version.assets.add(asset)

    # Verify that an Asset with no aggregatable metadata doesn't break anything
    version.save()


@pytest.mark.django_db
def test_version_valid_with_valid_asset(version, asset):
    version.assets.add(asset)

    version.status = Version.Status.VALID
    version.save()
    asset.status = Asset.Status.VALID
    asset.save()

    assert version.valid


@pytest.mark.django_db
@pytest.mark.parametrize(
    'status',
    [
        Version.Status.PENDING,
        Version.Status.VALIDATING,
        Version.Status.INVALID,
    ],
)
def test_version_invalid(version, status):
    version.status = status
    version.save()

    assert not version.valid


@pytest.mark.django_db
@pytest.mark.parametrize(
    'status',
    [
        Asset.Status.PENDING,
        Asset.Status.VALIDATING,
        Asset.Status.INVALID,
    ],
)
def test_version_valid_with_invalid_asset(version, asset, status):
    version.assets.add(asset)

    version.status = Version.Status.VALID
    version.save()

    asset.status = status
    asset.save()

    assert not version.valid


@pytest.mark.django_db
def test_version_publish_version(draft_version, asset):
    # Normally the publish endpoint would inject a doi, so we must do it manually
    fake_doi = 'doi'

    draft_version.assets.add(asset)
    draft_version.save()

    publish_version = draft_version.publish_version
    publish_version.doi = fake_doi
    publish_version.save()

    assert publish_version.dandiset == draft_version.dandiset
    assert publish_version.metadata == {
        **draft_version.metadata,
        'publishedBy': {
            'id': URN_RE,
            'name': 'DANDI publish',
            'startDate': TIMESTAMP_RE,
            'endDate': TIMESTAMP_RE,
            'wasAssociatedWith': [
                {
                    'id': URN_RE,
                    'identifier': 'RRID:SCR_017571',
                    'name': 'DANDI API',
                    # TODO version the API
                    'version': '0.1.0',
                    'schemaKey': 'Software',
                }
            ],
            'schemaKey': 'PublishActivity',
        },
        'datePublished': TIMESTAMP_RE,
        'manifestLocation': [
            f'http://localhost:9000/test-dandiapi-dandisets/test-prefix/dandisets/'
            f'{publish_version.dandiset.identifier}/{publish_version.version}/assets.yaml',
        ],
        'identifier': f'DANDI:{publish_version.dandiset.identifier}',
        'version': publish_version.version,
        'id': f'DANDI:{publish_version.dandiset.identifier}/{publish_version.version}',
        'url': (
            f'https://dandiarchive.org/dandiset/{publish_version.dandiset.identifier}'
            f'/{publish_version.version}'
        ),
        'citation': publish_version.citation(publish_version.metadata),
        'doi': fake_doi,
        # The published_version cannot have a properly defined assetsSummary yet, since that would
        # require having created rows the Asset-to-Version join table, which is a side affect.
        'assetsSummary': {
            'numberOfBytes': 0,
            'numberOfFiles': 0,
        },
    }


@pytest.mark.django_db
def test_version_rest_list(api_client, version):
    assert api_client.get(f'/api/dandisets/{version.dandiset.identifier}/versions/').data == {
        'count': 1,
        'next': None,
        'previous': None,
        'results': [
            {
                'dandiset': {
                    'identifier': version.dandiset.identifier,
                    'created': TIMESTAMP_RE,
                    'modified': TIMESTAMP_RE,
                    'contact_person': '',
                },
                'version': version.version,
                'name': version.name,
                'created': TIMESTAMP_RE,
                'modified': TIMESTAMP_RE,
                'asset_count': 0,
                'size': 0,
                'status': 'Pending',
            }
        ],
    }


@pytest.mark.django_db
def test_version_rest_retrieve(api_client, version):
    assert (
        api_client.get(
            f'/api/dandisets/{version.dandiset.identifier}/versions/{version.version}/'
        ).data
        == version.metadata
    )


@pytest.mark.django_db
def test_version_rest_info(api_client, version):
    assert api_client.get(
        f'/api/dandisets/{version.dandiset.identifier}/versions/{version.version}/info/'
    ).data == {
        'dandiset': {
            'identifier': version.dandiset.identifier,
            'created': TIMESTAMP_RE,
            'modified': TIMESTAMP_RE,
            'contact_person': '',
        },
        'version': version.version,
        'name': version.name,
        'created': TIMESTAMP_RE,
        'modified': TIMESTAMP_RE,
        'asset_count': 0,
        'metadata': version.metadata,
        'size': version.size,
        'status': 'Pending',
        'asset_validation_errors': [],
        'version_validation_errors': [],
        'contact_person': '',
    }


@pytest.mark.django_db
@pytest.mark.parametrize(
    'asset_status,expected_validation_error',
    [
        (
            Asset.Status.PENDING,
            [{'field': '', 'message': 'asset is currently being validated, please wait.'}],
        ),
        (
            Asset.Status.VALIDATING,
            [{'field': '', 'message': 'asset is currently being validated, please wait.'}],
        ),
        (Asset.Status.VALID, []),
        (Asset.Status.INVALID, []),
    ],
)
def test_version_rest_info_with_asset(
    api_client,
    draft_version_factory,
    asset_factory,
    asset_status: Asset.Status,
    expected_validation_error: str,
):
    version = draft_version_factory(status=Version.Status.VALID)
    asset = asset_factory(status=asset_status)
    version.assets.add(asset)

    # These validation error types should have the asset path prepended to them:
    if asset_status == Asset.Status.PENDING or asset_status == Asset.Status.VALIDATING:
        expected_validation_error[0]['field'] = asset.path

    assert api_client.get(
        f'/api/dandisets/{version.dandiset.identifier}/versions/{version.version}/info/'
    ).data == {
        'dandiset': {
            'identifier': version.dandiset.identifier,
            'created': TIMESTAMP_RE,
            'modified': TIMESTAMP_RE,
            'contact_person': '',
        },
        'version': version.version,
        'name': version.name,
        'created': TIMESTAMP_RE,
        'modified': TIMESTAMP_RE,
        'asset_count': 1,
        'metadata': version.metadata,
        'size': version.size,
        'status': 'Valid' if asset_status == Asset.Status.VALID else 'Invalid',
        'asset_validation_errors': expected_validation_error,
        'version_validation_errors': [],
        'contact_person': '',
    }


@pytest.mark.django_db
def test_version_rest_update(api_client, user, draft_version):
    assign_perm('owner', user, draft_version.dandiset)
    api_client.force_authenticate(user=user)

    new_name = 'A unique and special name!'
    new_metadata = {'foo': 'bar', 'num': 123, 'list': ['a', 'b', 'c']}
    year = datetime.now().year
    url = f'https://dandiarchive.org/dandiset/{draft_version.dandiset.identifier}/draft'
    saved_metadata = {
        **new_metadata,
        'manifestLocation': [
            (
                f'https://api.dandiarchive.org/api/dandisets/{draft_version.dandiset.identifier}'
                f'/versions/draft/assets/'
            )
        ],
        'name': new_name,
        'identifier': f'DANDI:{draft_version.dandiset.identifier}',
        'id': f'DANDI:{draft_version.dandiset.identifier}/draft',
        'version': 'draft',
        'url': url,
        'citation': f'{new_name} ({year}). (Version draft) [Data set]. DANDI archive. {url}',
        'assetsSummary': {
            'numberOfBytes': 0,
            'numberOfFiles': 0,
            'schemaKey': 'AssetsSummary',
        },
    }

    assert api_client.put(
        f'/api/dandisets/{draft_version.dandiset.identifier}/versions/{draft_version.version}/',
        {'metadata': new_metadata, 'name': new_name},
        format='json',
    ).data == {
        'dandiset': {
            'identifier': draft_version.dandiset.identifier,
            'created': TIMESTAMP_RE,
            'modified': TIMESTAMP_RE,
            'contact_person': '',
        },
        'version': draft_version.version,
        'name': new_name,
        'created': TIMESTAMP_RE,
        'modified': TIMESTAMP_RE,
        'asset_count': draft_version.asset_count,
        'metadata': saved_metadata,
        'size': draft_version.size,
        'status': 'Pending',
        'asset_validation_errors': [],
        'version_validation_errors': [],
        'contact_person': '',
    }

    # The version modified date should be updated
    start_time = draft_version.modified
    draft_version.refresh_from_db()
    end_time = draft_version.modified
    assert start_time < end_time

    assert draft_version.metadata == saved_metadata
    assert draft_version.name == new_name


@pytest.mark.django_db
def test_version_rest_update_large(api_client, user, draft_version):
    assign_perm('owner', user, draft_version.dandiset)
    api_client.force_authenticate(user=user)

    new_name = 'A unique and special name!'
    new_metadata = {
        'foo': 'bar',
        'num': 123,
        'list': ['a', 'b', 'c'],
        'very_large': 'words' * 10,
    }
    year = datetime.now().year
    url = f'https://dandiarchive.org/dandiset/{draft_version.dandiset.identifier}/draft'
    saved_metadata = {
        **new_metadata,
        'manifestLocation': [
            (
                f'https://api.dandiarchive.org/api/dandisets/{draft_version.dandiset.identifier}'
                f'/versions/draft/assets/'
            )
        ],
        'name': new_name,
        'identifier': f'DANDI:{draft_version.dandiset.identifier}',
        'id': f'DANDI:{draft_version.dandiset.identifier}/draft',
        'version': 'draft',
        'url': url,
        'citation': f'{new_name} ({year}). (Version draft) [Data set]. DANDI archive. {url}',
        'assetsSummary': {
            'numberOfBytes': 0,
            'numberOfFiles': 0,
            'schemaKey': 'AssetsSummary',
        },
    }

    assert api_client.put(
        f'/api/dandisets/{draft_version.dandiset.identifier}/versions/{draft_version.version}/',
        {'metadata': new_metadata, 'name': new_name},
        format='json',
    ).data == {
        'dandiset': {
            'identifier': draft_version.dandiset.identifier,
            'created': TIMESTAMP_RE,
            'modified': TIMESTAMP_RE,
            'contact_person': '',
        },
        'version': draft_version.version,
        'name': new_name,
        'created': TIMESTAMP_RE,
        'modified': TIMESTAMP_RE,
        'asset_count': draft_version.asset_count,
        'metadata': saved_metadata,
        'size': draft_version.size,
        'status': 'Pending',
        'asset_validation_errors': [],
        'version_validation_errors': [],
        'contact_person': '',
    }

    draft_version.refresh_from_db()
    assert draft_version.metadata == saved_metadata
    assert draft_version.name == new_name


@pytest.mark.django_db
def test_version_rest_update_published_version(api_client, user, published_version):
    assign_perm('owner', user, published_version.dandiset)
    api_client.force_authenticate(user=user)

    new_name = 'A unique and special name!'
    new_metadata = {'foo': 'bar', 'num': 123, 'list': ['a', 'b', 'c']}

    resp = api_client.put(
        f'/api/dandisets/{published_version.dandiset.identifier}'
        f'/versions/{published_version.version}/',
        {'metadata': new_metadata, 'name': new_name},
        format='json',
    )
    assert resp.status_code == 405
    assert resp.data == 'Only draft versions can be modified.'


@pytest.mark.django_db
def test_version_rest_update_not_an_owner(api_client, user, version):
    api_client.force_authenticate(user=user)

    new_name = 'A unique and special name!'
    new_metadata = {'foo': 'bar', 'num': 123, 'list': ['a', 'b', 'c']}

    assert (
        api_client.put(
            f'/api/dandisets/{version.dandiset.identifier}/versions/{version.version}/',
            {'metadata': new_metadata, 'name': new_name},
            format='json',
        ).status_code
        == 403
    )


@pytest.mark.django_db
def test_version_rest_publish(api_client, user: User, draft_version: Version, asset: Asset):
    assign_perm('owner', user, draft_version.dandiset)
    api_client.force_authenticate(user=user)
    draft_version.assets.add(asset)

    # Validate the metadata to mark the version and asset as `VALID`
    tasks.validate_version_metadata(draft_version.id)
    tasks.validate_asset_metadata(asset.id)
    draft_version.refresh_from_db()
    assert draft_version.valid

    resp = api_client.post(
        f'/api/dandisets/{draft_version.dandiset.identifier}'
        f'/versions/{draft_version.version}/publish/'
    )
    assert resp.data == {
        'dandiset': {
            'identifier': draft_version.dandiset.identifier,
            'created': TIMESTAMP_RE,
            'modified': TIMESTAMP_RE,
            'contact_person': '',
        },
        'version': VERSION_ID_RE,
        'name': draft_version.name,
        'created': TIMESTAMP_RE,
        'modified': TIMESTAMP_RE,
        'asset_count': 1,
        'size': draft_version.size,
        'status': 'Valid',
    }
    published_version = Version.objects.get(version=resp.data['version'])
    assert published_version
    assert draft_version.dandiset.versions.count() == 2

    published_asset: Asset = published_version.assets.get()
    assert published_asset.published
    # The asset should be the same after publishing
    assert asset.asset_id == published_asset.asset_id

    assert published_version.metadata == {
        **draft_version.metadata,
        'publishedBy': {
            'id': URN_RE,
            'name': 'DANDI publish',
            'startDate': TIMESTAMP_RE,
            'endDate': TIMESTAMP_RE,
            'wasAssociatedWith': [
                {
                    'id': URN_RE,
                    'identifier': 'RRID:SCR_017571',
                    'name': 'DANDI API',
                    # TODO version the API
                    'version': '0.1.0',
                    'schemaKey': 'Software',
                }
            ],
            'schemaKey': 'PublishActivity',
        },
        'datePublished': TIMESTAMP_RE,
        'manifestLocation': [
            f'http://localhost:9000/test-dandiapi-dandisets/test-prefix/dandisets/'
            f'{draft_version.dandiset.identifier}/{published_version.version}/assets.yaml',
        ],
        'identifier': f'DANDI:{draft_version.dandiset.identifier}',
        'version': published_version.version,
        'id': f'DANDI:{draft_version.dandiset.identifier}/{published_version.version}',
        'url': (
            f'https://dandiarchive.org/dandiset/{draft_version.dandiset.identifier}'
            f'/{published_version.version}'
        ),
        'citation': published_version.citation(published_version.metadata),
        'doi': f'10.80507/dandi.{draft_version.dandiset.identifier}/{published_version.version}',
        # Once the assets are linked, assetsSummary should be computed properly
        'assetsSummary': {
            'schemaKey': 'AssetsSummary',
            'numberOfBytes': 100,
            'numberOfFiles': 1,
            'dataStandard': [
                {
                    'schemaKey': 'StandardsType',
                    'identifier': 'RRID:SCR_015242',
                    'name': 'Neurodata Without Borders (NWB)',
                }
            ],
            'approach': [],
            'measurementTechnique': [],
            'variableMeasured': [],
            'species': [],
        },
    }

    draft_version.refresh_from_db()
    assert draft_version.status == Version.Status.PUBLISHED
    assert not draft_version.valid


@pytest.mark.django_db
def test_version_rest_publish_assets(
    api_client,
    user: User,
    draft_version: Version,
    draft_asset_factory,
    published_asset_factory,
):
    assign_perm('owner', user, draft_version.dandiset)
    api_client.force_authenticate(user=user)

    old_draft_asset: Asset = draft_asset_factory()
    old_published_asset: Asset = published_asset_factory()
    old_published_asset.publish()
    old_published_asset.save()
    assert not old_draft_asset.published
    assert old_published_asset.published
    draft_version.assets.add(old_draft_asset)
    draft_version.assets.add(old_published_asset)

    # Validate the metadata to mark the assets and version as `VALID`
    tasks.validate_asset_metadata(old_draft_asset.id)
    tasks.validate_asset_metadata(old_published_asset.id)
    tasks.validate_version_metadata(draft_version.id)
    draft_version.refresh_from_db()
    assert draft_version.valid

    resp = api_client.post(
        f'/api/dandisets/{draft_version.dandiset.identifier}'
        f'/versions/{draft_version.version}/publish/'
    )
    assert resp.status_code == 200
    published_version = Version.objects.get(version=resp.data['version'])

    assert published_version.assets.count() == 2
    new_draft_asset: Asset = published_version.assets.get(asset_id=old_draft_asset.asset_id)
    new_published_asset: Asset = published_version.assets.get(asset_id=old_published_asset.asset_id)

    # The former draft asset should have been modified into a published asset
    assert new_draft_asset.published
    assert new_draft_asset.asset_id == old_draft_asset.asset_id
    assert new_draft_asset.path == old_draft_asset.path
    assert new_draft_asset.blob == old_draft_asset.blob
    assert new_draft_asset.metadata == {
        **old_draft_asset.metadata,
        'datePublished': TIMESTAMP_RE,
        'publishedBy': {
            'id': URN_RE,
            'name': 'DANDI publish',
            'startDate': TIMESTAMP_RE,
            # TODO endDate needs to be defined before publish is complete
            'endDate': TIMESTAMP_RE,
            'wasAssociatedWith': [
                {
                    'id': URN_RE,
                    'identifier': 'RRID:SCR_017571',
                    'name': 'DANDI API',
                    'version': '0.1.0',
                    'schemaKey': 'Software',
                }
            ],
            'schemaKey': 'PublishActivity',
        },
    }

    # The published_asset should be completely unchanged
    assert new_published_asset.published
    assert new_published_asset.asset_id == old_published_asset.asset_id
    assert new_published_asset.path == old_published_asset.path
    assert new_published_asset.blob == old_published_asset.blob
    assert new_published_asset.metadata == old_published_asset.metadata


@pytest.mark.django_db
def test_version_rest_publish_not_an_owner(api_client, user, version, asset):
    api_client.force_authenticate(user=user)
    version.assets.add(asset)

    resp = api_client.post(
        f'/api/dandisets/{version.dandiset.identifier}/versions/{version.version}/publish/'
    )
    assert resp.status_code == 403


@pytest.mark.django_db
def test_version_rest_publish_not_a_draft(api_client, user, published_version, asset):
    assign_perm('owner', user, published_version.dandiset)
    api_client.force_authenticate(user=user)
    published_version.assets.add(asset)

    resp = api_client.post(
        f'/api/dandisets/{published_version.dandiset.identifier}'
        f'/versions/{published_version.version}/publish/'
    )
    assert resp.status_code == 405


@pytest.mark.django_db
@pytest.mark.parametrize(
    'status',
    [
        Version.Status.PENDING,
        Version.Status.VALIDATING,
        Version.Status.INVALID,
    ],
)
def test_version_rest_publish_invalid_metadata(api_client, user, draft_version, asset, status):
    assign_perm('owner', user, draft_version.dandiset)
    api_client.force_authenticate(user=user)
    draft_version.assets.add(asset)

    draft_version.status = status
    draft_version.save()

    resp = api_client.post(
        f'/api/dandisets/{draft_version.dandiset.identifier}'
        f'/versions/{draft_version.version}/publish/'
    )
    assert resp.status_code == 400
    assert resp.data == 'Dandiset metadata or asset metadata is not valid'

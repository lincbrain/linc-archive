from __future__ import annotations

from celery import shared_task
from celery.utils.log import get_task_logger
import requests

from dandiapi.api.doi import delete_doi
from dandiapi.api.mail import send_dandiset_unembargo_failed_message
from dandiapi.api.manifests import (
    write_assets_jsonld,
    write_assets_yaml,
    write_collection_jsonld,
    write_dandiset_jsonld,
    write_dandiset_yaml,
)
from dandiapi.api.models import Asset, AssetBlob, Version
from dandiapi.api.models.dandiset import Dandiset

logger = get_task_logger(__name__)


@shared_task(soft_time_limit=60)
def remove_asset_blob_embargoed_tag_task(blob_id: str) -> None:
    from dandiapi.api.services.embargo import remove_asset_blob_embargoed_tag

    asset_blob = AssetBlob.objects.get(blob_id=blob_id)
    remove_asset_blob_embargoed_tag(asset_blob)


@shared_task(queue='calculate_sha256', soft_time_limit=86_400)
def calculate_sha256(blob_id: str) -> None:
    asset_blob = AssetBlob.objects.get(blob_id=blob_id)
    logger.info('Found AssetBlob %s', blob_id)
    sha256 = asset_blob.blob.storage.sha256_checksum(asset_blob.blob.name)

    # TODO: Run dandi-cli validation

    AssetBlob.objects.filter(blob_id=blob_id).update(sha256=sha256)


@shared_task(soft_time_limit=180)
def write_manifest_files(version_id: int) -> None:
    version: Version = Version.objects.get(id=version_id)
    logger.info('Writing manifests for version %s:%s', version.dandiset.identifier, version.version)

    write_dandiset_yaml(version)
    write_assets_yaml(version)
    write_dandiset_jsonld(version)
    write_assets_jsonld(version)
    write_collection_jsonld(version)


@shared_task(soft_time_limit=10)
def validate_asset_metadata_task(asset_id: int) -> None:
    from dandiapi.api.services.metadata import validate_asset_metadata

    asset: Asset = Asset.objects.filter(id=asset_id, status=Asset.Status.PENDING).first()
    if asset:
        validate_asset_metadata(asset=asset)


@shared_task(soft_time_limit=30)
def validate_version_metadata_task(version_id: int) -> None:
    from dandiapi.api.services.metadata import validate_version_metadata

    version: Version = Version.objects.get(id=version_id)
    validate_version_metadata(version=version)


@shared_task
def delete_doi_task(doi: str) -> None:
    delete_doi(doi)


@shared_task
def publish_dandiset_task(dandiset_id: int):
    from dandiapi.api.services.publish import _publish_dandiset

    _publish_dandiset(dandiset_id=dandiset_id)


@shared_task
def register_external_api_request_task(method: str, external_endpoint: str, payload: dict = None,
                             query_params: dict = None):
    """
    Register a celery task that performs an API request to an external service.

    :param method: HTTP method to use for the request ('GET' or 'POST')
    :param external_endpoint: URL of the external API endpoint
    :param payload: Dictionary payload to send in the POST request (for 'POST' method)
    :param query_params: Dictionary of query parameters to send in the GET request
        (for 'GET' method)
    """
    headers = {
        'Content-Type': 'application/json',
    }
    try:
        if method.upper() == 'POST':
            requests.post(external_endpoint, json=payload, headers=headers, timeout=10)
        elif method.upper() == 'GET':
            response = requests.get(external_endpoint, params=query_params, headers=headers,
                                    timeout=10)
            try:
                return {'status_code': response.status_code, 'headers': response.headers}
            except Exception:
                logger.warning("Issue with GET response to %s", external_endpoint)
        else:
            logger.error("Unsupported HTTP method: %s", method)
            return

    except requests.exceptions.HTTPError:
        logger.exception("HTTP error occurred")
    except requests.exceptions.RequestException:
        logger.exception("Request exception occurred")
    except Exception:
        logger.exception("An unexpected error occurred")

@shared_task(soft_time_limit=1200)
def unembargo_dandiset_task(dandiset_id: int):
    from dandiapi.api.services.embargo import unembargo_dandiset

    ds = Dandiset.objects.get(pk=dandiset_id)

    # If the unembargo fails for any reason, send an email, but continue the error propagation
    try:
        unembargo_dandiset(ds)
    except Exception:
        send_dandiset_unembargo_failed_message(ds)
        raise

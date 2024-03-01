from __future__ import annotations

from typing import TYPE_CHECKING

from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from dandiapi.api.utils import get_presigned_cookies
import rsa
from botocore.signers import CloudFrontSigner

import datetime

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from botocore.signers import CloudFrontSigner


def rsa_signer(message):
    import os
    path = f'{os.getcwd()}/dandiapi/api/privkey.pem'
    with open(path, 'rb') as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )
    return private_key.sign(message, padding.PKCS1v15(), hashes.SHA1())


def get_presigned_url():
    key_id = 'K350HZY8RS1FBD'  # pkcs1 -- lincbrain AWS
    object_url = 'https://neuroglancer.lincbrain.org/sample_file.txt'
    expire_date = datetime.datetime(2025, 10, 12)

    cloudfront_signer = CloudFrontSigner(key_id, rsa_signer)

    # Create a signed url that will be valid until the specific expiry date
    # provided using a canned policy.
    signed_url = cloudfront_signer.generate_presigned_url(
        object_url, date_less_than=expire_date)
    return signed_url


import datetime

if TYPE_CHECKING:
    from django.http.response import HttpResponseBase
    from rest_framework.request import Request

@swagger_auto_schema(
    method='GET',
    responses={200: None},
    operation_summary='Provides presigned cookie for retrieving S3 assets exposed '
                      'via AWS CloudFront Distributions',
    operation_description='',
)
@api_view(['GET'])
@parser_classes([JSONParser])
@permission_classes([IsAuthenticated])
def presigned_cookie_s3_cloudfront_view(request: Request) -> HttpResponseBase:


    response_data = {"message": get_presigned_url()}
    response = Response(response_data)

    cookies = {}
    for cookie_name, cookie_value in cookies.items():
        response.set_cookie(
            key=cookie_name,
            value=cookie_value,
            secure=True,
            httponly=True,
            domain=".lincbrain.org"
        )

    return response

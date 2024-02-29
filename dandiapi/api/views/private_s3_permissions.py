from __future__ import annotations

from typing import TYPE_CHECKING

from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from dandiapi.api.utils import CloudFrontCookieGenerator

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
    expires_in_minutes = 20

    key_pair_id = 'K2NDLB5TAPBON9'  # thursday -- lincbrain AWS
    object_url = 'https://neuroglancer.lincbrain.org/*'

    cloudfront_cookie_generator = CloudFrontCookieGenerator()
    expires_at = int((datetime.datetime.utcnow() + datetime.timedelta(minutes=expires_in_minutes)).timestamp())

    cookies = cloudfront_cookie_generator.create_signed_cookies(
        resource=object_url,
        keypair_id=key_pair_id,
        expires_at=expires_at
    )

    response_data = {"message": "Cookies successfully generated"}
    response = Response(response_data)
    for cookie_name, cookie_value in cookies.items():
        response.set_cookie(
            key=cookie_name,
            value=cookie_value,
            secure=True,
            httponly=True,
            domain=".lincbrain.org"
        )

    return response

from __future__ import annotations

import os

from django.contrib.auth.models import User
from django.db import models, transaction
from django.utils.crypto import get_random_string
from django_extensions.db.models import TimeStampedModel


class UserMetadata(TimeStampedModel):
    class Status(models.TextChoices):
        INCOMPLETE = 'INCOMPLETE'
        PENDING = 'PENDING'
        APPROVED = 'APPROVED'
        REJECTED = 'REJECTED'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='metadata')
    status = models.CharField(choices=Status.choices, default=Status.INCOMPLETE, max_length=10)
    questionnaire_form = models.JSONField(blank=True, null=True)
    rejection_reason = models.TextField(blank=True, default='', max_length=1000)
    webknossos_credential = models.CharField(max_length=128, blank=True, null=True)  # noqa: DJ001

    def should_register_webknossos_account(self, api_url=None) -> bool:

        return (self.status == self.Status.APPROVED and
                not self.webknossos_credential and
                api_url)

    def register_webknossos_account(self, webknossos_api_url: str, webknossos_credential: str) -> None:

        webknossos_organization_name = os.getenv('WEBKNOSSOS_ORGANIZATION_NAME', None)
        webknossos_organization_display_name = os.getenv('WEBKNOSSOS_ORGANIZATION_DISPLAY_NAME',
                                                         None)

        # Offset to celery task to call /register in WebKNOSSOS
        from dandiapi.api.tasks import register_external_api_request_task

        register_external_api_request_task.delay(
            method='POST',
            external_endpoint='https://webknossos.lincbrain.org/api/auth/register',
            payload={
                "firstName": self.user.first_name,
                "lastName": self.user.last_name,
                "email": self.user.email,
                "organization": "LINC",
                "organizationName": "LINC",
                "password": {
                    "password1": webknossos_credential,
                    "password2": webknossos_credential
                }
            }
        )

    def save(self, *args, **kwargs):

        with transaction.atomic():

            super().save(*args, **kwargs)

            is_new_instance = self.pk is None
            if not is_new_instance:
                webknossos_api_url = os.getenv('WEBKNOSSOS_API_URL', None)

                if self.should_register_webknossos_account(api_url=webknossos_api_url):

                    random_password = get_random_string(length=12)
                    self.webknossos_credential = random_password
                    self.register_webknossos_account(webknossos_api_url=webknossos_api_url, webknossos_credential=random_password)
                    #  Slightly recursive call, but will halt with WebKNOSSOS logic
                    super().save(*args, **kwargs)




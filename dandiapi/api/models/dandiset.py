from __future__ import annotations

from typing import Optional

from django.db import models
from django_extensions.db.models import TimeStampedModel
from guardian.shortcuts import assign_perm, get_users_with_perms, remove_perm


class Dandiset(TimeStampedModel):
    # Don't add beginning and end markers, so this can be embedded in larger regexes
    IDENTIFIER_REGEX = r'\d{6}'

    EMBARGOED = 'EMBARGOED'
    UNEMBARGOING = 'UNEMBARGOING'
    OPEN = 'OPEN'
    EMBARGO_STATUS_CHOICES = [
        (EMBARGOED, 'Embargoed'),
        (UNEMBARGOING, 'Unembargoing'),
        (OPEN, 'Open'),
    ]

    embargo_status = models.CharField(
        max_length=max(len(choice[0]) for choice in EMBARGO_STATUS_CHOICES),
        choices=EMBARGO_STATUS_CHOICES,
        default=OPEN,
    )

    class Meta:
        ordering = ['id']
        permissions = [('owner', 'Owns the dandiset')]

    @property
    def identifier(self) -> Optional[str]:
        # Compare against None, to allow id 0
        return f'{self.id:06}' if self.id is not None else ''

    @property
    def most_recent_published_version(self):
        return self.versions.exclude(version='draft').order_by('modified').last()

    @property
    def draft_version(self):
        return self.versions.filter(version='draft').get()

    @property
    def owners(self):
        return get_users_with_perms(self, only_with_perms_in=['owner']).order_by('date_joined')

    def set_owners(self, new_owners):
        old_owners = get_users_with_perms(self, only_with_perms_in=['owner'])

        removed_owners = []
        added_owners = []

        # Remove old owners
        for old_owner in old_owners:
            if old_owner not in new_owners:
                remove_perm('owner', old_owner, self)
                removed_owners.append(old_owner)

        # Add new owners
        for new_owner in new_owners:
            if new_owner not in old_owners:
                assign_perm('owner', new_owner, self)
                added_owners.append(new_owner)

        # Return the owners added/removed so they can be emailed
        return removed_owners, added_owners

    def add_owner(self, new_owner):
        old_owners = get_users_with_perms(self, only_with_perms_in=['owner'])
        if new_owner not in old_owners:
            assign_perm('owner', new_owner, self)

    def remove_owner(self, owner):
        owners = get_users_with_perms(self, only_with_perms_in=['owner'])
        if owner in owners:
            remove_perm('owner', owner, self)

    @classmethod
    def published_count(cls):
        """Return the number of Dandisets with published Versions."""
        # Prevent circular import
        from .version import Version

        # It's not possible to efficiently filter by a reverse relation (.versions),
        # so this is an efficient alternative
        return Version.objects.exclude(version='draft').values('dandiset').distinct().count()

    def __str__(self) -> str:
        return self.identifier

from __future__ import absolute_import
from collections import defaultdict

from django.core.cache import cache

from api.v1.models import ApiExclusion


__author__ = 'josh'


def resolve_permissions(user):
    permissions = cache.get(u'sc_api_user_permissions_{0}'.format(user.pk))
    if permissions is None:
        permissions = defaultdict(list)
        if not user.is_anonymous:
            api_exclusions = ApiExclusion.objects.filter(user=user)
        else:
            api_exclusions = ApiExclusion.objects.none()
        for exclusion in api_exclusions:
            permissions[exclusion.resource].append(exclusion.field)
        cache.set(u'sc_api_user_permissions_{0}'.format(user.pk), permissions, 120)
    return permissions
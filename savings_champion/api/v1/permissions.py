from rest_framework import permissions
from rest_framework.authtoken.models import Token

__author__ = 'josh'


class HasToken(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.is_authenticated():
            if Token.objects.filter(user=request.user).exists():
                return True
        return False
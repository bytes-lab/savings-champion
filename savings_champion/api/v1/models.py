from django.conf import settings
from django.db import models
from django_extensions.db.fields import UUIDField

__author__ = 'josh'


class ApiExclusion(models.Model):
    uuid = UUIDField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    resource = models.TextField()
    field = models.TextField()


class ApiExcludedItem(models.Model):
    uuid = UUIDField(primary_key=True)
    name = models.TextField(default='')
    email = models.EmailField()

    def __unicode__(self):
        return self.name
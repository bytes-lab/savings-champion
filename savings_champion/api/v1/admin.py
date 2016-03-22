from django.contrib import admin
from api.v1.models import ApiExclusion

__author__ = 'josh'

class ApiExclusionAdmin(admin.ModelAdmin):
    pass

admin.site.register(ApiExclusion, ApiExclusionAdmin)
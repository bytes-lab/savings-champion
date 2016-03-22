from django.contrib import admin
from ifa.models import IFASignup, BJSignup


class IFAAdmin(admin.ModelAdmin):
    list_display = ('name','email', 'created_date', 'last_updated')

admin.site.register(IFASignup,IFAAdmin)

class BJAdmin(admin.ModelAdmin):
    list_display = ('name','email', 'created_date', 'last_updated')

admin.site.register(BJSignup,BJAdmin)
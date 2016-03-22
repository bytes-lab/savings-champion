from django.contrib import admin

from rate_tracker.models import RatetrackerAlert


class RatetrackerAlertAdmin(admin.ModelAdmin):
    list_display = ('user', 'last_updated')
    list_filter = ('authorised',)
    search_fields = ('user__email',)
    readonly_fields = ('user',)


admin.site.register(RatetrackerAlert, RatetrackerAlertAdmin)

from django.contrib import admin
from thisismoney.models import TiMSignups

class TiMSignupsAdmin(admin.ModelAdmin):
    list_display = ('email', 'completed_signup', 'completed_activation', 'last_updated', 'created_date')
    search_fields = ('email',)
    fieldsets = (
        (None, {
            'fields': ('email', 'completed_signup')
        }),
        )
    
admin.site.register(TiMSignups,TiMSignupsAdmin)

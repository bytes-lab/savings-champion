from django.contrib import admin
from concierge.models import ConciergeUserPool, ConciergeUserOption, ConciergeUserProviderRisk, EmailTemplate, \
    ConciergeProviderAccountTypeLimitation


class ConciergeUserPoolAdmin(admin.ModelAdmin):
    pass

class ConciergeUserOptionAdmin(admin.ModelAdmin):
    pass


class ConciergeUserProviderRiskAdmin(admin.ModelAdmin):
    pass


class ConciergeEmailTemplateAdmin(admin.ModelAdmin):
    pass


class ConciergeProviderAccountTypeLimitationAdmin(admin.ModelAdmin):
    pass

admin.site.register(ConciergeUserPool, ConciergeUserPoolAdmin)
admin.site.register(ConciergeUserOption, ConciergeUserOptionAdmin)
admin.site.register(ConciergeUserProviderRisk, ConciergeUserProviderRiskAdmin)
admin.site.register(EmailTemplate, ConciergeEmailTemplateAdmin)
admin.site.register(ConciergeProviderAccountTypeLimitation, ConciergeProviderAccountTypeLimitationAdmin)
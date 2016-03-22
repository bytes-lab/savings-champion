from django.contrib.auth import get_user_model
from common.models import Profile, Rates, AuthorProfile, Tweet, RateAlertsSignup, NewsletterSignup, CampaignsSignup, \
    ReminderSignup, \
    CarouselTab, UserReferral
from django.contrib import admin
from common.forms import AuthorProfileForm, ProfileForm, CarouselForm
from common.actions import mark_synched, mark_unsynched, update_salesforce_user
from django.contrib.auth.admin import UserAdmin

User = get_user_model()


class BaseModelAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}


class RatesAdmin(admin.ModelAdmin):
    list_display = ('boe_rate', 'inflation_rate', 'last_updated', 'created_date')


class ProfileAdmin(admin.ModelAdmin):
    list_display = (
    'user', 'full_name', 'user_email', 'newsletter', 'ratealerts', 'created_date', 'is_synched', 'source')
    search_fields = ('user__email', 'source', 'ip_address', 'user__username',)
    list_filter = ('created_date', 'newsletter', 'ratealerts',)
    form = ProfileForm
    readonly_fields = ('user', 'is_synched')
    fieldsets = (
        (None, {
            'fields': (
            'salutation', 'user', 'dob', 'telephone', 'postcode', 'newsletter', 'ratealerts', 'is_synched', 'source',
            'skeleton_user', 'filled_in_name', 'ip_address')
        }),
    )
    actions = [mark_synched, mark_unsynched]


class AuthorProfileAdmin(admin.ModelAdmin):
    form = AuthorProfileForm


class SignUpAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_synched', 'created_date', 'source')
    search_fields = ('email',)
    actions = [mark_synched, mark_unsynched]


class CampaignAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_client', 'name', 'is_synched', 'created_date', 'source')
    search_fields = ('email', 'name')
    actions = [mark_synched, mark_unsynched]


class TweetAdmin(admin.ModelAdmin):
    list_display = ('title', 'last_updated', 'created_date')


class CarouselAdmin(admin.ModelAdmin):
    form = CarouselForm


class MyUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    actions = [update_salesforce_user]


class ReminderAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_synched', 'created_date', 'healthcheck', 'bestbuys')
    search_fields = ('email',)
    actions = [mark_synched, mark_unsynched]
    list_filter = ('healthcheck', 'bestbuys',)


class UserReferralAdmin(admin.ModelAdmin):
    pass


admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)

admin.site.register(CarouselTab, CarouselAdmin)
admin.site.register(Tweet, TweetAdmin)
admin.site.register([RateAlertsSignup, NewsletterSignup], SignUpAdmin)
admin.site.register(CampaignsSignup, CampaignAdmin)

admin.site.register(Rates, RatesAdmin)
# admin.site.register([UserNext, UUIDNext], admin.ModelAdmin)
admin.site.register(AuthorProfile, AuthorProfileAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(ReminderSignup, ReminderAdmin)
admin.site.register(UserReferral, UserReferralAdmin)
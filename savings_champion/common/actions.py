from common.utils import ResponseError, get_subscription_bitmask
from common.models import CampaignsSignup, Profile
from common.management.commands.utils.salesforce_sync import init_client

def mark_synched(modeladmin, request, queryset):
    queryset.update(is_synched=True)
    
def mark_unsynched(modeladmin, request, queryset):
    queryset.update(is_synched=False)

def update_salesforce_user(modeladmin, request, queryset):
    SFResponseCodes =["SUCCESS", "ERR_USERID_EXISTS", "ERR_USERID_NOT_FOUND", "ERR_PORTFOLIOID_NOT_FOUND", "ERR_PORTFOLIOID_EXISTS"]
    django_client = init_client()
    for user in queryset:
        try:
            try:
                profile = user.profile
            except Profile.DoesNotExist:
                profile = Profile(user=user)
                profile.save()
            except Profile.MultipleObjectsReturned:
                profiles = Profile.objects.filter(user=user)
                profile = profiles[0]
            bitmask = get_subscription_bitmask(profile)
            if CampaignsSignup.objects.filter(email = user.email).exists():
                bitmask += 16
            bitmask += 8

            returncode = django_client.service.updateUser2('%s' % profile.user.id,
                        profile.user.username,
                        profile.user.email,
                        user.first_name,
                        user.last_name,
                        profile.dob,
                        profile.telephone,
                        profile.salutation,
                        profile.postcode,
                        bitmask,
                        profile.user.is_active,
                    )
            if returncode[1] > 0:
                raise ResponseError(returncode)

        except ResponseError as e:
            modeladmin.message_user(request, "%s went wrong" % SFResponseCodes[returncode])
        except Exception as e:
            modeladmin.message_user(request, "%s Occured to %s" % (e, user.email))
    modeladmin.message_user(request, "User updated")

mark_synched.short_description = "Mark as synced"
mark_unsynched.short_description = "Mark as unsynced"
update_salesforce_user.short_description = "Sync changes with Salesforce"

def update_salesforce_user_task(queryset):
    SFResponseCodes =["SUCCESS", "ERR_USERID_EXISTS", "ERR_USERID_NOT_FOUND", "ERR_PORTFOLIOID_NOT_FOUND", "ERR_PORTFOLIOID_EXISTS"]
    django_client = init_client()
    for user in queryset:
        try:
            profile = user.profile
        except Profile.DoesNotExist:
            profile = Profile(user=user)
            profile.save()
        except Profile.MultipleObjectsReturned:
            profiles = Profile.objects.filter(user=user)
            profile = profiles[0]
        bitmask = get_subscription_bitmask(profile)
        if CampaignsSignup.objects.filter(email=user.email).exists():
            bitmask += 16
        bitmask += 8

        returncode = django_client.service.updateUser2('%s' % profile.user.id,
                    profile.user.username,
                    profile.user.email,
                    user.first_name,
                    user.last_name,
                    profile.dob,
                    profile.telephone,
                    profile.salutation,
                    profile.postcode,
                    bitmask,
                    profile.user.is_active,
                )
        if returncode > 0:
            raise ResponseError(returncode)

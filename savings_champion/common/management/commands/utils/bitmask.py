from common.models import NewsletterSignup, RateAlertsSignup, CampaignsSignup, ReminderSignup, Profile
#the profile is now king of whether the flags are set (as the user can directly change it)
#rate alert syncing and newsletter syncing will first set the flags on the profile but after the initial creation it's left alone
from ifa.models import IFASignup, BJSignup
from pages.models import Petition, SevenPitfallsSignup
from products.models import WeeklyRateAlert


def get_bitmask(user):
    bitmask = 0
    try:
        profile = user.profile
    except Profile.DoesNotExist:
        profile = Profile(user=user)
        profile.save()
    except Profile.MultipleObjectsReturned:
        profiles = Profile.objects.filter(user=user)
        profile = profiles[0]
    if not profile.skeleton_user and profile.filled_in_name:
        #ratetracker user
        bitmask += 8
    if profile.newsletter:
        bitmask += 1
        #WILL HAVE TO CHECK FOR ACTIVE
    if profile.ratealerts:
        bitmask += 2

    if CampaignsSignup.objects.filter(email__iexact=user.email).exists():
        #concierge ENQUIRY
        bitmask += 16
        try:
            concierge = CampaignsSignup.objects.get(email__iexact=user.email)
        except CampaignsSignup.MultipleObjectsReturned:
            concierge = CampaignsSignup.objects.filter(email__iexact=user.email)
            concierge[1].delete()
            concierge = concierge[0]
        if concierge.is_client:
            bitmask += 32

    if ReminderSignup.objects.filter(email__iexact=user.email).exists():
        try:
            reminder = ReminderSignup.objects.get(email__iexact=user.email)
        except ReminderSignup.MultipleObjectsReturned:
            reminder = ReminderSignup.objects.filter(email__iexact=user.email)
            reminder[1].delete()
            reminder = reminder[0]
        if reminder.healthcheck:
            bitmask += 128
        if reminder.bestbuys:
            bitmask += 64
        reminder.is_synched = True
        reminder.save()
    if WeeklyRateAlert.objects.filter(email__iexact=user.email).exists():
        try:
            weekly_rate_alert = WeeklyRateAlert.objects.get(email__iexact=user.email)
        except WeeklyRateAlert.MultipleObjectsReturned:
            weekly_rate_alert = WeeklyRateAlert.objects.filter(email__iexact=user.email)
            weekly_rate_alert[1].delete()
            weekly_rate_alert = weekly_rate_alert[0]
        if weekly_rate_alert.frequency == 1:
            bitmask += 256
        elif weekly_rate_alert.frequency == 2:
            bitmask += 512
        elif weekly_rate_alert.frequency == 3:
            bitmask += 1024
    if IFASignup.objects.filter(email__iexact=user.email).exists():
        bitmask += 2048
    if BJSignup.objects.filter(email__iexact=user.email).exists():
        bitmask += 4096
    if Petition.objects.filter(email__iexact=user.email).exists():
        bitmask += 8192
    if SevenPitfallsSignup.objects.filter(email__iexact=user.email).exists():
        bitmask += 16384
    return bitmask


def set_initial_flags(user, profile):
    if NewsletterSignup.objects.filter(email__iexact=user.email).exists():
        profile.newsletter = True
        try:
            signup = NewsletterSignup.objects.get(email__iexact=user.email)
        except NewsletterSignup.MultipleObjectsReturned:
            signup = NewsletterSignup.objects.filter(email__iexact=user.email)
            signup[1].delete()
            signup = signup[0].get()
        signup.is_synched = True
        signup.save()
        if signup.source:
            profile.source = signup.source
    else:
        profile.newsletter = False

    if RateAlertsSignup.objects.filter(email__iexact=user.email).exists():
        profile.ratealerts = True
        try:
            signup = RateAlertsSignup.objects.get(email__iexact=user.email)
        except RateAlertsSignup.MultipleObjectsReturned:
            signup = RateAlertsSignup.objects.filter(email__iexact=user.email)
            signup[1].delete()
            signup = signup[0].get()
        signup.is_synched = True
        signup.save()
        if signup.source:
            profile.source = signup.source
    else:
        profile.ratealerts = False

    #just using this to set the source
    if CampaignsSignup.objects.filter(email__iexact=user.email).exists():
        try:
            signup = CampaignsSignup.objects.get(email__iexact=user.email)
        except CampaignsSignup.MultipleObjectsReturned:
            signup = CampaignsSignup.objects.filter(email__iexact=user.email)
            signup[1].delete()
            signup = signup[0].get()
        if signup.source:
            profile.source = signup.source

    profile.save()
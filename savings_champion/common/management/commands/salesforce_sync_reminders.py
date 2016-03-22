"""
Users can sign up to just Newsletters and RateAlerts, which we need to make sure
is also synced with SalesForce. Annoyingly I have to create dummy users to fit 
this condition.
"""
import os
import datetime
import string
from random import Random
import re
from celery.task import task
from django.contrib.auth import get_user_model
from django.core.management.base import NoArgsCommand
from django.conf import settings
from django.core.mail import send_mail
from common.models import ReminderSignup, NewsletterSignup, RateAlertsSignup
from common.management.commands.utils.salesforce_sync import init_client
from common.management.commands.utils.bitmask import get_bitmask, set_initial_flags
from common.models import Profile
from common.utils import ResponseError


User = get_user_model()

INT_RE = re.compile('\d+')

USERNAME_STEM = 'SCuser_'
SALESFORCE_SYNC_ALERTS_PATH = getattr(settings, 'SALESFORCE_SYNC_ALERTS_PATH')


class Command(NoArgsCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    def _get_start_date(self, dte):
        dte = self._get_query_date(dte)
        return datetime.datetime.combine(dte.date(), datetime.time.min)

    def _get_end_date(self, dte):
        dte = self._get_query_date(dte)
        return datetime.datetime.combine(dte.date(), datetime.time.max)

    def _get_query_date(self, dte, minus_days=1):
        #return dte + datetime.timedelta(days = -minus_days)
        return dte - datetime.timedelta(minutes=10)

    def _in_other_list(self, email, queryset):
        for signup in queryset:
            if email == signup.email:
                return True
        return False

    @task(ignore_result=True)
    def sync_reminder_signup(self, SFResponseCodes, django_client, reminder_signup, sync_message, synched):
        new_user = False
        try:
            user = User.objects.get(email__iexact=reminder_signup.email)
            try:
                profile = user.profile
            except Profile.DoesNotExist:
                profile = Profile(user=user)
                profile.save()
            set_initial_flags(user, profile)
        except User.DoesNotExist:
            new_user = True
            user = self._create_new_user_skeleton(reminder_signup)
            profile = Profile()
            profile.user = user
            profile.skeleton_user = True
            profile.filled_in_name = False
            profile.save()
            set_initial_flags(user, profile)

        sync_message.append("Reminder, ")
        bitmask = get_bitmask(user)
        if bitmask > 0:
            returncode = 5
            try:
                returncode = self._process_salesforce_sync(django_client, profile, user, new_user, bitmask)

                if returncode > 0:
                    raise ResponseError(returncode)

                profile.is_synched = True
                profile.save()

                reminder_signup.is_synched = True
                reminder_signup.save()

                if synched >= 400:
                    return

            except ResponseError as e:
                send_mail('Sync Error',
                          "The following error occurred while syncing reminders or instructions for %s: %s" % (
                              profile.user.email, SFResponseCodes[returncode]),
                          settings.DEFAULT_FROM_EMAIL,
                          ['admin@savingschampion.co.uk'], fail_silently=False)


    def alert_adjustment_sync(self, django_client):
        synched_emails = []
        synched = 0
        sync_message = []
        today = datetime.datetime.now()
        date_format = today.strftime('%Y%m%d')
        
        fn = os.path.join(SALESFORCE_SYNC_ALERTS_PATH % date_format)
        f1 = open(fn, 'ab')
        
        SFResponseCodes =["SUCCESS", "ERR_USERID_EXISTS", "ERR_USERID_NOT_FOUND", "ERR_PORTFOLIOID_NOT_FOUND", "ERR_PORTFOLIOID_EXISTS", "Process failed before returning a response code."]
        # First, sync users associated with the newsletter
        reminder_signups = ReminderSignup.objects.exclude(is_synched=True)
        for reminder_signup in reminder_signups:
            self.sync_reminder_signup.delay()(SFResponseCodes, django_client, reminder_signup, sync_message, synched)
                
        f1.close()
        # Send an email with the number of signups synched

    def _create_new_user_skeleton(self, signup):
        user = User()
        user.username = self._make_username()
        user.is_active = False
        user.email = signup.email
        user.set_password(self._make_random_password())
        user.save()
        return user

    def _process_salesforce_sync(self, django_client, profile, user, new_user, bitmask, first_name='', last_name = ''):
        newsletterActive = False
        ratealertsActive = False
        
        if profile.user.is_active:
            newsletterActive = True
            ratealertsActive = True
        else:
            if NewsletterSignup.objects.filter(email=profile.user.email).exists():
                signup = NewsletterSignup.objects.get(email=profile.user.email)
                if signup.is_activated:
                    newsletterActive = True
                    ratealertsActive = True
                else:
                    if RateAlertsSignup.objects.filter(email=profile.user.email).exists():
                        signup = RateAlertsSignup.objects.get(email=profile.user.email)
                        if signup.is_activated:
                            newsletterActive = True
                            ratealertsActive = True
            elif RateAlertsSignup.objects.filter(email=profile.user.email).exists():
                signup = RateAlertsSignup.objects.get(email=profile.user.email)
                if signup.is_activated:
                    newsletterActive = True
                    ratealertsActive = True
        
        if new_user:
            return django_client.service.newUser5('%s' % profile.user.id,
                profile.user.username,
                profile.user.email,
                first_name,
                last_name,
                '',
                '',
                '',
                '',
                bitmask,
                profile.source,
                '',
                '',
                False,
                profile.user.date_joined,
                ratealertsActive,
                newsletterActive,
            )
        else:
            return django_client.service.updateUser3('%s' % profile.user.id,
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
                profile.source,
                ratealertsActive,
                newsletterActive,
            )
    def handle_noargs(self, **options):
        """ 
        When logging into the salesforce api we have to append our security token to the end
        """

        dte = self._get_query_date(datetime.datetime.now())        
        django_client = init_client()

        self.alert_adjustment_sync(django_client)


    def _make_username(self):
        username = '%s%s' % (USERNAME_STEM, self._make_random())
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
            #mail_admins('SalesForce Alerts Sync Issue', 'Unable to create dummy users')

    def _make_random_password(self, length=8, chars=string.letters + string.digits):
        return self._make_random()

    def _make_random(self, length=8, chars=string.letters + string.digits):
        newpasswd = ''.join(Random().sample(string.letters + string.digits, 12))
        return newpasswd



def _get_start_date(dte):
    dte = _get_query_date(dte)
    return datetime.datetime.combine(dte.date(), datetime.time.min)


def _get_end_date(dte):
    dte = _get_query_date(dte)
    return datetime.datetime.combine(dte.date(), datetime.time.max)


def _get_query_date(dte, minus_days=1):
    # return dte + datetime.timedelta(days = -minus_days)
    return dte - datetime.timedelta(minutes=10)


def _in_other_list(email, queryset):
    for signup in queryset:
        if email == signup.email:
            return True
    return False


@task(ignore_result=True)
def sync_reminder_signup(SFResponseCodes, django_client, reminder_signup, sync_message, synched):
    new_user = False
    try:
        user = User.objects.get(email__iexact=reminder_signup.email)
        try:
            profile = user.profile
        except Profile.DoesNotExist:
            profile = Profile(user=user)
            profile.save()
        set_initial_flags(user, profile)
    except User.DoesNotExist:
        new_user = True
        user = _create_new_user_skeleton(reminder_signup)
        profile = Profile()
        profile.user = user
        profile.skeleton_user = True
        profile.filled_in_name = False
        profile.save()
        set_initial_flags(user, profile)

    sync_message.append("Reminder, ")
    bitmask = get_bitmask(user)
    if bitmask > 0:
        returncode = 5
        try:
            returncode = _process_salesforce_sync(django_client, profile, user, new_user, bitmask)

            if returncode > 0:
                raise ResponseError(returncode)

            profile.is_synched = True
            profile.save()

            reminder_signup.is_synched = True
            reminder_signup.save()

            if synched >= 400:
                return

        except ResponseError as e:
            send_mail('Sync Error',
                      "The following error occurred while syncing reminders or instructions for %s: %s" % (
                          profile.user.email, SFResponseCodes[returncode]),
                      settings.DEFAULT_FROM_EMAIL,
                      ['admin@savingschampion.co.uk'], fail_silently=False)


def alert_adjustment_sync(django_client):
    synched_emails = []
    synched = 0
    sync_message = []
    today = datetime.datetime.now()
    date_format = today.strftime('%Y%m%d')

    fn = os.path.join(SALESFORCE_SYNC_ALERTS_PATH % date_format)
    f1 = open(fn, 'ab')

    SFResponseCodes = ["SUCCESS", "ERR_USERID_EXISTS", "ERR_USERID_NOT_FOUND", "ERR_PORTFOLIOID_NOT_FOUND",
                       "ERR_PORTFOLIOID_EXISTS", "Process failed before returning a response code."]
    # First, sync users associated with the newsletter
    reminder_signups = ReminderSignup.objects.exclude(is_synched=True)
    for reminder_signup in reminder_signups:
        sync_reminder_signup.delay()(SFResponseCodes, django_client, reminder_signup, sync_message, synched)

    f1.close()
    # Send an email with the number of signups synched


def _create_new_user_skeleton(signup):
    user = User()
    user.username = _make_username()
    user.is_active = False
    user.email = signup.email
    user.set_password(_make_random_password())
    user.save()
    return user


def _process_salesforce_sync(django_client, profile, user, new_user, bitmask, first_name='', last_name=''):
    newsletterActive = False
    ratealertsActive = False

    if profile.user.is_active:
        newsletterActive = True
        ratealertsActive = True
    else:
        if NewsletterSignup.objects.filter(email=profile.user.email).exists():
            signup = NewsletterSignup.objects.get(email=profile.user.email)
            if signup.is_activated:
                newsletterActive = True
                ratealertsActive = True
            else:
                if RateAlertsSignup.objects.filter(email=profile.user.email).exists():
                    signup = RateAlertsSignup.objects.get(email=profile.user.email)
                    if signup.is_activated:
                        newsletterActive = True
                        ratealertsActive = True
        elif RateAlertsSignup.objects.filter(email=profile.user.email).exists():
            signup = RateAlertsSignup.objects.get(email=profile.user.email)
            if signup.is_activated:
                newsletterActive = True
                ratealertsActive = True

    if new_user:
        return django_client.service.newUser5('%s' % profile.user.id,
                                              profile.user.username,
                                              profile.user.email,
                                              first_name,
                                              last_name,
                                              '',
                                              '',
                                              '',
                                              '',
                                              bitmask,
                                              profile.source,
                                              '',
                                              '',
                                              False,
                                              profile.user.date_joined,
                                              ratealertsActive,
                                              newsletterActive,
        )
    else:
        return django_client.service.updateUser3('%s' % profile.user.id,
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
                                                 profile.source,
                                                 ratealertsActive,
                                                 newsletterActive,
        )


def handle_noargs(**options):
    """
    When logging into the salesforce api we have to append our security token to the end
    """

    dte = _get_query_date(datetime.datetime.now())
    django_client = init_client()

    alert_adjustment_sync(django_client)


def _make_username():
    username = '%s%s' % (USERNAME_STEM, _make_random())
    try:
        User.objects.get(username=username)
    except User.DoesNotExist:
        return username
        # mail_admins('SalesForce Alerts Sync Issue', 'Unable to create dummy users')


def _make_random_password(length=8, chars=string.letters + string.digits):
    return _make_random()


def _make_random(length=8, chars=string.letters + string.digits):
    newpasswd = ''.join(Random().sample(string.letters + string.digits, 12))
    return newpasswd
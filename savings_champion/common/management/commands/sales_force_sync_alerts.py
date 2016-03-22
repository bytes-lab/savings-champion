"""
Users can sign up to just Newsletters and RateAlerts, which we need to make sure
is also synced with SalesForce. Annoyingly I have to create dummy users to fit 
this condition.
"""
from django.contrib.auth import get_user_model
from django.core.management.base import NoArgsCommand
import os, datetime
from django.conf import settings
from common.models import RateAlertsSignup, NewsletterSignup, CampaignsSignup
from common.management.commands.utils.salesforce_sync import init_client
from common.management.commands.utils.bitmask import get_bitmask, set_initial_flags
from django.core.mail import send_mail
import string
from random import Random
from common.models import Profile
import re
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

    def alert_adjustment_sync(self, django_client):
        synched_emails = []
        synched = 0
        sync_message = []
        today = datetime.datetime.now()
        date_format = today.strftime('%Y%m%d')
        
        fn = os.path.join(SALESFORCE_SYNC_ALERTS_PATH % date_format)
        f1 = open(fn, 'ab')
        
        SFResponseCodes =["SUCCESS", "ERR_USERID_EXISTS", "ERR_USERID_NOT_FOUND", "ERR_PORTFOLIOID_NOT_FOUND", "ERR_PORTFOLIOID_EXISTS"]
        # First, sync users associated with the newsletter
        news_signups = NewsletterSignup.objects.exclude(is_synched=True)
        for news_signup in news_signups:
            new_user = False
            try:
                user = User.objects.get(email__iexact=news_signup.email)
                try:
                    profile = user.profile
                except Profile.DoesNotExist:
                    profile = Profile(user=user)
                    profile.save()
                set_initial_flags(user, profile)                
            except User.DoesNotExist:
                new_user = True
                user = self._create_new_user_skeleton(news_signup)
                profile = Profile()
                profile.user = user
                profile.skeleton_user = True
                profile.filled_in_name = False
                profile.save()
                set_initial_flags(user, profile)
            
            sync_message.append("Newsletter, ")
            if profile.ratealerts:
                sync_message.append("Rate Alerts, ")
            
            bitmask = get_bitmask(user)
            if bitmask > 0:
                try:
                    returncode = self._process_salesforce_sync(django_client, profile, user, new_user, bitmask)
                    
                    if returncode > 0:
                            raise ResponseError(returncode)
                        
                    synched += 1
                    
                    profile.is_synched = True
                    profile.save()                
        
                    if CampaignsSignup.objects.filter(email=user.email).exists():
                        sync_message.append("Concierge, ")
                        campaign_object = CampaignsSignup.objects.get(email=user.email)
                        campaign_object.is_synched = True
                        campaign_object.save()
                        
                    f1.write("Synced %s for %s \n" % ("".join(sync_message), user.email))
                    sync_message = []
                    synched_emails.append(user.email)
                    news_signup.is_synched = True
                    news_signup.save()
                    if synched >= 400:
                        break
                
                except ResponseError as e:
                    send_mail('Sync Error', 
                          "The following error occurred while syncing alerts for %s: %s" % (profile.user.email, SFResponseCodes[returncode]), 
                          settings.DEFAULT_FROM_EMAIL,
                          ['admin@savingschampion.co.uk'], fail_silently=False)
                
        # Secondly, sync users associated with rate alerts that aren't on the newsletter
        rate_signups = RateAlertsSignup.objects.exclude(is_synched=True)
        if synched < 400:
            for rate_signup in rate_signups:
                new_user = False
                try:
                    user = User.objects.get(email__iexact=rate_signup.email)
                    try:
                        profile = user.profile
                    except Profile.DoesNotExist:
                        profile = Profile(user=user)
                        profile.save()
                    set_initial_flags(user, profile)
                except User.DoesNotExist:                        
                    new_user = True
                    user = self._create_new_user_skeleton(rate_signup)
                    profile = Profile()
                    profile.user = user
                    profile.newsletter = False
                    profile.skeleton_user = True
                    profile.filled_in_name = False
                    profile.save()
                    set_initial_flags(user, profile)
                    
                sync_message.append("Rate Alerts, ")
                bitmask = get_bitmask(user)
                
                if bitmask > 0:
                    try:
                        returncode = self._process_salesforce_sync(django_client, profile, user, new_user, bitmask)
                    
                        if returncode > 0:
                            raise ResponseError(returncode)
                        
                        synched += 1
                        rate_signup.is_synched = True
                        rate_signup.save()
                        profile.is_synched = True
                        profile.save()
                        if CampaignsSignup.objects.filter(email=user.email).exists():
                            sync_message.append("Concierge, ")
                            campaign_object = CampaignsSignup.objects.get(email=user.email)
                            campaign_object.is_synched = True
                            campaign_object.save()
                            
                        f1.write("Synced %s for %s \n" % ("".join(sync_message), user.email))
                        sync_message = []
                        synched_emails.append(user.email)
                        if synched >= 400:
                            break
                        
                    except ResponseError as e:
                        send_mail('Sync Error', 
                          "The following error occurred while syncing alerts for %s: %s" % (profile.user.email, SFResponseCodes[returncode]), 
                          settings.DEFAULT_FROM_EMAIL,
                          ['admin@savingschampion.co.uk'], fail_silently=False)
        
        # Lastly, sync the campaign signups that aren't on rate signups or news signups
        campaign_signups = CampaignsSignup.objects.exclude(is_synched=True)
        if synched < 400:
            for campaign_signup in campaign_signups:                
                new_user = False
                first_name = ''
                last_name = ''

                try:
                    user = User.objects.get(email__iexact=campaign_signup.email)
                    try:
                        profile = user.profile
                    except Profile.DoesNotExist:
                        profile = Profile(user=user)
                        profile.save()
                    first_name = user.first_name
                    last_name = user.last_name
                    set_initial_flags(user, profile)
                except User.DoesNotExist:
                    new_user = True
                    user = self._create_new_user_skeleton(campaign_signup)
                    #user.is_active = True #requested by Jack Linstead for the rate tracker concierge emails.
                    user.save() 
                    # Try and split out the name into something usable to pass across to Salesforce
                    names = campaign_signup.name.split()
                    profile = Profile()
                    profile.user = user
                    profile.skeleton_user = True
                    profile.filled_in_name = False
                    profile.save()
                    set_initial_flags(user, profile)
                    try:
                        if len(names) == 1:
                            last_name = names[0]
                        else:
                            # Guesswork required, assume that only the last component is the last name
                            last_name = names.pop()
                            first_name = ' '.join(names)
                    except:
                        first_name = "Not Provided"
                        last_name = "Not Provided"
                
                    user.first_name = first_name
                    user.last_name = last_name
                    user.save()
                    
                sync_message.append("Concierge, ")
                bitmask = get_bitmask(user)
                if bitmask > 0:
                    try:
                        returncode = self._process_salesforce_concierge_sync(django_client, profile, user, new_user, bitmask, campaign_signup, first_name, last_name)
                        
                        if returncode > 0:
                            raise ResponseError(returncode)
                        
                        synched += 1
                        
                        campaign_signup.is_synched = True
                        campaign_signup.save()
                        profile.is_synched = True
                        profile.save()
                        f1.write("Synced %s for %s \n" % ("".join(sync_message), user.email))
                        sync_message = []
                        synched_emails.append(user.email)
                        if synched >= 400:
                            break
                        
                    except ResponseError as e:
                        send_mail('Sync Error', 
                          "The following error occurred while syncing alerts for %s: %s" % (profile.user.email, SFResponseCodes[returncode]), 
                          settings.DEFAULT_FROM_EMAIL,
                          ['admin@savingschampion.co.uk'], fail_silently=False)
        f1.close()

    def _create_new_user_skeleton(self, signup):
        user = User()
        user.username = self._make_username()
        user.is_active = False
        user.email = signup.email
        user.set_password(self._make_random_password())
        user.save()
        return user

    def _process_salesforce_sync(self, django_client, profile, user, new_user, bitmask, first_name = '', last_name = ''):
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
    def _process_salesforce_concierge_sync(self, django_client, profile, user, new_user, bitmask, campaign_signup, first_name = '', last_name = ''):
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
                campaign_signup.telephone,
                '',
                '',
                bitmask,
                profile.source,
                campaign_signup.alt_telephone,
                campaign_signup.best_call_time,
                profile.user.is_active,
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
    

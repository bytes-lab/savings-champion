"""
Users can sign up to just Newsletters and RateAlerts, which we need to make sure
is also synced with SalesForce. Annoyingly I have to create dummy users to fit 
this condition.
"""
from django.contrib.auth import get_user_model
from django.core.management.base import NoArgsCommand
from products.models import ProductPortfolio, RatetrackerReminder
import os, datetime
from common.models import RateAlertsSignup, NewsletterSignup, CampaignsSignup
from django.core.mail import send_mail
from django.conf import settings
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

    def _get_subscription_bitmask(self, profile):
        retval = 0
        if profile.newsletter:
            retval += 1

        if profile.ratealerts:
            retval += 2
        return retval

    def _in_other_list(self, email, queryset):
        for signup in queryset:
            if email == signup.email:
                return True
        return False

    def alert_adjustment_sync(self, django_client, news_signups, rate_signups, campaign_signups):
        synched_emails = []
        synched = 0
        sync_message = []
        today = datetime.datetime.now()
        date_format = today.strftime('%Y%m%d')
        
        fn = os.path.join(SALESFORCE_SYNC_ALERTS_PATH % date_format)
        f1 = open(fn, 'ab')
        
        SFResponseCodes =["SUCCESS", "ERR_USERID_EXISTS", "ERR_USERID_NOT_FOUND", "ERR_PORTFOLIOID_NOT_FOUND", "ERR_PORTFOLIOID_EXISTS"]
        # First, sync users associated with the newsletter
        for news_signup in news_signups:
            new_user = False
            try:
                user = User.objects.get(email__iexact=news_signup.email)
                try:
                    profile = user.profile
                except Profile.DoesNotExist:
                    profile = Profile(user=user)
                    profile.save()
                if profile.ratealerts:
                    sync_message.append("Rate Alerts, ")
            except User.DoesNotExist:
                new_user = True
                user = self._create_new_user_skeleton(news_signup)
                profile = Profile()
                profile.user = user
                profile.skeleton_user = True
                profile.save()
                if self._in_other_list(user.email, rate_signups):
                    profile.ratealerts = True
                    sync_message.append("Rate Alerts, ")
            except Exception as ex:
                print "The following %s caused %s" % (news_signup, ex)
            profile.newsletter = True
            sync_message.append("Newsletter, ")
            bitmask = self._get_subscription_bitmask(profile)
            if self._in_other_list(user.email, campaign_signups):
                bitmask += 16
                sync_message.append("Concierge, ")
            if ProductPortfolio.objects.filter(user = user).count() > 0:
                sync_message.append("Rate Tracker, ")
                bitmask += 8
            elif RatetrackerReminder.objects.filter(user = user).count() > 0:
                sync_message.append("Rate Tracker, ")
                bitmask += 8
            elif not new_user:
                bitmask += 8
            try:
                returncode = 0
                
                if returncode > 0:
                        raise ResponseError(returncode)
                    
                synched += 1
                
                profile.is_synched = True
                profile.save()
    
                news_signup.is_synched = True
                news_signup.save()
    
                if profile.ratealerts:
                    try:
                        ratealert_object = RateAlertsSignup.objects.get(email=user.email)
                    except RateAlertsSignup.DoesNotExist:
                        ratealert_object = RateAlertsSignup()
    
                    ratealert_object.is_synched = True
                    ratealert_object.save()
    
                if self._in_other_list(user.email, campaign_signups):
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
                      settings.CSV_EXPORT_RECIPIENTS, fail_silently=False)
            except Exception as ex:
                print "The following %s caused %s" % (news_signup, ex)
                
        # Secondly, sync users associated with rate alerts that aren't on the newsletter
        if synched < 400:
            for rate_signup in rate_signups:
                if rate_signup.email not in synched_emails:
                    new_user = False
                    try:
                        user = User.objects.get(email__iexact=rate_signup.email)
                        try:
                            profile = user.profile
                        except Profile.DoesNotExist:
                            profile = Profile(user=user)
                        profile.save()

                    except User.DoesNotExist:                        
                        new_user = True
                        user = self._create_new_user_skeleton(rate_signup)
                        profile = Profile()
                        profile.user = user
                        profile.newsletter = False
                        profile.skeleton_user = True
                        profile.save()
                    except Exception as ex:
                        print "The following %s caused %s" % (rate_signup, ex)
                    profile.ratealerts = True
                    sync_message.append("Rate Alerts, ")
                    bitmask = self._get_subscription_bitmask(profile)
                    if self._in_other_list(user.email, campaign_signups):
                        bitmask += 16
                        sync_message.append("Concierge, ")
                    if ProductPortfolio.objects.filter(user = user).count() > 0:
                        bitmask += 8
                        sync_message.append("Rate Tracker, ")
                    elif RatetrackerReminder.objects.filter(user = user).count() > 0:
                        bitmask += 8
                        sync_message.append("Rate Tracker, ")
                    elif not new_user:
                        bitmask += 8
                    try:
                        returncode = 0
                    
                        if returncode > 0:
                            raise ResponseError(returncode)
                        
                        synched += 1
                        rate_signup.is_synched = True
                        rate_signup.save()
                        profile.is_synched = True
                        profile.save()
                        if self._in_other_list(user.email, campaign_signups):
                            campaign_object = CampaignsSignup.objects.get(email=user.email)
                            if not profile.newsletter and campaign_object.newsletter:
                                profile.newsletter = True
                                profile.is_synched = True
                                profile.save()
        
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
                          settings.CSV_EXPORT_RECIPIENTS, fail_silently=False)
                    except Exception as ex:
                        print "The following %s caused %s" % (rate_signup, ex)
        
        # Lastly, sync the campaign signups that aren't on rate signups or news signups
        if synched < 400:
            for campaign_signup in campaign_signups:
                
                if campaign_signup.email not in synched_emails:
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
                        if campaign_signup.newsletter:
                            profile.newsletter = True
                            sync_message.append("Newsletter, ")
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
                        profile.save()
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
                        if campaign_signup.newsletter:
                            profile.newsletter = True
                            sync_message.append("Newsletter, ")
                        profile.ratealerts = False
                    user.first_name = first_name
                    user.last_name = last_name
                    user.save()
                    sync_message.append("Concierge, ")
                    bitmask = self._get_subscription_bitmask(profile)
                    bitmask += 16
                    if ProductPortfolio.objects.filter(user = user).count() > 0:
                        bitmask += 8
                        sync_message.append("Rate Tracker, ")
                    elif RatetrackerReminder.objects.filter(user = user).count() > 0:
                        bitmask += 8
                        sync_message.append("Rate Tracker, ")
                    elif not new_user:
                        bitmask += 8
                    try:
                        returncode = 0
                        
                        if returncode > 0:
                            raise ResponseError(returncode)
                        
                        synched += 1
                        
                        campaign_signup.is_synched = True
                        campaign_signup.save()
                        profile.is_synched = True
                        profile.save()
                        if profile.newsletter:
                            try:
                                newsletter = NewsletterSignup.objects.get(email=campaign_signup.email)
                            except NewsletterSignup.DoesNotExist:
                                newsletter = NewsletterSignup()
                                newsletter.email = user.email
        
                            newsletter.is_synched = True
                            newsletter.save()
                        f1.write("Synced %s for %s \n" % ("".join(sync_message), user.email))
                        sync_message = []
                        synched_emails.append(user.email)
                        if synched >= 400:
                            break
                        
                    except ResponseError as e:
                        send_mail('Sync Error', 
                          "The following error occurred while syncing alerts for %s: %s" % (profile.user.email, SFResponseCodes[returncode]), 
                          settings.DEFAULT_FROM_EMAIL,
                          settings.CSV_EXPORT_RECIPIENTS, fail_silently=False)
                    except Exception as ex:
                        print "The following %s caused %s" % (campaign_signup, ex)
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
        if new_user:
            return django_client.service.newUser4('%s' % profile.user.id,
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
            )
        else:
            return django_client.service.updateUser('%s' % profile.user.id,
                profile.user.username,
                profile.user.email,
                user.first_name,
                user.last_name,
                profile.dob,
                profile.telephone,
                profile.salutation,
                profile.postcode,
                bitmask,
            )
    def _process_salesforce_concierge_sync(self, django_client, profile, user, new_user, bitmask, campaign_signup, first_name = '', last_name = ''):
        if new_user:
            return django_client.service.newUser4('%s' % profile.user.id,
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
            )
        else:
            return django_client.service.updateUser('%s' % profile.user.id,
                profile.user.username,
                profile.user.email,
                user.first_name,
                user.last_name,
                profile.dob,
                profile.telephone,
                profile.salutation,
                profile.postcode,
                bitmask,
            )

    def handle_noargs(self, **options):
        """ 
        When logging into the salesforce api we have to append our security token to the end
        """

        dte = self._get_query_date(datetime.datetime.now())

        # get all signups that havent been set to true (i.e anything thats false or null)
        newsletter_signups = NewsletterSignup.objects.exclude(is_synched=True)
        rate_signups = RateAlertsSignup.objects.exclude(is_synched=True)
        campaign_signups = CampaignsSignup.objects.exclude(is_synched=True)
        django_client = None

        self.alert_adjustment_sync(django_client, newsletter_signups, rate_signups, campaign_signups)


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
    

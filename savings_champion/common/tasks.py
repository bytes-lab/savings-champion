from datetime import datetime
import random

import hashlib
from UniversalAnalytics import Tracker
from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from mailchimp3 import MailChimp
from pysendy import Sendy, AlreadySubscribedException, HttpRequestException
from requests import HTTPError
from simple_salesforce import SalesforceAuthenticationFailed
from suds import WebFault

from common.management.commands.utils.bitmask import get_bitmask
from common.management.commands.utils.salesforce_sync import init_client
from common.models import Profile
from common.utils import ResponseError

from products.models import ProductPortfolio, RatetrackerReminder
from stats.client import StatsDClient


def update_profile_from_user(sender, instance, **kwargs):
    if Profile.objects.filter(user=instance).exists():
        profile = Profile.objects.get(user=instance)
        create_user_profile.delay(profile.pk)


@shared_task(ignore_result=True, bind=True)
def create_user_profile(self, profile_id):
    try:
        django_client = init_client()
        profile = Profile.objects.get(pk=profile_id)
        bitmask = get_bitmask(profile.user)
        newsletter_active = False
        ratealerts_active = False

        if profile.newsletter:
            newsletter_active = profile.newsletter
        if profile.ratealerts:
            ratealerts_active = profile.ratealerts

        if bitmask >= 0:
            statsd_client = StatsDClient().get_counter_client(
                client_name='salesforce.create_user_profile.attempted'
            )
            statsd_client += 1
            returncode = django_client.service.newUser5('%s' % profile.user.id,
                                                        profile.user.username,
                                                        profile.user.email,
                                                        profile.user.first_name,
                                                        profile.user.last_name,
                                                        profile.dob,
                                                        profile.telephone,
                                                        profile.salutation,
                                                        profile.postcode,
                                                        bitmask,
                                                        profile.source,
                                                        '',
                                                        '',
                                                        profile.user.is_active,
                                                        profile.user.date_joined,
                                                        ratealerts_active,
                                                        newsletter_active,
                                                        )
            if returncode > 0:
                if returncode == 1:
                    # userid already exists (due to this being a skeleton user so we run an updateuser command instead of erroring)
                    statsd_client = StatsDClient().get_counter_client(
                        client_name='salesforce.create_user_profile.attempted'
                    )
                    statsd_client += 1
                    returncode = django_client.service.updateUser3('%s' % profile.user.id,
                                                                   profile.user.username,
                                                                   profile.user.email,
                                                                   profile.user.first_name,
                                                                   profile.user.last_name,
                                                                   profile.dob,
                                                                   profile.telephone,
                                                                   profile.salutation,
                                                                   profile.postcode,
                                                                   bitmask,
                                                                   profile.user.is_active,
                                                                   profile.source,
                                                                   ratealerts_active,
                                                                   newsletter_active,
                                                                   )
                    # if this return code is still errorring then raise a response error
                    if returncode > 0:
                        raise ResponseError(returncode)
                else:
                    raise ResponseError(returncode)
            profile.is_synched = True
            profile.save()
    except (WebFault, SalesforceAuthenticationFailed) as exc:
        raise self.retry(exc=exc, countdown=int(random.uniform(2, 4) ** self.request.retries))


@shared_task(ignore_result=True, bind=True)
def delete_user_profile(self, user_id):
    try:
        User = get_user_model()

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            # Looks like we've already done our job in another thread/task.
            return
        django_client = init_client()

        # Iterate over all Variable Rate Products and "delete" them from Salesforce.
        for rate_tracker in ProductPortfolio.objects.filter(user=user_id):
            rate_tracker.is_deleted = True
            rate_tracker.save()

        # Iterate over all Fixed Rate Products and "delete" them from Salesforce.
        for rate_tracker in RatetrackerReminder.objects.filter(user=user_id):
            rate_tracker.is_deleted = True
            rate_tracker.save()

        # "Delete" this user from salesforce (User is marked deleted)
        statsd_client = StatsDClient().get_counter_client(
            client_name='salesforce.delete_user_profile.attempted'
        )
        statsd_client += 1
        return_code = django_client.service.deleteUser(user_id)
        assert return_code in [0, '0'], return_code

        # Finally delete all records of this user from Django
        user.delete()

        statsd_client = StatsDClient().get_counter_client(
            client_name='user.profile.deleted'
        )
        statsd_client -= 1
    except (WebFault, SalesforceAuthenticationFailed) as exc:
        raise self.retry(exc=exc, countdown=int(random.uniform(2, 4) ** self.request.retries))


@shared_task(ignore_result=True, bind=True)
def update_subscription_on_email_service(self, email, interest_group=u'Newsletter', subscribe=True):
    client = MailChimp(u'SavingsChampion', u'87d231607417c908e4fa24db025190f4-us3')
    interests = client.interest.all(list_id=u'3e4f769738', category_id=u'db93488550')
    for interest in interests[u'interests']:
        if interest[u'name'].lower() == interest_group.lower():
            interest_id = interest[u'id']
            break
        print (interest[u'name'].lower(), interest_group.lower())
    else:
        interest_response = client.interest.create(list_id=u'3e4f769738', category_id=u'db93488550', data={
            u'name': interest_group
        })
        interest_id = interest_response[u'id']

    try:
        client.member.create(list_id=u'3e4f769738', data={
            u"email_address": email,
            u"status": u"subscribed",
            u"merge_fields": {},
            u"interests": {u"{id}".format(id=interest_id): subscribe},
        })
    except HTTPError:
        email_hash = hashlib.md5(email.lower()).hexdigest()
        client.member.update(list_id=u'3e4f769738', member_id=email_hash, data={
            u"email_address": email,
            u"status": u"subscribed",
            u"merge_fields": {},
            u"interests": {u"{id}".format(id=interest_id): subscribe},
        })

@shared_task(ignore_result=True, bind=True)
def add_to_campaign_monitor(self, email, interest_group=u'Newsletter', subscriber_type='P'):
    try:
        # We replaced campaign monitor with Mailchimp

        try:
            profile = Profile.objects.get(user__email=email)
            full_name = profile.full_name()
        except Profile.DoesNotExist:
            full_name = ''
        except Profile.MultipleObjectsReturned:
            profile = Profile.objects.filter(user__email=email)
            profile = profile.first()
            full_name = profile.full_name()

        if sendy_list_id is not None:
            try:
                sendy.subscribe(name=full_name, email=email, list_id=settings.SENDY_ALL_USER_LIST,
                                date_created=datetime.now())
            except AlreadySubscribedException:
                pass
            try:
                sendy.subscribe(name=full_name, email=email, list_id=settings.SENDY_NEWSLETTER_ID,
                                date_created=datetime.now())
            except AlreadySubscribedException:
                pass
            if subscriber_type.upper() == 'B':
                try:
                    sendy.subscribe(name=full_name, email=email, list_id=settings.SENDY_BUSINESS_AUTO_RESPONDER,
                                    date_created=datetime.now())
                except AlreadySubscribedException:
                    pass
            elif subscriber_type.upper() == 'C':
                try:
                    sendy.subscribe(name=full_name, email=email, list_id=settings.SENDY_CHARITY_AUTO_RESPONDER,
                                    date_created=datetime.now())
                except AlreadySubscribedException:
                    pass
            else:
                try:
                    sendy.subscribe(name=full_name, email=email, list_id=settings.SENDY_PERSONAL_AUTO_RESPONDER,
                                    date_created=datetime.now())
                except AlreadySubscribedException:
                    pass
            try:
                sendy.subscribe(name=full_name, email=email, list_id=sendy_list_id, date_created=datetime.now())
            except AlreadySubscribedException:
                pass
    except HttpRequestException as exc:
        raise self.retry(exc=exc, countdown=int(random.uniform(2, 4) ** self.request.retries))


@shared_task(ignore_result=True, bind=True)
def delete_from_campaign_monitor(self, email, createsend_list_id=None, sendy_list_id=None):
    try:
        sendy_base_url = getattr(settings, 'SENDY_API_URL', 'https://sendy.savingschampion.co.uk')
        sendy = Sendy(base_url=sendy_base_url)
        sendy.unsubscribe(email=email, list_id=sendy_list_id)
    except HttpRequestException as exc:
        raise self.retry(exc=exc, countdown=int(random.uniform(2, 4) ** self.request.retries))


@shared_task(ignore_result=True)
def send_email(subject, message, from_email, recipient_list, *args, **kwargs):
    send_mail(subject, message, from_email, recipient_list, *args, **kwargs)


@shared_task(ignore_result=True)
def analytics(*args, **kwargs):
    tracker = Tracker.create(settings.GA_ACCOUNT)
    tracker.send(*args, **kwargs)

"""
Gets a list of the newest users signed up to receive Reminders from Savings Champion
"""

from django.core.management.base import NoArgsCommand

from django.conf import settings

from common.models import Profile
from common.models import RateAlertsSignup

import datetime
from createsend import *

class Command(NoArgsCommand):
    
    def _get_start_date(self, dte):
        return datetime.datetime.combine(dte.date(), datetime.time.min)
    
    def _get_end_date(self, dte):
        return datetime.datetime.combine(dte.date(), datetime.time.max)
    
    def _get_query_date(self, dte, minus_days = 1):
        return dte + datetime.timedelta(days = -minus_days)
    
    def handle_noargs(self, **options):
        """ Check if each user has a corresponding notification preference """
        
        dte = self._get_query_date(datetime.datetime.now())
        alerts = RateAlertsSignup.objects.filter(created_date__gte=self._get_start_date(dte), 
                                                 created_date__lte=self._get_end_date(dte)).order_by('-created_date')
                                        
        profiles = Profile.objects.filter(ratealerts = True, 
                                          created_date__gte=self._get_start_date(dte),
                                          created_date__lte=self._get_end_date(dte)).order_by('-created_date')
        
        
        createsend_api_key = getattr(settings, 'CREATESEND_API_KEY')
        createsend_list_id = getattr(settings, 'CREATESEND_RATE_ALERTS_LIST_ID')
        
        CreateSend.api_key = createsend_api_key

        for profile in profiles :
            subscriber = Subscriber(createsend_list_id, profile.user.email)
            email_address = subscriber.add(createsend_list_id,
                                           profile.user.email,
                                           '%s %s' % (profile.user.first_name,
                                                      profile.user.last_name),
                                           [],
                                           True)
        
        
        ratealerts_signup = RateAlertsSignup.objects.filter(created_date__gte=self._get_start_date(dte),
                                                            created_date__lte=self._get_end_date(dte)).order_by('-created_date')
        
        for signup in ratealerts_signup :
            subscriber = Subscriber(signup.email)
            email_address = subscriber.add(createsend_list_id, signup.email, '', [], True)
            signup.is_synched = True
            signup.save()
"""
Gets a csv file of all users who have signed up to RateAlerts, either through
registering or through the simple sign up and then sends result to settings
value for CSV_EXPORT_RECIPIENTS
"""

from django.core.management.base import NoArgsCommand
import csv
import os
import datetime
from django.core.mail import EmailMessage
from django.conf import settings
from common.models import RateAlertsSignup, Profile

ALERTS_CSV_PATH = getattr(settings, 'ALERTS_CSV_PATH')

ALERTS_CSV_EMAIL = getattr(settings, 'CSV_EXPORT_RECIPIENTS', ['richard-price@nameless.co.uk'])

SAVCHAMP_EMAIL_FILTERS = getattr(settings, 'SAVINGS_CHAMPION_EMAIL_FILTERS')

class Command(NoArgsCommand):
    
    def _get_start_date(self, dte):
        return datetime.datetime.combine(dte.date(), datetime.time.min)
    
    def _get_end_date(self, dte):
        return datetime.datetime.combine(dte.date(), datetime.time.max)
    
    def _get_query_date(self, dte, minus_days=1):
        return dte + datetime.timedelta(days=-minus_days)
    
    def handle_noargs(self, **options):
        """ Check if each user has a corresponding notification preference """
        dte = self._get_query_date(datetime.datetime.now())
        human_readable_format = dte.strftime('%Y/%m/%d')
        
        date_format = dte.strftime('%Y%m%d')
        alerts = RateAlertsSignup.objects.filter(created_date__gte=self._get_start_date(dte), 
                                                 created_date__lte=self._get_end_date(dte)).order_by('-created_date').exclude(email__in=SAVCHAMP_EMAIL_FILTERS)
        
        profiles = Profile.objects.filter(ratealerts=True,
                                          created_date__gte=self._get_start_date(dte),
                                          created_date__lte=self._get_end_date(dte)).order_by('-created_date')
   
        fn = os.path.join(ALERTS_CSV_PATH % date_format)
        
        f = open(fn, 'wb')                                                     
        fwr = csv.writer(f, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        fwr.writerow(['Email', 'First Name', 'Last Name', 'Created Date'])
        
        for profile in profiles :
            try :
                fwr.writerow([profile.user.email, 
                              profile.user.first_name.encode('ascii', 'ignore'),
                              profile.user.last_name.encode('ascii', 'ignore'),
                              profile.created_date
                              ])
            except Exception as ex:
                print 'Exception as %s with profile %s %s' % (ex, profile.user.email, profile.user.last_name)
            
        for alert in alerts:
            try:
                fwr.writerow([alert.email,
                              '',
                              '',
                              alert.created_date,
                              ])
            except Exception as ex:
                print 'Exception as %s ' % ex
                
        f.close()
        email = EmailMessage('Rate Alerts Emails %s' % human_readable_format, 
                             'Please find attached Rate Alerts subscriptions for %s, this includes registered users and users signed up by email only' % human_readable_format, 
                             settings.DEFAULT_FROM_EMAIL,
                             ALERTS_CSV_EMAIL,)
        
        email.attach_file(fn)
        email.send()
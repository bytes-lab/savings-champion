"""
This is deprecated and is no longer called. March 2012
All work now happens in daily_csv.py
"""

from django.core.management.base import NoArgsCommand
import os
import datetime
from django.core.mail import EmailMessage
from django.conf import settings

REMINDERS_CSV_PATH = getattr(settings, 'REMINDERS_CSV_PATH')
PORTFOLIOS_CSV_PATH = getattr(settings, 'PORTFOLIOS_CSV_PATH')

ALERTS_CSV_EMAIL = getattr(settings, 'CSV_EXPORT_RECIPIENTS', ['richard-price@nameless.co.uk'])

SAVCHAMP_EMAIL_FILTERS = getattr(settings, 'SAVINGS_CHAMPION_EMAIL_FILTERS')


class Command(NoArgsCommand):
    
    def _get_start_date(self, dte):
        dte = self._get_query_date(dte)
        return datetime.datetime.combine(dte.date(), datetime.time.min)
    
    def _get_end_date(self, dte):
        dte = self._get_query_date(dte)
        return datetime.datetime.combine(dte.date(), datetime.time.max)
    
    def _get_query_date(self, dte, minus_days=1):
        return dte + datetime.timedelta(days=-minus_days)
    
    def handle_noargs(self, **options):
        """ Check if each user has a corresponding notification preference """
        dte = self._get_query_date(datetime.datetime.now())
        
        date_format = dte.strftime('%Y%m%d')
        
        fn = os.path.join(REMINDERS_CSV_PATH % date_format)
        fn2 = os.path.join(PORTFOLIOS_CSV_PATH % date_format)
       
        human_readable_format = dte.strftime('%Y/%m/%d')
        
        email = EmailMessage('Rate Tracker subscriptions %s' % human_readable_format, 
                             'Please find attached Rate Tracker subscriptions for %s' % human_readable_format, 
                             settings.DEFAULT_FROM_EMAIL,
                             ALERTS_CSV_EMAIL,)
        
        email.attach_file(fn)
        email.attach_file(fn2)
        email.send()
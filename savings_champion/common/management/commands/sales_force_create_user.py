"""
Gets a list of all profiles that have not been set synched = True and then
syncs to SalesForce. 
SalesForce settings are initialised in init_client and driven by settings variables.
"""

from django.core.management.base import NoArgsCommand
import datetime
from django.conf import settings

SALESFORCE_CREATE_USERS_PATH = getattr(settings, 'SALESFORCE_CREATE_USERS_PATH')


class Command(NoArgsCommand):
    
    def _get_start_date(self, dte):
        dte = self._get_query_date(dte)
        return datetime.datetime.combine(dte.date(), datetime.time.min)
    
    def _get_end_date(self, dte):
        dte = self._get_query_date(dte)
        return datetime.datetime.combine(dte.date(), datetime.time.max)
    
    def _get_query_date(self, dte, minus_days=1):
        #return dte + datetime.timedelta(days=-minus_days)
        return dte - datetime.timedelta(minutes=10)
    
    
    def handle_noargs(self, **options):
        """ 
        When logging into the salesforce api we have to append our security token to the end


        Replaced with Celery Task on model save
        """
        pass

"""
Command to find all users who have not activited there accounts
"""
from django.contrib.auth import get_user_model

from django.core.management.base import NoArgsCommand
import csv
import os
import datetime
from django.core.mail import EmailMessage
from django.conf import settings
from common.models import Profile

User = get_user_model()

NON_ACTIVE_USERS_CSV_PATH = getattr(settings, 'NON_ACTIVE_USERS_CSV_PATH')
ALERTS_CSV_EMAIL = getattr(settings, 'CSV_EXPORT_RECIPIENTS', ['richard-price@nameless.co.uk'])
SAVCHAMP_EMAIL_FILTERS = getattr(settings, 'SAVINGS_CHAMPION_EMAIL_FILTERS')

class Command(NoArgsCommand):
    
    def _get_start_date(self, dte):
        return datetime.datetime.combine(dte.date(), datetime.time.max)
    
    def _get_end_date(self, dte, minus_days = 7):
        return datetime.datetime.combine(dte + datetime.timedelta(days = -minus_days), datetime.time.min)
    
    def _get_query_date(self, dte, minus_days = 1):
        return dte + datetime.timedelta(days = -minus_days)
    
    def handle_noargs(self, **options):
        dte = self._get_query_date(datetime.datetime.now())
        human_readable_format = dte.strftime('%Y/%m/%d')
        
        date_format = dte.strftime('%Y%m%d')
        
        fn = os.path.join(NON_ACTIVE_USERS_CSV_PATH % date_format)
          
        f = open(fn, 'wb')                                                     
        fwr = csv.writer(f, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        fwr.writerow(['Username', 'Email', 'First Name', 'Last Name', 'Tel. no.', 'Source', 'Date Joined'])
        
        # Get users who have not activated yet
        users = User.objects.filter(date_joined__lte=self._get_start_date(dte), 
                                    date_joined__gte=self._get_end_date(dte),
                                    is_active=False,
                                    is_superuser=False).order_by('date_joined').exclude(email__in=SAVCHAMP_EMAIL_FILTERS)
        
        counter = 0 
        for user in users:
            try:
                try:
                    profile = user.profile
                except Profile.DoesNotExist:
                    profile = Profile(user=user)
                    profile.save()
                if not profile.skeleton_user:
                    email = user.email
                    first_name = user.first_name
                    last_name = user.last_name
                    user_name = user.username
                    date_joined = user.date_joined
                    tel = profile.telephone
                    source = profile.source
                    fwr.writerow([user_name,email, first_name, last_name, tel, source, date_joined])  
                    counter += 1
                
            except Exception:
                pass
            
        f.close()

        if counter > 0:
            
            email = EmailMessage('Inactive users report w/e %s, %s users found ' % (human_readable_format,counter),
                                 'Please find attached a list of inactive users who joined last week', 
                                 settings.DEFAULT_FROM_EMAIL,
                                 ALERTS_CSV_EMAIL,)
            email.attach_file(fn)
            email.send()
        else:
            email = EmailMessage('Inactive users report w/e %s, 0 users founds ' % human_readable_format, 
                                 'There are no inactive users who joined last week', 
                                 settings.DEFAULT_FROM_EMAIL,
                                 ALERTS_CSV_EMAIL,)
            email.send()
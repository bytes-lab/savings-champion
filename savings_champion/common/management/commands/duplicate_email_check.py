from django.contrib.auth import get_user_model
from django.core.management.base import NoArgsCommand
from django.conf import settings
import csv
import os
import datetime
from django.core.mail import EmailMessage

User = get_user_model()

DUPLICATE_EMAILS_PATH = getattr(settings, 'DUPLICATE_EMAILS_PATH')
ALERTS_CSV_EMAIL = getattr(settings, 'CSV_EXPORT_RECIPIENTS')

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        today = datetime.datetime.now()
        date_format = today.strftime('%Y%m%d')
        
        userlist = User.objects.all()
        duplicate_user = []
        duplicate_email = []
        duplicate = []
        
        fn = os.path.join(DUPLICATE_EMAILS_PATH % date_format)
        f1 = open(fn, 'wb')
        fwr = csv.writer(f1, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        fwr.writerow(['Username', 'Email'])
        
        accounts = 0
        
        for user in userlist:
            user_count = User.objects.filter(email=user.email)
            if len(user_count) > 1:
                fwr.writerow([user.username, 
                          user.email])
                accounts += 1
        
        f1.close()
        
        email = EmailMessage('Duplicate Email List', 
                             'There are currently %s accounts with duplicate emails' % accounts, 
                             settings.DEFAULT_FROM_EMAIL,
                             ALERTS_CSV_EMAIL,)
        
        email.attach_file(fn)
        email.send()

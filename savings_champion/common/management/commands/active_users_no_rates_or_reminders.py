"""
Command to find all users who have activated but have not rates or reminders.
"""

import csv
import os
import datetime
from django.contrib.auth import get_user_model
from django.core.management.base import NoArgsCommand
from django.core.mail import EmailMessage
from django.conf import settings
from common.models import Profile

User = get_user_model()

NON_ACTIVE_USERS_CSV_PATH = getattr(settings, 'ACTIVE_USERS_NO_RATES_OR_REMINDERS_CSV_PATH')
ALERTS_CSV_EMAIL = getattr(settings, 'CSV_EXPORT_RECIPIENTS', ['richard-price@nameless.co.uk'])

SAVCHAMP_EMAIL_FILTERS = getattr(settings, 'SAVINGS_CHAMPION_EMAIL_FILTERS')


class Command(NoArgsCommand):
    def _get_start_date(self, dte):
        return datetime.datetime.combine(dte.date(), datetime.time.max)

    def _get_end_date(self, dte, minus_days=7):
        return datetime.datetime.combine(dte + datetime.timedelta(days=-minus_days), datetime.time.min)

    def _get_query_date(self, dte, minus_days=1):
        return dte + datetime.timedelta(days=-minus_days)

    def handle_noargs(self, **options):
        dte = self._get_query_date(datetime.datetime.now())
        human_readable_format = dte.strftime('%Y/%m/%d')

        date_format = dte.strftime('%Y%m%d')

        fn = os.path.join(NON_ACTIVE_USERS_CSV_PATH % date_format)
        f = open(fn, 'wb')
        fwr = csv.writer(f, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        fwr.writerow(['Username', 'Email', 'First Name', 'Last Name', 'Tel. no.', 'Source', 'Last Login', 'Date Joined'])

        users = User.objects.filter(date_joined__lte=self._get_start_date(dte),
                                    date_joined__gte=self._get_end_date(dte),
                                    is_active=True,
                                    is_superuser=False).order_by('date_joined').exclude(email__in=SAVCHAMP_EMAIL_FILTERS)

        counter = 0

        for user in users:
            try:
                if not user.profile.skeleton_user:
                    if not user.portfolio_products.exists() and not user.ratetrackerreminder_set.exists():
                        email = user.email
                        first_name = user.first_name
                        last_name = user.last_name
                        user_name = user.username
                        last_login = user.last_login
                        date_joined = user.date_joined
                        tel = user.profile.telephone
                        source = user.profile.source

                        fwr.writerow([user_name, email, first_name, last_name, tel, source, last_login, date_joined])

                        counter += 1

            except Exception, Profile.DoesNotExist:
                print '%s does not have a profile ' % user.first_name

                #print dir(user)

        f.close()

        if counter > 0:

            email = EmailMessage(
                'Portfolios and Trackers check w/e %s, %s users found ' % (human_readable_format, counter),
                'Please find attached a list of users who joined last week and are not tracking any products.',
                settings.DEFAULT_FROM_EMAIL,
                ALERTS_CSV_EMAIL, )
            email.attach_file(fn)
            email.send()
        else:
            email = EmailMessage('Portfolios and Trackers check w/e %s, 0 users founds ' % human_readable_format,
                                 'All users who joined last week are tracking products.',
                                 settings.DEFAULT_FROM_EMAIL,
                                 ALERTS_CSV_EMAIL, )
            email.send()
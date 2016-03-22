import random
from celery import shared_task
from simple_salesforce import SalesforceAuthenticationFailed
from suds import WebFault
from common.management.commands.utils.salesforce_sync import init_client
from common.models import Profile
from common.utils import ResponseError
from products.models import ProductPortfolio, RatetrackerReminder, Product
from stats.client import StatsDClient


@shared_task(ignore_result=True, bind=True)
def sync_ratetracker_portfolio(self, product_portfolio_id):
    try:
        django_client = init_client()
        portfolio = ProductPortfolio.objects.get(pk=product_portfolio_id)
        user = portfolio.user
        # Get users rate tracker reminders
        # Ensure user has a profile, then update the bitmask by starting that task
        try:
            profile = user.profile
        except Profile.DoesNotExist:
            profile = Profile(user=user)
            profile.is_synched = False
            profile.save()
        except Profile.MultipleObjectsReturned:
            profiles = Profile.objects.filter(user=user)
            profile = profiles[0]
        prt = django_client.factory.create('ProductPortfolio')
        prt.Balance = portfolio.balance
        prt.OpeningDate = portfolio.opening_date
        prt.Id = "pp%s" % portfolio.id
        prt.RateTrack = True
        latest_product_tier = portfolio.master_product.return_product_from_balance(portfolio.balance)
        prt.SCCode = latest_product_tier.sc_code
        prt.UserId = portfolio.user_id
        if portfolio.is_deleted:
            statsd_client = StatsDClient().get_counter_client(
                client_name='salesforce.sync_ratetracker_portfolio.attempted'
            )
            statsd_client += 1
            return_code = django_client.service.deleteRateTracker(portfolio.user_id, prt)
            if return_code == 2:
                raise ResponseError('Could not delete a product record on Salesforce, awaiting User creation')
            if return_code == 3:
                statsd_client = StatsDClient().get_counter_client(
                    client_name='salesforce.sync_ratetracker_portfolio.attempted'
                )
                statsd_client += 1
                return_code = django_client.service.newRateTracker(portfolio.user_id, prt)
                if return_code == 0:
                    statsd_client = StatsDClient().get_counter_client(
                        client_name='salesforce.sync_ratetracker_portfolio.attempted'
                    )
                    statsd_client += 1
                    return_code = django_client.service.deleteRateTracker(portfolio.user_id, prt)
                else:
                    raise ResponseError('Could not create a new product record for deletion on Salesforce')

        else:
            statsd_client = StatsDClient().get_counter_client(
                client_name='salesforce.sync_ratetracker_portfolio.attempted'
            )
            statsd_client += 1
            return_code = django_client.service.newRateTracker(portfolio.user_id, prt)
            if return_code == 2:
                raise ResponseError('Could not create a new product record on Salesforce, awaiting User creation')
            if return_code == 4:
                statsd_client = StatsDClient().get_counter_client(
                    client_name='salesforce.sync_ratetracker_portfolio.attempted'
                )
                statsd_client += 1
                return_code = django_client.service.updateRateTracker(portfolio.user_id, prt)

        if return_code == 0:
            portfolio.is_synched = True
            portfolio.save()
        else:  # Profile Doesn't Exist Yet or has been deleted.
            portfolio.is_synched = False
    #     # Process bitmask value for Salesforce
    except (WebFault, SalesforceAuthenticationFailed) as exc:
        pass
    #     raise self.retry(exc=exc, countdown=int(random.uniform(2, 4) ** self.request.retries))


@shared_task(ignore_result=True, bind=True)
def sync_ratetracker_reminder(self, product_reminder_id):
    try:
        django_client = init_client()
        reminder = RatetrackerReminder.objects.get(pk=product_reminder_id)
        prt = django_client.factory.create('ProductPortfolio')
        prt.Balance = reminder.balance
        prt.OpeningDate = reminder.maturity_date
        prt.Id = "rr%s" % reminder.id
        prt.RateTrack = True

        # XXX get a product have to find appropriate product that is published in 1970, this can almost certainly
        # be optomised if required. Also relies on their only being 1 product that matches this way.
        product_code = 'SCxxxxx'

        # Needed now because Sue requested that all Fixed Rate Bond products are now bonds.
        # So I slice a couple letters off the account type and use contains to find the special Product for this provider.

        title_length = len(reminder.account_type.title.upper())
        products = Product.objects.filter(provider=reminder.provider).filter(
            title__contains='DJANGO %s' % reminder.account_type.title[:title_length - 2].upper())

        if products.exists():
            product_code = products.first().sc_code
        prt.UserId = reminder.user_id
        prt.SCCode = product_code
        if reminder.is_deleted:
            statsd_client = StatsDClient().get_counter_client(
                client_name='salesforce.sync_ratetracker_reminder.attempted'
            )
            statsd_client += 1
            return_code = django_client.service.deleteRateTracker(reminder.user_id, prt)
            if return_code == 3:
                statsd_client = StatsDClient().get_counter_client(
                    client_name='salesforce.sync_ratetracker_reminder.attempted'
                )
                statsd_client += 1
                django_client.service.newRateTracker(reminder.user_id, prt)
                statsd_client = StatsDClient().get_counter_client(
                    client_name='salesforce.sync_ratetracker_reminder.attempted'
                )
                statsd_client += 1
                django_client.service.deleteRateTracker(reminder.user_id, prt)
        else:
            statsd_client = StatsDClient().get_counter_client(
                client_name='salesforce.sync_ratetracker_reminder.attempted'
            )
            statsd_client += 1
            return_code = django_client.service.newRateTracker(reminder.user_id, prt)
            if return_code == 4:
                statsd_client = StatsDClient().get_counter_client(
                    client_name='salesforce.sync_ratetracker_reminder.attempted'
                )
                statsd_client += 1
                django_client.service.updateRateTracker(reminder.user_id, prt)
    except (WebFault, SalesforceAuthenticationFailed) as exc:
        raise self.retry(exc=exc, countdown=int(random.uniform(2, 4) ** self.request.retries))

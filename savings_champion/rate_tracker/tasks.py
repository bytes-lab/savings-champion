from collections import defaultdict

import datetime
from celery import shared_task
from django.contrib.auth import get_user_model

from products.models import ProductPortfolio, RatetrackerReminder, Provider
from rate_tracker.business_logic import has_account_moved_to_another, has_account_rate_changed, is_account_bonus_ending, \
    has_account_gone_over_fscs_limits_for_provider, has_account_gone_outside_balance_limits, \
    is_fixed_rate_account_maturing, produce_client_alert_from_problems


def check_client_portfolios_for_issues():
    """
    Runs through all of the accounts that are marked as active and queues up checks on their accounts for issues

    :rtype: None
    """

    User = get_user_model()
    users = User.objects.filter(is_active=True)

    for user in users:
        check_client_portfolio_for_issues.delay(user.pk)

@shared_task
def check_client_portfolio_for_issues(user_id):

    """
    Checks the supplied user id's accounts for any issues
    :param user: the primary key ID for the user to be checked
    :return: None
    """

    def _add_to_nested_dict(client_issues, portfolio_product, key, value):

        if hasattr(portfolio_product, 'master_product'):
            # Product is a ProductPortfolio instance
            if portfolio_product.master_product.title not in client_issues:
                client_issues[u'{provider} - {product}'.format(provider=portfolio_product.master_product.provider.title,
                                                     product=portfolio_product.master_product.title)] = {}
            client_issues[u'{provider} - {product}'.format(provider=portfolio_product.master_product.provider.title,
                                                 product=portfolio_product.master_product.title)][key] = value
        elif hasattr(portfolio_product, 'maturity_date'):
            # Product is a RatetrackerReminder instance
            if u'{provider} - Fixed Rate Bond'.format(provider=portfolio_product.provider) not in client_issues:
                client_issues[
                    u'{provider} - Fixed Rate Bond'.format(provider=portfolio_product.provider)] = {}
            client_issues[
                u'{provider} - Fixed Rate Bond'.format(provider=portfolio_product.provider)][key] = value
        else:
            raise ValueError("portfolio_product didn't match duck typing")

        return client_issues

    User = get_user_model()
    user = User.objects.get(pk=user_id)

    client_issues = defaultdict(dict)
    provider_balances = defaultdict(int)
    provider_issues = {}

    for number, portfolio_product in enumerate(ProductPortfolio.objects.filter(user=user, is_deleted=False).prefetch_related('master_product', 'master_product__provider')):

        provider_balances[portfolio_product.master_product.provider_id] += portfolio_product.balance

        moved, new_account = has_account_moved_to_another(portfolio_product)
        if moved:
            client_issues = _add_to_nested_dict(client_issues, portfolio_product, u'moved_account', new_account)

        rate_changed, old_rate, new_rate = has_account_rate_changed(portfolio_product)
        if rate_changed:
            client_issues = _add_to_nested_dict(client_issues, portfolio_product, u'rate_changed', (old_rate, new_rate))

        bonus_ended, old_rate, new_rate = is_account_bonus_ending(portfolio_product)
        if bonus_ended:
            client_issues = _add_to_nested_dict(client_issues, portfolio_product, u'bonus_ended', (old_rate, new_rate))

        over_fscs = has_account_gone_over_fscs_limits_for_provider(portfolio_product)
        if over_fscs:
            client_issues = _add_to_nested_dict(client_issues, portfolio_product, u'over_fscs_limit', True)

        outside_balance = has_account_gone_outside_balance_limits(portfolio_product)
        if outside_balance:
            client_issues = _add_to_nested_dict(client_issues, portfolio_product, u'outside_balance_limit', True)

    for number, ratetracker_reminder in enumerate(RatetrackerReminder.objects.filter(user=user, is_deleted=False).iterator()):

        provider_balances[ratetracker_reminder.provider_id] += ratetracker_reminder.balance

        maturing, maturity_date = is_fixed_rate_account_maturing(ratetracker_reminder)
        if maturing:
            client_issues = _add_to_nested_dict(client_issues, ratetracker_reminder, u'maturing', maturity_date)

    provider_balances = dict(provider_balances)

    for provider, balance in provider_balances.items():
        provider = Provider.objects.get(pk=provider)
        if balance > provider.fscs_limit_type.balance_limit and not provider.fscs_limit_type.balance_unlimited:
            provider_issues[provider.title] = (balance, provider.fscs_limit_type.balance_limit)

    if len(client_issues) > 0 or len(provider_issues) > 0:
        produce_client_alert_from_problems(user.pk, client_issues, provider_issues)


@shared_task
def update_portfolio_alert_dates(user_id):
    ProductPortfolio.objects.filter(user_id=user_id).update(last_alerted=datetime.date.today())

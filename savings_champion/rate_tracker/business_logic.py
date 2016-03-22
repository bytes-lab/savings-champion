# coding=utf-8
import datetime
from collections import namedtuple

from django.template import Context
from django.template.loader import get_template

from products.models import ProductTier, ProductPortfolio
from rate_tracker.models import RatetrackerAlert

__author__ = 'josh'


def has_account_moved_to_another(portfolio_product):
    """
    Check if account has moved to new product
    :rtype: bool
    :param portfolio_product:
    """
    if portfolio_product.master_product.moved_to is not None:
        # todo: Check if the moved_to product is active yet
        if portfolio_product.master_product.revert_on_bonus_end and portfolio_product.master_product.status == 'Closed':
            if portfolio_product.master_product.available_to + datetime.timedelta(
                    weeks=(4 * portfolio_product.master_product.bonus_term)) < datetime.date.today():

                portfolio_product.master_product = portfolio_product.master_product.moved_to
                portfolio_product.save()
                return True, portfolio_product.master_product.moved_to

            if portfolio_product.master_product.bonus_end_date < datetime.date.today():

                portfolio_product.master_product = portfolio_product.master_product.moved_to
                portfolio_product.save()
                return True, portfolio_product.master_product.moved_to

        if portfolio_product.master_product.revert_on_maturity:
            if datetime.date.today() + datetime.timedelta(
                    weeks=(4 * portfolio_product.master_product.term)) < portfolio_product.master_product.maturity_date:

                portfolio_product.master_product = portfolio_product.master_product.moved_to
                portfolio_product.save()
                return True, portfolio_product.master_product.moved_to

        if portfolio_product.master_product.status == 'Historic':
            portfolio_product.master_product = portfolio_product.master_product.moved_to
            portfolio_product.save()
            return True, portfolio_product.master_product.moved_to
        # todo: Move client record to new product
        return True, portfolio_product.master_product.moved_to
    return False, None


def is_account_bonus_ending(portfolio_product, lead_time=14):
    """
    Check if account has a bonus ending in <lead_time> days
    :rtype: bool
    :param portfolio_product: The ProductPortfolio that triggered the check
    :param lead_time: The time in days before the bonus ends to alert client to make a change
    """
    try:
        latest_account = portfolio_product.master_product.get_latest_product_tier(portfolio_product.balance)
    except ProductTier.DoesNotExist:
        # This will be picked up later, so don't alert for this right now as we have no way of knowing what the rates are..
        FakeProductTier = namedtuple('FakeProductTier', 'gross_rate underlying_gross_rate')
        latest_account = FakeProductTier(gross_rate=None,
                                         underlying_gross_rate=None)

    # Check for a fixed bonus end date
    if portfolio_product.master_product.bonus_end_date:
        # Check to see if fixed bonus end date is happening within the lead time
        lead_date = portfolio_product.master_product.bonus_end_date - datetime.timedelta(days=lead_time)
        # If today is (after) the alert date, bonus has ended.
        if datetime.date.today() >= lead_date:
            return True, latest_account.gross_rate, latest_account.underlying_gross_rate

    # Check for a bonus term
    if portfolio_product.master_product.bonus_term:
        if portfolio_product.opening_date:
            if (portfolio_product.opening_date + datetime.timedelta(
                    weeks=(4 * portfolio_product.master_product.bonus_term)) - datetime.timedelta(days=lead_time)) <= datetime.date.today():
                return True, latest_account.gross_rate, latest_account.underlying_gross_rate
        else:
            return True, latest_account.gross_rate, latest_account.underlying_gross_rate

    return False, latest_account.gross_rate, latest_account.underlying_gross_rate


def has_account_rate_changed(portfolio_product):
    """
    Check if variable rate account rate has changed rate
    :rtype: bool
    :param portfolio_product: The ProductPortfolio that triggered the check
    :type portfolio_product: ProductPortfolio
    """
    account_current_rate = portfolio_product.get_latest_rate
    starting_rate = portfolio_product.master_product.get_latest_rate_for_date(portfolio_product.balance, portfolio_product.opening_date, date=portfolio_product.last_alerted)

    if starting_rate < account_current_rate:
        return True, starting_rate, account_current_rate
    elif account_current_rate < starting_rate:
        return True, starting_rate, account_current_rate
    return False, starting_rate, account_current_rate


def is_fixed_rate_account_maturing(portfolio_product, lead_time=14):
    """
    Check if fixed rate account is maturing
    :rtype: bool
    :param portfolio_product:
    :param lead_time: The time in days before the bonus ends to alert client to make a change
    """

    if portfolio_product.maturity_date - datetime.timedelta(days=lead_time) <= datetime.date.today():
        return True, portfolio_product.maturity_date
    return False, portfolio_product.maturity_date


def has_account_gone_over_fscs_limits_for_provider(portfolio_product):
    """
    Check if this account in isolation is over the FSCS limits for this provider
    :rtype: bool
    :param portfolio_product:
    """
    if portfolio_product.master_product.provider.fscs_limit_type.balance_unlimited:
        return False

    if portfolio_product.balance > portfolio_product.master_product.provider.fscs_limit_type.balance_limit:
        return True
    return False


def has_account_gone_outside_balance_limits(portfolio_product):
    """
    Check if account is outside the balance limits set by the provider

    :rtype: bool
    :param portfolio_product:
    """
    try:
        portfolio_product.master_product.get_latest_product_tier(portfolio_product.balance)
    except ProductTier.DoesNotExist:
        return True
    return False


def produce_client_alert_from_problems(client, problem_products, problem_providers):
    ratetracker_alert, _ = RatetrackerAlert.objects.get_or_create(user_id=client, authorised=False)
    template = get_template(u'ratetracker_issues_email.html')
    rendered_template = template.render(Context({u'problem_products': dict(problem_products),
                                                 u'problem_providers': problem_providers,
                                                 u'ratetracker_alert': ratetracker_alert}))
    ratetracker_alert.alert_email = rendered_template
    ratetracker_alert.save()

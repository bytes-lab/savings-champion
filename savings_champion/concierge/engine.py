# coding=utf-8
from collections import defaultdict
from copy import deepcopy
from decimal import Decimal
from datetime import datetime, timedelta, date
from django.contrib.auth import get_user_model
from django.db.models import Q, F, Sum
from concierge.models import ConciergeUserPool, ConciergeUserOption, ConciergeUserProviderRisk, \
    ConciergeUserRequiredProduct, ConciergeUserRemovedProduct, ConciergeUserLicenceRisk, \
    ConciergeProviderAccountTypeLimitation, ConciergeUserAcceptedProduct
from products.models import ProductPortfolio, ProductTier, MasterProduct, RatetrackerReminder
from sortedcontainers import SortedSet

class TermColor(object):
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


class TermColorFake(object):
    HEADER = ''  # \033[95m'
    OKBLUE = ''  # \033[94m'
    OKGREEN = ''  # \033[92m'
    WARNING = ''  # \033[93m'
    FAIL = ''  # \033[91m'
    ENDC = ''  # \033[0m'


term_color = TermColorFake()


def user_portfolio_interest(portfolio, ratetracker_reminders=None):
    interest = Decimal(0)
    total_balance = Decimal(0)
    for account in portfolio:
        interest += (account.balance * (1 + (account.get_latest_rate / 100)))
        total_balance += account.balance
    for reminder in ratetracker_reminders:
        interest += (reminder.balance * (1 + (reminder.rate / 100)))
        total_balance += reminder.balance

    return interest - total_balance, total_balance


def compare_existing_portfolio_to_generated(email, required_accounts=None, removed_accounts=None, best_case=False):
    User = get_user_model()
    user = User.objects.get(email=email)
    engine = Engine(email,
                    best_case=best_case)
    generated_portfolio, engine_log, naughty_list, total_amount, total_interest, fscs_conflicts = engine.improve_portfolio()
    portfolio_products = ProductPortfolio.objects.filter(user=user,
                                                         is_deleted=False)
    expected_amount = ConciergeUserPool.objects.filter(user=user).aggregate(expected_amount=Sum('balance'))
    ratetracker_reminders = RatetrackerReminder.objects.filter(user=user,
                                                               is_deleted=False)
    existing_interest, existing_amount = user_portfolio_interest(portfolio_products, ratetracker_reminders)

    return {'generated_portfolio': generated_portfolio,
            'engine_log': engine_log,
            'naughty_list': naughty_list,
            'total_amount': total_amount,
            'expected_amount': expected_amount['expected_amount'],
            'existing_amount': existing_amount,
            'existing_interest': existing_interest,
            'generated_interest': total_interest,
            'interest_change': total_interest - existing_interest,
            'generated_portfolio_length': engine.generated_portfolio_length(),
            'account_count_change': engine.generated_portfolio_length() - portfolio_products.count()}


def fscs_optimized_portfolio(email, required_products=None, depth=1, previous_interest=None):
    # Run the engine
    # Find portfolio FSCS conflicts
    # Work out combinations
    # Run each combination for depth deep
    # continue if portfolio improved, stop if not
    # return only largest improvement
    engine = Engine(email)
    generated_portfolio, engine_log, naughty_list, total_amount, total_interest, fscs_conflicts = engine.improve_portfolio(required_products=required_products)

    if previous_interest is not None:
        if previous_interest > total_interest:
            return 0

    if depth > 0:
        depth -= depth
        length = len(fscs_conflicts)
        for count, fscs_conflict in enumerate(fscs_conflicts, start=1):
            print "%s: %s of %s" % (depth, count, length)
            portfolio, engine_log, naughty_list, total_amount, returned_interest, fscs_conflicts = fscs_optimized_portfolio(email, [fscs_conflict], depth, total_interest)
            if returned_interest > total_interest:
                total_interest = returned_interest
                generated_portfolio = portfolio
                print total_interest
                print fscs_conflict

    return generated_portfolio, engine_log, naughty_list, total_amount, total_interest, fscs_conflicts


class Engine:

    def __init__(self, email, best_case=False):
        self.pool_balance = defaultdict(Decimal)
        # PEP8 Exception: function returns the User model class, hence capitalisation.
        # noinspection PyPep8Naming
        User = get_user_model()
        # end of PEP8 Exception #
        self.provider_limitations = {}
        self.provider_usage = defaultdict(Decimal)
        self.required_accounts = []
        self.removed_accounts = []
        self.engine_log = []
        self.used_master_products = defaultdict(lambda: defaultdict(int))
        self.assigned_products = {}
        self.naughty_list = defaultdict(SortedSet)
        self.total_amount = Decimal()
        self.total_interest = Decimal()
        self.fscs_usage = defaultdict(Decimal)
        self.fscs_conflicts = []
        self.user = User.objects.get(email=email)
        self.user_concierge_options, _ = ConciergeUserOption.objects.get_or_create(user=self.user)
        self.pools = ConciergeUserPool.objects.filter(user=self.user).order_by('-term', '-balance')
        self.product_portfolios = None
        self.best_case = best_case

    def improve_portfolio(self, required_products=None, removed_products=None):
        self.provider_usage = defaultdict(Decimal)
        self.required_accounts = ConciergeUserRequiredProduct.objects.filter(
            concierge_user__user=self.user).values_list(
            'master_product_id', 'balance')
        self.removed_accounts = ConciergeUserRemovedProduct.objects.filter(concierge_user__user=self.user).values_list(
            'master_product_id', flat=True)
        if required_products is not None:
            self.required_accounts.extend(required_products)
        if removed_products is not None:
            self.removed_accounts.extend(removed_products)

        self.engine_log = []
        self.used_master_products = defaultdict(lambda: defaultdict(int))
        self.assigned_products = {}
        self.naughty_list = defaultdict(SortedSet)
        self.total_amount = Decimal()
        self.total_interest = Decimal()
        self.fscs_usage = defaultdict(Decimal)
        self.fscs_conflicts = []
        self.user_concierge_options, _ = ConciergeUserOption.objects.get_or_create(user=self.user)
        self.pools = ConciergeUserPool.objects.filter(user=self.user).order_by('-term', '-balance')
        self.product_portfolios = ProductPortfolio.objects.filter(user=self.user).select_related('product')
        self.provider_limitations = {}
        self.pool_balance = defaultdict(Decimal)

        if self.user_concierge_options.use_existing_accounts or self.best_case:
            self._use_existing_accounts()
            master_products_pks = self.product_portfolios.values_list('master_product', flat=True).distinct()
        else:
            master_products_pks = []

        # self.calculate_isa_savings(master_products_pks)
        self.calculate_regular_savings(master_products_pks)

        return self.assigned_products, self.engine_log, dict(
            self.naughty_list), self.total_amount, self.generated_portfolio_interest(), self.fscs_conflicts

    def calculate_isa_savings(self, master_products_pks):
        viable_products = ProductTier.objects.filter(Q(available_until=None,
                                                       product__status='Live') | Q(
            product__in=master_products_pks)).filter(
            product__bestbuy_type__title__in=['Variable Rate ISAs', 'Fixed Rate ISAs']).exclude(
            product__title__istartswith='DJANGO').exclude(
            tier_type='Operating Tier')
        if not self.user_concierge_options.child:
            viable_products = viable_products.exclude(
                product__bestbuy_type__title__in=['Junior ISA'])
        if not self.user_concierge_options.business:
            viable_products = viable_products.exclude(product__account_type='B')
        else:
            viable_products = viable_products.exclude(product__account_type='P')
        if not self.user_concierge_options.charity:
            viable_products = viable_products.exclude(product__account_type='C')
        else:
            viable_products = viable_products.exclude(product__account_type='P')
        if self.removed_accounts is not None and not self.best_case:
            removed_products = MasterProduct.objects.filter(pk__in=self.removed_accounts)
            viable_products = viable_products.exclude(product__in=removed_products)
        if not self.user_concierge_options.existing_customer and not self.best_case:
            viable_products = viable_products.exclude(existing_only=True)
        if not self.user_concierge_options.local_customer and not self.best_case:
            viable_products = viable_products.exclude(locals_only=True)
        if self.user_concierge_options.monthly_interest and not self.best_case:
            viable_products = viable_products.filter(
                product__interest_paid_frequency__title__icontains='monthly').exclude(
                monthly_gross=None).order_by('-monthly_gross', '-maximum').select_related('product')

        else:
            viable_products = viable_products.select_related('product')
        adjusted_pools = {}
        if self.required_accounts is not None:
            adjusted_pools = self.handle_required_accounts()
        for pool in self.pools:
            status_line = u"{0:s}Pool Term: {1}{2:s}".format(term_color.OKBLUE, pool.term, term_color.ENDC)
            self.engine_log.append(status_line)
            # print status_line
            # Month is ~31 days and notice is stored in days
            pool_viable_products = viable_products.filter(product__term__lte=pool.term,
                                                          product__notice__lte=(pool.term * 31)).order_by('-gross_rate',
                                                                                                          '-maximum')

            if pool.term not in self.assigned_products:
                self.assigned_products[pool.term] = []
            # if pool.term in adjusted_pools:
            #    self.pool_balance[pool.term] = adjusted_pools[pool.term]
            #    self.total_amount += self.pool_balance[pool.term]

            for product_tier in pool_viable_products:
                if self.pool_balance[pool.term] == pool.balance:
                    status_line = u"{0}Pool Filled{1}".format(term_color.OKBLUE, term_color.ENDC)
                    self.engine_log.append(status_line)
                    break
                else:
                    status_line = u"{0}Pool has £{1} remaining{2}".format(term_color.OKBLUE,
                                                                         pool.balance - self.pool_balance[pool.term],
                                                                         term_color.ENDC)
                    self.engine_log.append(status_line)

                if self.user_concierge_options.dual_portfolio and not product_tier.product.open_limit_total == -1 and not \
                                self.used_master_products[product_tier.product.pk]['total'] < (
                                    product_tier.product.open_limit_total + product_tier.product.open_limit_own_name):
                    status_line = u"%sCan't be opened due to a product limit of %s accounts%s, inc second person" % (
                        term_color.FAIL,
                        product_tier.product.open_limit_total,
                        term_color.ENDC)
                    self.engine_log.append(status_line)
                    continue
                elif not product_tier.product.open_limit_total == -1 and not \
                                self.used_master_products[product_tier.product.pk][
                                    'total'] < product_tier.product.open_limit_total:
                    status_line = u"%sCan't be opened due to a product limit of %s accounts%s" % (term_color.FAIL,
                                                                                                  product_tier.product.open_limit_total,
                                                                                                  term_color.ENDC)
                    self.engine_log.append(status_line)
                    continue

                while True:

                    verdict, account_balance, restrictions, status_lines, empty, joint = self.account_filtering_logic(
                        product_tier)

                    status_line = u"{0:s}Verdict for {1:s} was {2}{3:s}".format(term_color.OKBLUE, product_tier.product.title, verdict,
                                                                               term_color.ENDC)
                    self.engine_log.append(status_line)

                    if verdict:
                        added, pool_term, account_balance, reason = self.add_product_to_most_appropriate_pool(
                            account_balance,
                            product_tier)
                        if not added:
                            status_line = u"%sProduct was not able to be added due to; '%s' - %s %s £%s @ %s%s" % (
                                term_color.WARNING, reason, product_tier.provider.title, product_tier.product.title,
                                account_balance, product_tier.gross_rate, term_color.ENDC)
                            self.engine_log.append(status_line)
                            break

                        self.used_master_products[product_tier.product.pk]['total'] += 1
                        if joint:
                            self.used_master_products[product_tier.product.pk]['joint'] += 1
                        else:
                            self.used_master_products[product_tier.product.pk]['own_name'] += 1
                        self.provider_usage[product_tier.provider] += account_balance

                        if self.user_concierge_options.monthly_interest:
                            status_line = u"%sADD %s %s £%s @ %s%s" % (
                                term_color.OKGREEN, product_tier.provider.title, product_tier.product.title,
                                account_balance, product_tier.monthly_gross, term_color.ENDC)
                        else:
                            status_line = u"%sADD %s %s £%s @ %s%s" % (
                                term_color.OKGREEN, product_tier.provider.title, product_tier.product.title,
                                account_balance, product_tier.gross_rate, term_color.ENDC)

                        self.engine_log.append(status_line)
                        self.total_amount += account_balance
                        self.total_interest += account_balance * (product_tier.gross_rate / 100)
                    elif not empty:
                        self._add_to_naughty_list(account_balance, pool, product_tier, status_lines, restrictions)
                        break
                    else:
                        break
            else:
                status_line = u"%sWARNING Still Have %s to allocate, but no accounts left are valid! looking to fill " \
                              u"residual accounts%s" % (term_color.WARNING, pool.balance - self.pool_balance[pool.term],
                                                        term_color.ENDC)

                self.engine_log.append(status_line)
                # print status_line

    def calculate_regular_savings(self, master_products_pks):
        viable_products = ProductTier.objects.filter(Q(available_until=None,
                                                       product__status='Live') | Q(
            product__in=master_products_pks)).exclude(
            product__bestbuy_type__title__in=['Regular Savings',
                                              'Variable Rate Bond',
                                              'Variable Rate ISAs',
                                              'Fixed Rate ISAs',
                                              'Junior ISA']).exclude(
            product__title__istartswith='DJANGO').exclude(
            tier_type='Operating Tier')
        if not self.user_concierge_options.child:
            viable_products = viable_products.exclude(
                product__bestbuy_type__title__in=['Children\'s Accounts'])
        if not self.user_concierge_options.current_accounts and not self.best_case:
            viable_products = viable_products.exclude(
                product__bestbuy_type__title__in=['High Interest Current Accounts', 'Current Accounts'])
        if not self.user_concierge_options.business:
            viable_products = viable_products.exclude(product__account_type='B')
        else:
            viable_products = viable_products.exclude(product__account_type='P')
        if not self.user_concierge_options.charity:
            viable_products = viable_products.exclude(product__account_type='C')
        else:
            viable_products = viable_products.exclude(product__account_type='P')
        if self.removed_accounts is not None and not self.best_case:
            removed_products = MasterProduct.objects.filter(pk__in=self.removed_accounts)
            viable_products = viable_products.exclude(product__in=removed_products)
        if not self.user_concierge_options.existing_customer and not self.best_case:
            viable_products = viable_products.exclude(existing_only=True)
        if not self.user_concierge_options.local_customer and not self.best_case:
            viable_products = viable_products.exclude(locals_only=True)
        if self.user_concierge_options.monthly_interest and not self.best_case:
            viable_products = viable_products.filter(
                product__interest_paid_frequency__title__icontains='monthly').exclude(
                monthly_gross=None).order_by('-monthly_gross', '-maximum').select_related('product')

        else:
            viable_products = viable_products.select_related('product')
        adjusted_pools = {}
        if self.required_accounts is not None:
            adjusted_pools = self.handle_required_accounts()
        for pool in self.pools:
            status_line = u"{0:s}Pool Term: {1}{2:s}".format(term_color.OKBLUE, pool.term, term_color.ENDC)
            self.engine_log.append(status_line)
            # print status_line
            # Month is ~31 days and notice is stored in days
            pool_viable_products = viable_products.filter(product__term__lte=pool.term,
                                                          product__notice__lte=(pool.term * 31)).order_by('-gross_rate',
                                                                                                          '-maximum')

            if pool.term not in self.assigned_products:
                self.assigned_products[pool.term] = []
            # if pool.term in adjusted_pools:
            #    self.pool_balance[pool.term] = adjusted_pools[pool.term]
            #    self.total_amount += self.pool_balance[pool.term]

            for product_tier in pool_viable_products:
                if self.pool_balance[pool.term] == pool.balance:
                    status_line = u"{0}Pool Filled{1}".format(term_color.OKBLUE, term_color.ENDC)
                    self.engine_log.append(status_line)
                    break
                else:
                    status_line = u"{0}Pool has £{1} remaining{2}".format(term_color.OKBLUE,
                                                                         pool.balance - self.pool_balance[pool.term],
                                                                         term_color.ENDC)
                    self.engine_log.append(status_line)

                if self.user_concierge_options.dual_portfolio and not product_tier.product.open_limit_total == -1 and not \
                                self.used_master_products[product_tier.product.pk]['total'] < (
                                    product_tier.product.open_limit_total + product_tier.product.open_limit_own_name):
                    status_line = u"%sCan't be opened due to a product limit of %s accounts%s, inc second person" % (
                        term_color.FAIL,
                        product_tier.product.open_limit_total,
                        term_color.ENDC)
                    self.engine_log.append(status_line)
                    continue
                elif not product_tier.product.open_limit_total == -1 and not \
                                self.used_master_products[product_tier.product.pk][
                                    'total'] < product_tier.product.open_limit_total:
                    status_line = u"%sCan't be opened due to a product limit of %s accounts%s" % (term_color.FAIL,
                                                                                                  product_tier.product.open_limit_total,
                                                                                                  term_color.ENDC)
                    self.engine_log.append(status_line)
                    continue

                while True:

                    verdict, account_balance, restrictions, status_lines, empty, joint = self.account_filtering_logic(
                        product_tier)

                    status_line = u"{0:s}Verdict for {1:s} was {2}{3:s}".format(term_color.OKBLUE, product_tier.product.title, verdict,
                                                                               term_color.ENDC)
                    self.engine_log.append(status_line)

                    if verdict:
                        added, pool_term, account_balance, reason = self.add_product_to_most_appropriate_pool(
                            account_balance,
                            product_tier)
                        if not added:
                            status_line = u"%sProduct was not able to be added due to; '%s' - %s %s £%s @ %s%s" % (
                                term_color.WARNING, reason, product_tier.provider.title, product_tier.product.title,
                                account_balance, product_tier.gross_rate, term_color.ENDC)
                            self.engine_log.append(status_line)
                            break

                        self.used_master_products[product_tier.product.pk]['total'] += 1
                        if joint:
                            self.used_master_products[product_tier.product.pk]['joint'] += 1
                        else:
                            self.used_master_products[product_tier.product.pk]['own_name'] += 1
                        self.provider_usage[product_tier.provider] += account_balance

                        if self.user_concierge_options.monthly_interest:
                            status_line = u"%sADD %s %s £%s @ %s%s" % (
                                term_color.OKGREEN, product_tier.provider.title, product_tier.product.title,
                                account_balance, product_tier.monthly_gross, term_color.ENDC)
                        else:
                            status_line = u"%sADD %s %s £%s @ %s%s" % (
                                term_color.OKGREEN, product_tier.provider.title, product_tier.product.title,
                                account_balance, product_tier.gross_rate, term_color.ENDC)

                        self.engine_log.append(status_line)
                        self.total_amount += account_balance
                        self.total_interest += account_balance * (product_tier.gross_rate / 100)
                    elif not empty:
                        self._add_to_naughty_list(account_balance, pool, product_tier, status_lines, restrictions)
                        break
                    else:
                        break
            else:
                status_line = u"%sWARNING Still Have %s to allocate, but no accounts left are valid! looking to fill " \
                              u"residual accounts%s" % (term_color.WARNING, pool.balance - self.pool_balance[pool.term],
                                                        term_color.ENDC)

                self.engine_log.append(status_line)
                # print status_line

    def generated_portfolio_length(self, portfolio=None):
        length = 0
        if portfolio is None:
            portfolio = self.assigned_products

        for pool, accounts in portfolio.iteritems():
            length += len(accounts)
        return length

    def check_fscs(self, product_tier, balance):
        """
        Accepts a ProductTier object and a balance.
        Checks that balance doesn't go over product maximum, user defined limits and FSCS protection limits.
        If user defined limit is higher than protection limit then the user defined limit is in priority.

        :param product_tier: A django ProductTier object
        :type product_tier: ProductTier
        :param balance: The desired balance that the system wants to put into the account
        :type balance: Decimal
        :return: The allowed balance and if the balance conflicted with FSCS
        :rtype: tuple
        """
        fscs_holder = product_tier.provider.fscs_licence_holder
        fscs_conflicted = False
        joint = False
        if not product_tier.provider.fscs_limit_type.balance_unlimited:

            projected_fscs_usage = (balance + self.fscs_usage[fscs_holder])
            if ConciergeUserProviderRisk.objects.filter(user=self.user, provider=product_tier.provider).exists():
                # User has custom provider risk settings
                provider_risk = ConciergeUserProviderRisk.objects.get(user=self.user, provider=product_tier.provider)
                if projected_fscs_usage > provider_risk.maximum_balance:
                    provider_risk_balance = provider_risk.maximum_balance - self.fscs_usage[fscs_holder]
                    if provider_risk_balance < product_tier.maximum:
                        provider_risk_balance = provider_risk_balance
                    else:
                        provider_risk_balance = product_tier.maximum
                    if provider_risk_balance < provider_risk.maximum_balance:
                        fscs_conflicted = True
                    return provider_risk_balance, fscs_conflicted, joint

            if projected_fscs_usage > product_tier.provider.fscs_limit_type.balance_limit:
                # This balance is over fscs protection
                if projected_fscs_usage > self.user_concierge_options.maximum_opening_balance:

                    if self.user_concierge_options.joint_name:
                        balance, fscs_conflicted, joint = self.joint_fscs(product_tier, balance)
                    else:
                        balance, fscs_conflicted, joint = self.solo_fscs(product_tier, balance)

        return balance, fscs_conflicted, joint

    def solo_fscs(self, product_tier, balance, dual_portfolio=False):
        fscs_holder = product_tier.provider.fscs_licence_holder
        fscs_conflicted = False

        # FSCS Limits
        if dual_portfolio:
            # We have two peoples FSCS in solo products
            protection_limit_balance = (product_tier.provider.fscs_limit_type.balance_limit *
                                        product_tier.provider.fscs_limit_type.multiplier_if_joint) - self.fscs_usage[
                                           fscs_holder]
        else:
            protection_limit_balance = product_tier.provider.fscs_limit_type.balance_limit - self.fscs_usage[
                fscs_holder]

        if protection_limit_balance > balance:
            # New protection limit might be over cash we have left, don't go overboard.
            protection_limit_balance = balance

        if protection_limit_balance > product_tier.maximum:
            # Ensure we're not accidentally over the product maximum!
            protection_limit_balance = product_tier.maximum

        # User Limits

        if dual_portfolio:
            user_limit_balance = (self.user_concierge_options.maximum_opening_balance *
                                  product_tier.provider.fscs_limit_type.multiplier_if_joint) - self.fscs_usage[
                                     fscs_holder]
        else:
            user_limit_balance = self.user_concierge_options.maximum_opening_balance - self.fscs_usage[fscs_holder]

        if user_limit_balance > balance:
            user_limit_balance = balance

        if user_limit_balance > product_tier.maximum:
            # Ensure we're not accidentally over the product maximum!
            user_limit_balance = product_tier.maximum

        # Protection Limit Decider
        if user_limit_balance > protection_limit_balance:
            # Pick whichever is the largest figure, use that. We want to fill all accounts as best we can.
            new_balance = user_limit_balance
        else:
            new_balance = protection_limit_balance

        if dual_portfolio:
            # Now ensure no more than one persons FSCS is in one product
            protection_limit_balance = product_tier.provider.fscs_limit_type.balance_limit
            user_limit_balance = self.user_concierge_options.maximum_opening_balance
            if user_limit_balance > protection_limit_balance:
                # Pick whichever is the largest figure, use that. We want to fill all accounts as best we can.
                new_balance = user_limit_balance if new_balance > user_limit_balance else new_balance
            else:
                new_balance = protection_limit_balance if new_balance > protection_limit_balance else new_balance

        if new_balance < self.user_concierge_options.maximum_opening_balance < product_tier.maximum:
            # If the balance is less than the user allows, there must be FSCS conflicts somewhere.
            fscs_conflicted = True

        elif new_balance < product_tier.provider.fscs_limit_type.balance_limit - self.fscs_usage[
            fscs_holder] < product_tier.maximum:
            # If the balance is less that we could have on an account, there must be FSCS conflicts somewhere.
            fscs_conflicted = True

        return new_balance, fscs_conflicted, False

    def joint_fscs(self, product_tier, balance):
        fscs_holder = product_tier.provider.fscs_licence_holder
        fscs_conflicted = False
        if not self.used_master_products[product_tier.product.pk]['joint'] < product_tier.product.open_limit_joint_name:
            if not product_tier.product.open_limit_joint_name == -1:
                balance, fscs_conflicted, joint = self.solo_fscs(product_tier, balance)
                return balance, fscs_conflicted, joint

        if product_tier.maximum < product_tier.provider.fscs_limit_type.balance_limit * product_tier.provider.fscs_limit_type.multiplier_if_joint:
            # If product maximum balance is less than Protection maximum, open as single accounts if possible
            balance, fscs_conflicted, joint = self.solo_fscs(product_tier, balance, dual_portfolio=True)
            return balance, fscs_conflicted, joint

        # FSCS Limits
        protection_limit_balance = (
                                       product_tier.provider.fscs_limit_type.balance_limit * product_tier.provider.fscs_limit_type.multiplier_if_joint) - \
                                   self.fscs_usage[fscs_holder]

        if protection_limit_balance > balance:
            # New protection limit might be over cash we have left, don't go overboard.
            protection_limit_balance = balance

        if protection_limit_balance > product_tier.maximum:
            # Ensure we're not accidentally over the product maximum!
            protection_limit_balance = product_tier.maximum

        # User Limits
        user_limit_balance = self.user_concierge_options.maximum_opening_balance * product_tier.provider.fscs_limit_type.multiplier_if_joint - \
                             self.fscs_usage[fscs_holder]

        if user_limit_balance > balance:
            user_limit_balance = balance

        if user_limit_balance > product_tier.maximum:
            # Ensure we're not accidentally over the product maximum!
            user_limit_balance = product_tier.maximum

        # Protection Limit Decider
        if user_limit_balance > protection_limit_balance:
            # Pick whichever is the largest figure, use that. We want to fill all accounts as best we can.
            new_balance = user_limit_balance
        else:
            new_balance = protection_limit_balance

        if new_balance < self.user_concierge_options.maximum_opening_balance * product_tier.provider.fscs_limit_type.multiplier_if_joint:
            # If the balance is less than the user allows, there must be FSCS conflicts somewhere.
            fscs_conflicted = True

        elif new_balance < (
                    product_tier.provider.fscs_limit_type.balance_limit * product_tier.provider.fscs_limit_type.multiplier_if_joint) - \
                self.fscs_usage[fscs_holder]:
            # If the balance we worked out is less that we could possibly have on a joint account, there must be FSCS conflicts somewhere.
            fscs_conflicted = True
        return new_balance, fscs_conflicted, True

    def _determine_smallest_pool_for_product(self, product_tier):
        pool = 0
        for pool_position, pool in enumerate(self.pools):
            if (product_tier.product.term > pool.term or
                        (product_tier.product.notice / 30) > pool.term) and pool_position > 0:
                correct_pool = self.pools[pool_position - 1]
                break
            elif product_tier.product.term > pool.term or (product_tier.product.notice / 30) > pool.term:
                assert False, 'Supplied a product with longer term than any pool!'
        else:
            if len(self.pools) > 0:
                # If pools is True then pool will exist before the code reaches here.
                correct_pool = pool
            else:
                # print "Couldn't add to pool"
                return False, 0
        return True, correct_pool

    def add_product_to_most_appropriate_pool(self, account_balance, product_tier):
        """
            Calculates the correct pool for a product by term and notice period
            Loops over every pool we have in order of descending time period, and determines where the account hits the
            term/notice threshold, then places it in the shortest term valid pool.

            If it loops over every product and still hasn't selected a pool, it will use the last and smallest pool to hold
            the account.

            It asserts False if the first pool is smaller than the product term/notice as this product should never have
            been selected.
        """

        placed, correct_pool = self._determine_smallest_pool_for_product(product_tier)
        added = False
        reason = ''
        if placed:
            account_balance, added, reason = self._assign_money_from_pools(account_balance, correct_pool, product_tier)

        return added, correct_pool.term, account_balance, reason


    def _assign_money_from_pools(self, account_balance, correct_pool, product_tier):


        """

        Function designed to determine in a transactional manner, the maximum funds that are available from the current
        pools.

        Uses a temporary copy of the class wide pool_balance record, this ensures that we don't accidentally update
        self.product_balance

        :param account_balance:
        :param correct_pool:
        :param product_tier:
        :return: funds that could be allocated
        """

        local_pool_balance = deepcopy(self.pool_balance)

        usable_pools = [x for x in self.pools.order_by('term') if
                        x.term >= correct_pool.term]  # get all less restrictive pools
        unallocated_funds = account_balance

        for current_pool in usable_pools:
            if local_pool_balance[current_pool.term] > current_pool.balance:
                assert False, 'Pool %s balance has not been respected!' % current_pool.term
            if local_pool_balance[
                current_pool.term] + unallocated_funds <= current_pool.balance and unallocated_funds > Decimal(0):
                # current product would fit into this most restrictive pool, don't worry about looking for more cash
                local_pool_balance[current_pool.term] += unallocated_funds
                unallocated_funds = Decimal(0)
            elif local_pool_balance[current_pool.term] == current_pool.balance and unallocated_funds > Decimal(0):
                # Pool is already full!
                continue
            elif unallocated_funds > Decimal(0):
                # Pool can handle some money, but not all. look for additional funds
                funds_allowed = current_pool.balance - local_pool_balance[current_pool.term]
                local_pool_balance[current_pool.term] += funds_allowed
                unallocated_funds -= funds_allowed

        allocated = (account_balance - unallocated_funds)

        added = False
        reason = ''
        if allocated > 0:
            if allocated >= product_tier.minimum:
                added = True
                self._add_product_to_pool(correct_pool, product_tier, allocated)
                fscs_holder = product_tier.provider.fscs_licence_holder
                self.fscs_usage[fscs_holder] += allocated
                if self.pool_balance == local_pool_balance:
                    assert False, "Pretty sure if we've allocated funds, these two shouldn't be the same."
                self.pool_balance = local_pool_balance
            else:
                reason = 'Account balance did not reach the minimum for this product'
        else:
            reason = 'Account balance was 0'

        del local_pool_balance

        return allocated, added, reason

    def _add_product_to_pool(self, correct_pool, product_tier, account_balance):
        try:
            if self.user_concierge_options.monthly_interest:
                self.assigned_products[correct_pool.term].append(
                    (product_tier, product_tier.get_latest_rate(account_balance, monthly=True, opening_date=date.today()), account_balance)
                )
            else:
                self.assigned_products[correct_pool.term].append(
                    (product_tier, product_tier.get_latest_rate(account_balance, opening_date=date.today()), account_balance)
                )
        except KeyError:
            # print "Created Pool %s Early" % correct_pool.term
            if self.user_concierge_options.monthly_interest:
                self.assigned_products[correct_pool.term] = [
                    (product_tier, product_tier.get_latest_rate(account_balance, monthly=True, opening_date=date.today()), account_balance)]
            else:
                self.assigned_products[correct_pool.term] = [
                    (product_tier, product_tier.get_latest_rate(account_balance, opening_date=date.today()), account_balance)]

    def add_required_account(self, term, product_tier, balance, adjusted_pools, fscs=True):
        fscs_conflicted = False
        if fscs:
            balance, fscs_conflicted, joint = self.check_fscs(product_tier, balance)
            if joint:
                self.used_master_products[product_tier.product.pk]['joint'] += 1
            else:
                self.used_master_products[product_tier.product.pk]['own_name'] += 1
        added, added_to_pool_term, account_balance, reason = self.add_product_to_most_appropriate_pool(balance, product_tier)
        if not added:
            # Wasn't able to determine correct pool for product, add it to requested tier (might already have account open)
            if self.user_concierge_options.monthly_interest:
                self.assigned_products[term] = [(product_tier, product_tier.get_latest_rate(balance, monthly=True, opening_date=date.today()),
                                                 balance)]
            else:
                self.assigned_products[term] = [
                    (product_tier, product_tier.get_latest_rate(balance, opening_date=date.today()), balance)]
            adjusted_pools[term] += balance
        else:
            adjusted_pools[added_to_pool_term] += balance

        fscs_holder = product_tier.provider.fscs_licence_holder
        self.fscs_usage[fscs_holder] += Decimal(balance)
        self.used_master_products[product_tier.product.pk]['total'] += 1
        return balance, adjusted_pools, fscs_conflicted

    def handle_required_accounts(self):

        adjusted_pools = defaultdict(Decimal)
        for required_product_id, balance in self.required_accounts:
            required_product = MasterProduct.objects.get(pk=required_product_id)
            # print required_product, balance
            # First pool is longest term. check our product fits, if not make a fake pool for it
            if required_product.producttier_set.filter(available_until=None, minimum__lte=balance,
                                                       maximum__gte=balance).exists():
                required_product_tier = \
                    required_product.producttier_set.filter(available_until=None, minimum__lte=balance,
                                                            maximum__gte=balance)[0]

                if self.pools[0].term < required_product_tier.term:
                    added_balance, adjusted_pools, fscs_conflicted = self.add_required_account(
                        required_product_tier.term, required_product_tier, balance, adjusted_pools, fscs=False)
                elif required_product_tier.term_fixed_date is not None and datetime.now().date() + timedelta(
                        days=(self.pools[0].term * 30)) < required_product_tier.term_fixed_date:
                    term_delta = required_product_tier.term_fixed_date - datetime.now().date()
                    term = (term_delta.days / 30)
                    added_balance, adjusted_pools, fscs_conflicted = self.add_required_account(term,
                                                                                               required_product_tier,
                                                                                               balance, adjusted_pools,
                                                                                               fscs=False)
                else:
                    added_balance, adjusted_pools, fscs_conflicted = self.add_required_account(self.pools[0].term,
                                                                                               required_product_tier,
                                                                                               balance, adjusted_pools,
                                                                                               fscs=False)

                self.fscs_balance_fix(required_product_tier)
            else:
                pass
        return adjusted_pools

    def generated_portfolio_interest(self):
        interest = Decimal(0)

        for pool, accounts in self.assigned_products.iteritems():
            for account in accounts:
                product, rate, balance = account

                interest += (balance * (rate / 100))

        return interest

    def _add_to_naughty_list(self, account_balance, pool, product_tier, status_lines=None, rejections=None):
        if status_lines is None:
            status_lines = set()
        if rejections is None:
            rejections = set()

        frozen_status_lines = frozenset(status_lines)
        frozen_rejections = frozenset(rejections)

        if self.user_concierge_options.monthly_interest:
            self.naughty_list[pool.term].add(
                (product_tier, float(account_balance), product_tier.get_latest_rate(account_balance, monthly=True, opening_date=date.today()),
                 frozen_status_lines, frozen_rejections)
            )
        else:
            self.naughty_list[pool.term].add(
                (product_tier, float(account_balance), product_tier.get_latest_rate(account_balance, opening_date=date.today()),
                 frozen_status_lines, frozen_rejections)
            )

    def _use_existing_accounts(self):
        for product_portfolio in self.product_portfolios.filter(
                master_product__bestbuy_type__title__in=['Regular Savings',
                                                  'Variable Rate Bond',
                                                  'Variable Rate ISAs',
                                                  'Fixed Rate ISAs',
                                                  'Junior ISA']):
            self.fscs_usage[product_portfolio.provider.fscs_licence_holder] += product_portfolio.balance
        two_weeks_time = datetime.today() + timedelta(days=14)
        future_product_reminders = RatetrackerReminder.objects.filter(user=self.user, maturity_date__gte=two_weeks_time,
                                                                      is_deleted=False)
        for product in future_product_reminders:
            fscs_holder = product.provider.fscs_licence_holder
            self.fscs_usage[fscs_holder] += product.balance
        expired_product_reminders = RatetrackerReminder.objects.filter(user=self.user,
                                                                       maturity_date__lte=two_weeks_time,
                                                                       is_deleted=False, pool_altered=False,
                                                                       fee_exempt=True)
        pool_lengths = self.pools.order_by('-term', '-balance').values_list('term', 'pk')
        for product in expired_product_reminders:
            product_term = product.term
            for term, pk in pool_lengths:
                if product_term <= term:
                    product.pool_altered = True
                    ConciergeUserPool.objects.filter(pk=pk).update(balance=(F('balance') + product.balance))
                    product.save()
                    break
            else:
                # No pool of this term, add it.
                product.pool_altered = True
                ConciergeUserPool.objects.get_or_create(user=self.user, term=product.term, balance=product.balance)
                product.save()

    def fscs_balance_fix(self, required_product_tier):
        fscs_limit = required_product_tier.provider.fscs_limit_type.balance_limit
        user_limit = self.user_concierge_options.maximum_opening_balance
        fscs_conflicted_balance = user_limit if user_limit > fscs_limit else fscs_limit
        self.fscs_conflicts.append((required_product_tier.product.pk, fscs_conflicted_balance))

    def opening_options(self, product_tier, user_options, accepted_restrictions):
        open_methods = []
        rejections = []
        openable = False
        # todo: finish setting up restrictions
        if 'open_branch' not in accepted_restrictions:
            if product_tier.product.is_open_branch:
                open_methods.append('Branch')
                if user_options.open_branch:
                    openable = True
                else:
                    rejections.append('open_branch')
        else:
            open_methods.append('Branch')
            openable = True

        if 'open_telephone' not in accepted_restrictions:
            if product_tier.product.is_open_telephone:
                open_methods.append('Telephone')
                if user_options.open_telephone:
                    openable = True
                else:
                    rejections.append('open_telephone')
        else:
            open_methods.append('Telephone')
            openable = True

        if 'open_internet' not in accepted_restrictions:
            if product_tier.product.is_open_internet:
                open_methods.append('Internet')
                if user_options.open_internet:
                    openable = True
                else:
                    rejections.append('open_internet')
        else:
            open_methods.append('Internet')
            openable = True

        if 'open_post' not in accepted_restrictions:
            if product_tier.product.is_open_post:
                open_methods.append('Post')
                if user_options.open_post:
                    openable = True
                else:
                    rejections.append('open_post')
        else:
            open_methods.append('Post')
            openable = True

        return open_methods, openable, rejections

    def access_options(self, product_tier, user_options, accepted_restrictions):
        access_methods = []
        accessible = False
        rejections = []

        if 'open_branch' not in accepted_restrictions:
            if product_tier.product.is_branch_access:
                access_methods.append('Branch')
                if user_options.access_branch:
                    accessible = True
                else:
                    rejections.append('open_post')
        else:
            access_methods.append('Branch')
            accessible = True

        if 'open_telephone' not in accepted_restrictions:
            if product_tier.product.is_phone_access:
                access_methods.append('Telephone')
                if user_options.access_telephone:
                    accessible = True
                else:
                    rejections.append('open_post')
        else:
            access_methods.append('Telephone')
            accessible = True

        if 'open_internet' not in accepted_restrictions:
            if product_tier.product.is_internet_access:
                access_methods.append('Internet')
                if user_options.access_internet:
                    accessible = True
                else:
                    rejections.append('open_post')
        else:
            access_methods.append('Internet')
            accessible = True

        if 'open_post' not in accepted_restrictions:
            if product_tier.product.is_post_access:
                access_methods.append('Post')
                if user_options.access_post:
                    accessible = True
                else:
                    rejections.append('open_post')
        else:
            access_methods.append('Post')
            accessible = True

        return access_methods, accessible, rejections

    def account_filtering_logic(self, product_tier):

        verdict = True  # do we use this account or not?
        empty = False  # would this account have been empty?
        joint = False  # has this account be dealt with as a joint account?
        restrictions = set()
        accepted_restrictions = list(
            ConciergeUserAcceptedProduct.objects.filter(concierge_user=self.user_concierge_options,
                                                        product=product_tier.product).values_list('restriction',
                                                                                                  flat=True))
        status_lines = set()
        account_balance = product_tier.maximum

        if self.user_concierge_options.dual_portfolio:
            if self.used_master_products[product_tier.product.pk]['total'] >= (product_tier.product.open_limit_total +
                                                                               product_tier.product.open_limit_own_name):
                if product_tier.product.open_limit_total != -1:
                    status_line = u"%sProduct is already opened %s times, only allows %s for two people%s" % (
                        term_color.FAIL,
                        self.used_master_products[product_tier.product.pk]['total'],
                        (product_tier.product.open_limit_total + product_tier.product.open_limit_own_name),
                        term_color.ENDC
                    )
                    self.engine_log.append(status_line)
                    status_lines.add(status_line)
                    verdict = False
        elif self.used_master_products[product_tier.product.pk]['total'] >= product_tier.product.open_limit_total != -1:
            status_line = u"%sProduct is already opened %s times, only allows %s%s" % (
                term_color.FAIL,
                self.used_master_products[product_tier.product.pk]['total'],
                product_tier.product.open_limit_total,
                term_color.ENDC
            )
            self.engine_log.append(status_line)
            status_lines.add(status_line)
            verdict = False
            # If product is not over the amounts allowed for single user portfolio and
            # dual user portfolio (who can have another set of own name accounts)

        if self.user_concierge_options.joint_name or self.user_concierge_options.dual_portfolio:
            # Two people are part of this portfolio
            if self.user_concierge_options.joint_name:
                if self.used_master_products[product_tier.product.pk][
                        'joint'] == product_tier.product.open_limit_joint_name:
                    # Ensure we've some joint account spots left
                    if product_tier.product.open_limit_joint_name != -1:
                        status_line = u"%sProduct is already opened in joint %s times, only allows %s joint%s" % (
                            term_color.FAIL,
                            self.used_master_products[product_tier.product.pk]['joint'],
                            product_tier.product.open_limit_joint_name,
                            term_color.ENDC
                        )
                        self.engine_log.append(status_line)
                        status_lines.add(status_line)
                        joint_verdict = False
                    else:
                        joint_verdict = True
                else:
                    joint_verdict = True
            else:
                joint_verdict = False

            if self.user_concierge_options.dual_portfolio and self.used_master_products[product_tier.product.pk][
                    'own_name'] == product_tier.product.open_limit_own_name * 2:
                # we need to allow each person to open their own accounts
                if product_tier.product.open_limit_own_name != -1:
                    status_line = u"%sProduct is already opened in own name %s times, only allows %s in own name%s" % (
                        term_color.FAIL,
                        self.used_master_products[product_tier.product.pk]['own_name'],
                        (product_tier.product.open_limit_own_name * 2),
                        term_color.ENDC
                    )
                    self.engine_log.append(status_line)
                    status_lines.add(status_line)
                    own_verdict = False
                else:
                    own_verdict = True
            else:
                own_verdict = True
            if verdict:
                # Make sure we don't overwrite an already false verdict
                verdict = (joint_verdict or own_verdict)
            pass
        else:
            if self.used_master_products[product_tier.product.pk][
                    'own_name'] == product_tier.product.open_limit_own_name:
                if product_tier.product.open_limit_own_name != -1:
                    status_line = u"%sProduct is already opened %s times, only allows %s%s" % (
                        term_color.FAIL,
                        self.used_master_products[product_tier.product.pk]['own_name'],
                        product_tier.product.open_limit_own_name,
                        term_color.ENDC
                    )
                    self.engine_log.append(status_line)
                    status_lines.add(status_line)
                    verdict = False

        # Ensure Provider Limits Respected
        if product_tier.provider.provider_maximum != 0 and product_tier.provider.provider_maximum < account_balance + \
                self.provider_usage[product_tier.provider]:
            account_balance = product_tier.provider.provider_maximum - self.provider_usage[product_tier.provider]

        # Ensure User Limits are always respected as a maximum
        if ConciergeUserProviderRisk.objects.filter(user=self.user, provider=product_tier.provider).exists():
            # User has custom provider risk settings
            provider_risk = ConciergeUserProviderRisk.objects.get(user=self.user,
                                                                  provider=product_tier.provider)
            if provider_risk.maximum_balance < account_balance + self.provider_usage[product_tier.provider]:
                account_balance = provider_risk.maximum_balance - self.provider_usage[product_tier.provider]

        if ConciergeUserLicenceRisk.objects.filter(user=self.user,
                                                   provider__fscs_parent=product_tier.provider.fscs_parent).exists():
            pass

        if not self.user_concierge_options.ignore_fscs and not self.best_case:
            account_balance, fscs_conflicted, joint = self.check_fscs(product_tier, account_balance)
            if fscs_conflicted:
                self.fscs_balance_fix(product_tier)

        if self.user_concierge_options.monthly_interest:
            if not product_tier.get_latest_rate(account_balance,
                                                monthly=True, opening_date=date.today()) == product_tier.monthly_gross:
                status_line = u"%sLatest monthly rate of %s doesn't match expected rate of %s!%s" % (
                    term_color.FAIL, product_tier.get_latest_rate(account_balance, monthly=True, opening_date=date.today()),
                    product_tier.monthly_gross, term_color.ENDC)
                self.engine_log.append(status_line)
                status_lines.add(status_line)
                verdict = False
                empty = True  # Marked as empty, because you can't get this rate
        else:
            if not product_tier.get_latest_rate(account_balance, opening_date=date.today()) == product_tier.gross_rate:
                status_line = u"%sLatest rate of %s doesn't match the expected rate of %s!%s" % (
                    term_color.FAIL, product_tier.get_latest_rate(account_balance, opening_date=date.today()), product_tier.gross_rate,
                    term_color.ENDC)
                self.engine_log.append(status_line)
                status_lines.add(status_line)
                verdict = False
                empty = True  # Marked as empty, because you can't get this rate

        opening_methods, openable, rejections = self.opening_options(product_tier, self.user_concierge_options,
                                                                     accepted_restrictions)
        if not openable and not self.best_case:
            status_line = u"%sAccount can't be opened via any allowed methods, only via '%s'%s" % (
                term_color.FAIL, "', '".join(opening_methods), term_color.ENDC)
            self.engine_log.append(status_line)
            status_lines.add(status_line)
            for rejection in rejections:
                restrictions.add(rejection)
            verdict = False

        access_methods, accessible, rejections = self.access_options(product_tier, self.user_concierge_options,
                                                                     accepted_restrictions)
        if not accessible and not self.best_case:
            status_line = u"%sAccount can't be accessed via any allowed methods, only via '%s'%s" % (
                term_color.FAIL, "', '".join(access_methods), term_color.ENDC)
            self.engine_log.append(status_line)
            status_lines.add(status_line)
            for rejection in rejections:
                restrictions.add(rejection)
            verdict = False

        if ConciergeProviderAccountTypeLimitation.objects.filter(provider=product_tier.provider,
                                                                 bestbuys__in=product_tier.product.bestbuy_type.all()).exists():
            limitations = ConciergeProviderAccountTypeLimitation.objects.filter(provider=product_tier.provider,
                                                                                bestbuys__in=product_tier.product.bestbuy_type.all())
            for limitation in limitations:
                if limitation.pk not in self.provider_limitations:
                    self.provider_limitations[limitation.pk] = Decimal(0)
                if self.provider_limitations[limitation.pk] == limitation.maximum_balance:
                    status_line = u"%sHitting the provider's maximum for this product type(s) - Contact provider to confirm%s" % (
                        term_color.FAIL, term_color.ENDC)
                    self.engine_log.append(status_line)
                    status_lines.add(status_line)
                    restrictions.add('provider_maximum')
                    verdict = False
                if self.provider_limitations[limitation.pk] + account_balance > limitation.maximum_balance:
                    if limitation.maximum_balance - self.provider_limitations[limitation.pk] < product_tier.minimum:
                        status_line = u"%sHitting the provider's maximum for this product type(s) - Contact provider to confirm%s" % (
                            term_color.FAIL, term_color.ENDC)
                        self.engine_log.append(status_line)
                        status_lines.add(status_line)
                        restrictions.add('provider_maximum')
                        verdict = False
                    else:
                        account_balance_old = account_balance
                        account_balance = limitation.maximum_balance - self.provider_limitations[limitation.pk]
                        status_line = u"%s%s %s account balance altered from %s to %s due to provider maximum on this account type(s)%s" % (
                            term_color.FAIL, product_tier.provider.title, product_tier.product.title,
                            account_balance_old, account_balance,
                            term_color.ENDC)
                        self.engine_log.append(status_line)
                        status_lines.add(status_line)

        if account_balance < Decimal('1'):
            status_line = u"%sWe cannot open an empty account%s" % (
                term_color.FAIL, term_color.ENDC)

            self.engine_log.append(status_line)
            status_lines.add(status_line)
            verdict = False
            empty = True

        if not account_balance >= product_tier.minimum:
            status_line = u"%sAccount requires more money than is remaining in this pool%s" % (
                term_color.FAIL, term_color.ENDC)

            self.engine_log.append(status_line)
            status_lines.add(status_line)
            verdict = False
            empty = True

        if not product_tier.product.minimum_age <= self.user_concierge_options.get_age() <= product_tier.product.maximum_age and product_tier.product.maximum_age > 0:
            status_line = u"%sWe can't open this account when client is not in age range %s - %s%s" % (
                term_color.FAIL, str(product_tier.product.minimum_age), str(product_tier.product.maximum_age), term_color.ENDC)

            self.engine_log.append(status_line)
            status_lines.add(status_line)
            verdict = False

        if 'existing' not in accepted_restrictions and product_tier.product.existing_only and not self.best_case:
            status_line = u"%sAvailable to existing customers only%s" % (
                term_color.FAIL, term_color.ENDC)
            self.engine_log.append(status_line)
            status_lines.add(status_line)
            restrictions.add('existing')
            verdict = False

        if 'locals' not in accepted_restrictions and product_tier.product.locals_only and not self.best_case:
            status_line = u"%sAvailable to local customers only%s" % (
                term_color.FAIL, term_color.ENDC)
            self.engine_log.append(status_line)
            status_lines.add(status_line)
            restrictions.add('local')
            verdict = False

        if 'sharia' not in accepted_restrictions:
            if product_tier.product.shariaa:
                if not self.best_case:
                    status_line = u"%sSharia'a accounts do not guarantee return of funds and/or interest %s" % (
                        term_color.FAIL, term_color.ENDC)
                    self.engine_log.append(status_line)
                    status_lines.add(status_line)
                    restrictions.add('sharia')
                    verdict = False

        if 'joint_account' not in accepted_restrictions:
            if product_tier.joint_account_only:
                if not self.best_case:
                    status_line = u"%sThe rate is only available as a joint account%s" % (
                        term_color.FAIL, term_color.ENDC)
                    self.engine_log.append(status_line)
                    status_lines.add(status_line)
                    restrictions.add('joint_acount')
                    verdict = False

        if 'current_account' not in accepted_restrictions:
            if product_tier.product.bestbuy_type.filter(title__in=['High Interest Current Accounts',
                                                                   'Current Accounts']).exists():
                if not self.best_case:
                    status_line = u"%sCurrent accounts have more complex terms and conditions, and lower maximum balances%s" % (
                        term_color.FAIL, term_color.ENDC)
                    self.engine_log.append(status_line)
                    status_lines.add(status_line)
                    restrictions.add('current_account')
                    verdict = False

        if 'opening_threshold' not in accepted_restrictions:
            if not account_balance >= self.user_concierge_options.minimum_opening_balance:
                if not account_balance == Decimal(0):
                    status_line = u"%sThe balance was lower than the user's opening threshold or was £0%s" % (
                        term_color.FAIL, term_color.ENDC)

                    self.engine_log.append(status_line)
                    status_lines.add(status_line)
                    restrictions.add('opening_threshold')
                    # print status_line
                    verdict = False

        if 'other_reason' not in accepted_restrictions:
            if (product_tier.product.other_reason_to_exclude_this_product != '' or
                    product_tier.product.other_reason_compliance_checked):
                if not self.best_case:
                    status_line = u"%s%s%s" % (
                        term_color.FAIL, product_tier.product.other_reason_to_exclude_this_product, term_color.ENDC
                    )

                    self.engine_log.append(status_line)
                    status_lines.add(status_line)
                    restrictions.add('other_reason')
                    # print status_line
                    verdict = False

        return verdict, account_balance, restrictions, status_lines, empty, joint

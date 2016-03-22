# coding=utf-8
import uuid
from behave import *
import datetime
from django.test import RequestFactory
from common.accounts.utils import create_stage_one_profile
from concierge.engine import Engine
from concierge.models import ConciergeUserPool
from products.models import Provider, FSCSLimitType, MasterProduct, ProductTier

use_step_matcher("re")


@given("a typical user")
def step_impl(context):
    """
    :type context behave.runner.Context
    """
    request = RequestFactory().get('/')
    request.session = {}
    user, user_created, record_stats = create_stage_one_profile(request,
                                                                'default_user@example.com',
                                                                'testing',
                                                                send_activation=False,
                                                                login_user=False,
                                                                use_site_framework=False)
    context.user = user
    context.user_created = user_created


@step("this user wants to tie up their money for")
def step_impl(context):
    """
    :type context behave.runner.Context
    :type amount str
    :type term str
    """
    ConciergeUserPool.objects.filter(user=context.user).delete()
    for pool in context.table:
        ConciergeUserPool.objects.get_or_create(user=context.user, term=pool['term'], balance=pool['amount'])

@when("the engine is run on the default user")
def step_impl(context):
    """
    :type context behave.runner.Context
    """
    engine = Engine('default_user@example.com')
    context.assigned_products, context.engine_log, context.naughty_list, \
    context.total_amount, context.generated_portfolio_interest, context.fscs_conflicts = engine.improve_portfolio()

@then("the engine should give recommendations")
def step_impl(context):
    """
    :type context behave.runner.Context
    """

    assert isinstance(context.assigned_products, dict)
    assert 36 in context.assigned_products
    assert 12 in context.assigned_products
    assert 0 in context.assigned_products
    assert len(context.assigned_products[36]) == 0, (36, context.assigned_products[36])
    assert len(context.assigned_products[12]) == 0, (12, context.assigned_products[12])
    assert len(context.assigned_products[0]) == 0, (0, context.assigned_products[0])


@step("the products available are")
def step_impl(context):
    """
    :type context behave.runner.Context
    """
    Provider.objects.all().delete()
    for product in context.table:

        fscs_licence, _ = FSCSLimitType.objects.get_or_create(name=product['fscs_licence'])
        if _:
            fscs_licence.balance_limit = product['fscs_licence_limit']
            fscs_licence.save()

        provider, _ = Provider.objects.get_or_create(title=product['provider'])
        if _:
            provider.provider_maximum = product['provider_maximum']
            provider.fscs_limit_type = fscs_licence
            provider.save()

        master_product, _ = MasterProduct.objects.get_or_create(title=product['product'])
        if _:
            master_product.provider = provider
            master_product.status = 'Live'
            master_product.available_from = datetime.datetime.now() - datetime.timedelta(days=7)
            master_product.available_to = datetime.datetime.now() + datetime.timedelta(days=14)
            master_product.is_internet_access = True
            master_product.is_phone_access = True
            master_product.is_post_access = True
            master_product.is_branch_access = True
            master_product.is_cc_access = True
            master_product.is_open_internet = True
            master_product.is_open_telephone = True
            master_product.is_open_post = True
            master_product.is_open_branch = True
            master_product.is_open_cc = True
            master_product.save()

        product_tier, _ = ProductTier.objects.get_or_create(provider=provider,
                                                            product=master_product,
                                                            maximum=product['maximum'],
                                                            minimum=product['minimum'],
                                                            sc_code=product['sc_code'],
                                                            sf_product_tier_id=uuid.uuid4())
        if _:
            product_tier.provider = provider
            product_tier.gross_rate = product['rate']
            product_tier.save()


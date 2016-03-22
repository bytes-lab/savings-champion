from django.shortcuts import render
from products.models import BestBuy

__author__ = 'josh'


def moneytothemasses_personal_top_accounts(request, bestbuy_slug, context=None):
    if context is None:
        context = {}

    # required for the sidebar
    bestbuys = BestBuy.objects.filter(has_table=True, client_type='p')
    context['bestbuys'] = bestbuys
    context['bestbuyselected'] = True

    bestbuy = BestBuy.objects.get(slug=bestbuy_slug, client_type='p')
    context['bestbuy'] = bestbuy

    # Money to the masses are only allowed our top 5 accounts in Fixed Rate Bonds and Fixed rate ISA
    if bestbuy_slug not in ['fixed-rate-bond', 'fixed-rate-isa']:
        context['products'] = bestbuy.get_personal_products()
    else:
        context['products'] = bestbuy.get_personal_products(old_order_by=False).filter(link_to_products__rank=0,
                                                                     link_to_products__date_replaced=None).order_by('term').distinct()
    return render(request, 'products/moneytothemasses/table.html', context)


def mymoneydiva_personal_top_accounts(request, bestbuy_slug, context=None):
    if context is None:
        context = {}

    # required for the sidebar
    bestbuys = BestBuy.objects.filter(has_table=True, client_type='p')
    context['bestbuys'] = bestbuys
    context['bestbuyselected'] = True

    bestbuy = BestBuy.objects.get(slug=bestbuy_slug, client_type='p')
    context['bestbuy'] = bestbuy

    # Money to the masses are only allowed our top 5 accounts in Fixed Rate Bonds and Fixed rate ISA
    if bestbuy_slug not in ['fixed-rate-bond', 'fixed-rate-isa']:
        context['products'] = bestbuy.get_personal_products()
    else:
        context['products'] = bestbuy.get_personal_products(old_order_by=False).filter(link_to_products__rank=0,
                                                                                       link_to_products__date_replaced=None).order_by(
            'term').distinct()
    return render(request, 'products/mymoneydiva/table.html', context)


def mymoneydiva_business_top_accounts(request, bestbuy_slug, context=None):
    if context is None:
        context = {}

    # required for the sidebar
    bestbuys = BestBuy.objects.filter(has_table=True, client_type='b')
    context['bestbuys'] = bestbuys
    context['bestbuyselected'] = True

    bestbuy = BestBuy.objects.get(slug=bestbuy_slug, client_type='b')
    context['bestbuy'] = bestbuy

    # Money to the masses are only allowed our top 5 accounts in Fixed Rate Bonds and Fixed rate ISA
    if bestbuy_slug not in ['fixed-rate-bond', 'fixed-rate-isa']:
        context['products'] = bestbuy.get_business_products()
    else:
        context['products'] = bestbuy.get_business_products(old_order_by=False).filter(link_to_products__rank=0,
                                                                                       link_to_products__date_replaced=None).order_by(
            'term').distinct()
    return render(request, 'products/mymoneydiva/business_table.html', context)

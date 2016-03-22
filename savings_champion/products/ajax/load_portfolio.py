#contains the methods for retrieving HTML for the portfolio
from decimal import Decimal
from django.contrib.auth.models import User
from django.db.models import Sum
from django.http import HttpResponse 
from django.template.loader import get_template
from django.template import RequestContext
from itertools import chain
from django.views.decorators.cache import never_cache
from common.models import Profile, CampaignsSignup
from products.models import ProductPortfolio, RatetrackerReminder
from django.shortcuts import redirect, render
from multiprocessing.dummy import Pool as ThreadPool

def portfolio_sort(portfolio_object):
    return portfolio_object.get_personal_rating

@never_cache
def load_portfolio(request, context=None):
    if context is None:
        context = {}
    if request.is_ajax() and request.user.is_authenticated():

        portfolio = ProductPortfolio.objects.filter(user=request.user, is_deleted=False)
        reminders = RatetrackerReminder.objects.filter(user=request.user, is_deleted=False)
        total = Decimal(0)

        portfolio_balance_total = portfolio.aggregate(portfolio_balance_sum=Sum('balance'))['portfolio_balance_sum']

        if portfolio_balance_total is not None:
            total += portfolio_balance_total

        reminder_balance_total = reminders.aggregate(reminder_balance_sum=Sum('balance'))['reminder_balance_sum']

        if reminder_balance_total is not None:
            total += reminder_balance_total

        portfolio = sorted(chain(portfolio, reminders), key=portfolio_sort)

        for p in portfolio:
            context[p.get_personal_rating_readable.split(' ')[0]] = True
        if total >= 85000:
            context['conciergeUpsell'] = True
        context['portfolio'] = portfolio
        context['grandtotal'] = total
        try:
            context['concierge'] = CampaignsSignup.objects.get(email=request.user.email)
        except:
            context['concierge'] = {'is_client': False}

        return render(request, 'products/healthcheck/portfolio_display.html', context)
    else:
        return redirect('ajax_required')

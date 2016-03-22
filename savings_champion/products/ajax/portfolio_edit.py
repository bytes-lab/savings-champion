from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import re
from products.models import ProductPortfolio, RatetrackerReminder
from decimal import *
from django.template.loader import get_template
from django.template import Context
from django.core.mail import mail_admins
from django.core.mail import send_mail
import datetime
from django.shortcuts import redirect, render


@login_required
def update_portfolio_balance(request, context=None):

    if context is None:
        context = {}

    if request.method == 'POST':

        # request.POST['id'] for the portfolio id
        # request.POST['balance'] for the new balance.

        if not request.user.is_staff:
            user_portfolio = ProductPortfolio.objects.get(id=request.POST['id'], user=request.user)
        else:
            user_portfolio = ProductPortfolio.objects.get(id=request.POST['id'])

        balance = request.POST['balance']

        #Just in case something got through the javascript.
        balance = re.sub(r'[^.0-9]', "", balance)

        # force the balance to be positive, we only track savings here...
        balance = abs(Decimal(balance))

        # Source the old rate, before we update the balance otherwise we'll lose it!
        oldRate = user_portfolio.master_product.get_latest_rate(user_portfolio.balance, user_portfolio.opening_date)

        user_portfolio.balance = balance
        context['product'] = user_portfolio.master_product.title
        context['balance'] = balance
        new_product = user_portfolio.master_product.get_latest_product_tier(balance)
        newRate = user_portfolio.master_product.get_latest_rate(balance, user_portfolio.opening_date)
        context['rate'] = "{0:.2f}%".format(newRate)

        user_portfolio.is_synched = False

        try:
            user_portfolio.save()
        except Exception as ex:
            mail_admins("Exception when updating the balance", "%s %s" % (ex, request.user.email), )
            return render(request, 'products/ratetracker/editfail.html', context)

        if balance > new_product.maximum:
            context['outsideLimitMessage'] = "Your new balance is above the maximum \
            set by the provider for this account. You should confirm the correct \
            rate with your provider, or contact us for help at info@savingschampion.co.uk \
            or 0800 321 3581"
        elif balance < new_product.minimum:
            context['outsideLimitMessage'] = "Your new balance is below the minimum \
            set by the provider for this account. You should confirm the correct \
            rate with your provider, or contact us for help at info@savingschampion.co.uk \
            or 0800 321 3581"

        if request.is_ajax():
            if newRate > oldRate:
                render(request, 'products/ratetracker/editsuccessnewrate.html', context)
            else:
                render(request, 'products/ratetracker/editsuccess.html', context)

    return redirect('healthcheck-portfolio')


@login_required
def update_reminder_balance(request):
    # the portfolio one is probably too complicated when this will just need to change the balance.
    if request.method == 'POST':
        #request.POST['id'] for the reminder id
        #request.POST['balance'] for the new balance.

        if not request.user.is_staff:
            userReminder = RatetrackerReminder.objects.get(id=request.POST['id'], user=request.user)
        else:
            userReminder = RatetrackerReminder.objects.get(id=request.POST['id'])

        balance = request.POST['balance']
        rate = request.POST['rate']
        c = Context()
        html = get_template('products/ratetracker/editsuccess.html')

        try:
            #Just in case some commas got through the javascript.
            balance = re.sub(r'[^.0-9]', "", balance)
            balance = Decimal(balance)

            if balance < 0:
                raise Exception("The balance really shouldn't be less than 0")
        except Exception as ex:
            mail_admins("Exception when updating the balance", "%s %s" % (ex, request.user.email), )
            html = get_template('products/ratetracker/editfail.html')
            html_content = html.render(c)
            return HttpResponse(html_content)

        try:
            userReminder.balance = balance
            userReminder.rate = rate
            c = Context({'product': "your %s" % userReminder.account_type,
                         'balance': balance,
                         'rate': rate})
            userReminder.is_synched = False
            userReminder.save()

        except Exception as ex:
            mail_admins("Exception when updating the balance", "%s %s" % (ex, request.user.email), )
            html = get_template('products/ratetracker/editfail.html')
            html_content = html.render(c)
            return HttpResponse(html_content)

        html_content = html.render(c)
        if request.is_ajax():
            return HttpResponse(html_content)
        else:
            return redirect('healthcheck-portfolio')


@login_required
def add_opening(request):
    if request.method == 'POST':
        pp_id = int(request.POST['portfolio_id'])

        if not request.user.is_staff:
            portfolio = ProductPortfolio.objects.get(id=pp_id, user=request.user)
        else:
            portfolio = ProductPortfolio.objects.get(id=pp_id)

        year = int(request.POST['opening_date_year'])
        month = int(request.POST['opening_date_month'])

        if year > 0 and month > 0:
            portfolio.opening_date = datetime.datetime(year, month, 1).date()
            portfolio.is_synched = False
            portfolio.save()

        if request.is_ajax():
            return HttpResponse('')
        else:
            return redirect('healthcheck-portfolio')

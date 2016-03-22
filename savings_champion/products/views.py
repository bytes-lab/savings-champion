# Create your views here.
from collections import OrderedDict
from itertools import chain
from collections import defaultdict
from decimal import Decimal
from django.db.models import F, Sum
#from django_select2 import Select2View, NO_ERR_RESP
from django.shortcuts import render_to_response, redirect, render, get_object_or_404
from django.template import RequestContext
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from common.accounts.utils import create_stage_one_profile
from common.models import Referrer, CampaignsSignup
from common.utils import record_referral_signup
from concierge.models import AdviserQueue
from products.models import BestBuy, Product, ProductPortfolio, RatetrackerReminder, MasterProduct
from products.forms import AddProductsForm, WeeklyRateAlertsForm, RateTrackerThresholdForm, WeeklyBusinessRateAlertsForm, \
    BestBuyCallbackForm
from products.forms import ReminderEditForm, PortfolioEditForm, AddFixedProductForm, AddOpeningDateForm, \
    EmailInstructionsForm
from common.accounts.forms import SignUpForm
from pages.models import FAQ
from common.tasks import add_to_campaign_monitor, analytics, update_subscription_on_email_service

BESTBUYS_COUNT = getattr(settings, 'BESTBUYS_COUNT', 5)
EMPTY_VALUES = ['', None, '']


def check_opening_date_exists(request):
    message = ""
    if request.is_ajax() and request.method == 'POST':
        if not request.POST["productID"] == "0" and request.POST["productID"] not in EMPTY_VALUES:
            try:
                message = Product.objects.get(pk=request.POST["productID"]).show_opening_date()
            except Product.DoesNotExist as e:
                message = ""

    return HttpResponse(message)


def savings_healthcheck(request, template_file="products/healthcheck/healthcheck_landing.html"):
    context = RequestContext(request)
    if request.user.is_authenticated():
        return redirect('healthcheck-portfolio')
    initial = {}
    form_class = SignUpForm

    form = form_class

    return render_to_response('products/healthcheck/healthcheck_landing.html',
                              {'form': form},
                              context_instance=context)


def savings_healthcheck_faq(request, template_file="products/healthcheck/healthcheck_faq.html"):
    context = RequestContext(request)
    if request.user.is_authenticated():
        return redirect('healthcheck-portfolio')

    context['form'] = SignUpForm()
    context['faqs'] = FAQ.objects.get(title="Healthcheck").faqblock_set.all().order_by('order')
    return render_to_response("products/healthcheck/healthcheck_faq.html",
                              context_instance=context)


def portfolio_sort(portfolio_object):
    return portfolio_object.get_personal_rating


@login_required
@never_cache
def savings_healthcheck_portfolio(request, context=None):
    if context is None:
        context = {}

    portfolio = ProductPortfolio.objects.filter(user=request.user, is_deleted=False).select_related('master_product', 'master_product__provider').prefetch_related('master_product__producttier_set')
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

    if request.user.is_authenticated():
        context['form'] = AddProductsForm()
        context['edit_form'] = PortfolioEditForm()
        context['reminder_edit'] = ReminderEditForm()
        context['fixed_product_form'] = AddFixedProductForm()
        context['opening_date_form'] = AddOpeningDateForm()
        context['threshold_form'] = RateTrackerThresholdForm(
            initial={'amount': request.user.profile.ratetracker_threshold})
    return render(request, "products/healthcheck/healthcheck_portfolio.html", context)


@login_required
def savings_healthcheck_portfolio_nojavascript(request,
                                               template_file="products/healthcheck/healthcheck_portfolio_nojs.html"):
    context = RequestContext(request)

    if request.user.is_authenticated():
        portfolio = ProductPortfolio.objects.filter(user=request.user, is_deleted=False)
        reminders = RatetrackerReminder.objects.filter(user=request.user, is_deleted=False)
        portfolio = chain(portfolio, reminders)
        total = 0
        for p in portfolio:
            total += p.balance
        context['grandtotal'] = total
        context['portfolio'] = portfolio
        context['form'] = AddProductsForm()
        context['edit_form'] = PortfolioEditForm()
        context['reminder_edit'] = ReminderEditForm()
        context['fixed_product_form'] = AddFixedProductForm()
        context['opening_date_form'] = AddOpeningDateForm()
    return render_to_response(template_file,
                              context_instance=context)


@login_required
def savings_healthcheck_portfolio_add_product(request, template_file="products/healthcheck/success/newproduct.html", context=None):
    if context is None:
        context = {}
    form = AddProductsForm()
    if request.method == "POST":
        form = AddProductsForm(request.POST)
        if form.is_valid():
            user = request.user
            product = Product.objects.get(pk=form.cleaned_data.get('product'))
            portfolio = ProductPortfolio()
            portfolio.user = user

            portfolio.account_type = BestBuy.objects.get(id=product.bestbuy_type.all()[0].id)
            portfolio.balance = form.cleaned_data.get('balance')
            portfolio.master_product = product.master_product
            portfolio.provider = product.provider

            # When making I found some bonus terms can be entered as '' as well as None
            #hence the ugly if statement to ensure it is an int
            #as it only gets evaluated on portfolio.save() which by then a typeerror try/except is too late as it could be any field

            if isinstance(product.bonus_term, int) or isinstance(product.bonus_term, float):
                portfolio.bonus_term = product.bonus_term
            else:
                portfolio.bonus_term = None

            portfolio.notice = product.notice

            opening_date = form.cleaned_data.get('opening_date')
            if opening_date:
                portfolio.opening_date = opening_date
            portfolio.is_synched = False
            portfolio.save()

            context['p'] = portfolio
            record_referral_signup(request=request, user=user, user_created=False, action='rate_tracker_used',
                                   third_party=False)
            if request.is_ajax():
                return render(request, template_file, context)
    context['form'] = form
    context['error'] = True
    template_file = 'products/healthcheck/addproductsform.html'
    return render(request, template_file, context)


@login_required
def savings_healthcheck_portfolio_add_fixed_product(request,
                                                    template_file="products/healthcheck/success/newproduct.html", context=None):
    if context is None:
        context = {}
    form = AddFixedProductForm()
    if request.method == "POST":
        form = AddFixedProductForm(request.POST)
        if form.is_valid():
            user = request.user

            reminder = RatetrackerReminder()
            reminder.user = user

            reminder.provider = form.cleaned_data.get('fixed_provider')

            account_type = BestBuy.objects.get(id=form.cleaned_data.get('account_type'))
            reminder.account_type = account_type

            reminder.balance = form.cleaned_data.get('balance')
            reminder.rate = form.cleaned_data.get('rate')

            reminder.maturity_date = form.cleaned_data.get('maturity_date')

            reminder.is_synched = False
            reminder.save()

            context['p'] = reminder
            record_referral_signup(request=request, user=user, user_created=False, action='rate_tracker_used',
                                   third_party=False)
            if request.is_ajax():
                return render(request, template_file, context)
        else:
            messages.error(request, 'Your Savings Product was invalid.')
    context['fixed_product_form'] = form
    context['error'] = True
    template_file = 'products/healthcheck/addfixedproductsform.html'
    return render(request, template_file, context)


def top_personal_accounts_index(request, template_file="products/topaccounts/index.html"):
    context = RequestContext(request)

    bestbuys = BestBuy.objects.filter(has_table=True, client_type='p')
    context['bestbuys'] = bestbuys
    context['bestbuyselected'] = False
    return render_to_response(template_file,
                              context_instance=context)

def top_business_accounts_index(request, template_file="products/topaccounts/business/index.html"):
    context = RequestContext(request)

    bestbuys = BestBuy.objects.filter(has_table=True, client_type='b')
    context['bestbuys'] = bestbuys
    context['bestbuyselected'] = False
    return render_to_response(template_file,
                              context_instance=context)


def personal_top_accounts(request, bestbuy_slug, term=None):
    context = RequestContext(request)

    # required for the sidebar
    bestbuys = BestBuy.objects.filter(has_table=True, client_type='p')
    context['bestbuys'] = bestbuys
    context['bestbuyselected'] = True

    bestbuy = BestBuy.objects.get(slug=bestbuy_slug, client_type='p')
    context['bestbuy'] = bestbuy

    products = bestbuy.get_personal_products(term=term)
    fixed_rate_bond_products = defaultdict(list)
    for product in products:
        product_term = product.link_to_products.get(bestbuy=bestbuy, product=product, date_replaced=None).term
        fixed_rate_bond_products[product_term].append(product)
    context['terms'] = fixed_rate_bond_products.keys()
    context['products'] = fixed_rate_bond_products
    context['emailform'] = EmailInstructionsForm()
    context['weekly_form'] = WeeklyRateAlertsForm()

    if request.method == 'POST':
        form = WeeklyRateAlertsForm(request.POST)
        if form.is_valid():
            best_buy_table_emails = form.save()
            if 'referer' in request.session:
                referer = Referrer.objects.get(pk=request.session['referer']).name
            else:
                referer = '(Direct)'
            analytics.delay('event', 'Reccuring Best Buy Emails', 'Signup', referer)
            create_profile_output = create_stage_one_profile(request=request, email=best_buy_table_emails.email,
                                                             source='recurring_best_buy_emails', send_activation=False,
                                                             login_user=False)
            if isinstance(create_profile_output, tuple):
                user, user_created, record_stats = create_profile_output
            else:
                return create_profile_output
            record_referral_signup(request=request, user=user, user_created=user_created,
                                   action='signup')
            context['weekly_signed_up'] = True
            from common.tasks import update_subscription_on_email_service
            if best_buy_table_emails.frequency == 1:
                update_subscription_on_email_service.delay(best_buy_table_emails.email, interest_group=u'Daily Best Buy Tables')
                record_referral_signup(request=request, user=user, user_created=user_created,
                                       action='recurring_daily_best_buys')
            if best_buy_table_emails.frequency == 2:
                update_subscription_on_email_service.delay(best_buy_table_emails.email, interest_group=u'Weekly Best Buy Tables')
                record_referral_signup(request=request, user=user, user_created=user_created,
                                       action='recurring_weekly_best_buys')
            if best_buy_table_emails.frequency == 3:
                update_subscription_on_email_service.delay(best_buy_table_emails.email, interest_group=u'Monthly Best Buy Tables')
                record_referral_signup(request=request, user=user, user_created=user_created,
                                       action='recurring_monthly_best_buys')

    return render_to_response('products/topaccounts/table.html',
                              context_instance=context)


def business_top_accounts(request, bestbuy_slug, term=None):
    context = RequestContext(request)

    # required for the sidebar
    bestbuys = BestBuy.objects.filter(has_table=True, client_type='b')
    context['bestbuys'] = bestbuys
    context['bestbuyselected'] = True

    bestbuy = BestBuy.objects.get(slug=bestbuy_slug, client_type='b')
    context['bestbuy'] = bestbuy

    products = bestbuy.get_business_products(term)
    fixed_rate_bond_products = defaultdict(list)
    for product in products:
        product_term = product.link_to_products.get(bestbuy=bestbuy, product=product, date_replaced=None).term
        fixed_rate_bond_products[product_term].append(product)
    context['terms'] = fixed_rate_bond_products.keys()
    context['products'] = fixed_rate_bond_products

    return render_to_response('products/topaccounts/business/table.html',
                              context_instance=context)


def best_buy_table_callback(request, context=None):
    if context is None:
        context = {}

    if request.method == 'POST':
        form = BestBuyCallbackForm(request.POST)
        if form.is_valid():
            create_profile_output = create_stage_one_profile(request=request, email=form.cleaned_data['email'],
                                                             source='best_buy_call_back', send_activation=False,
                                                             login_user=False)
            user, user_created, record_stats = create_profile_output
            record_referral_signup(request=request, user=user, user_created=user_created,
                                   action='best_buy_call_back')
            AdviserQueue.add_to_queue(email=form.cleaned_data['email'],
                                      first_name=form.cleaned_data['name'],
                                      last_name='.',
                                      lead_source='Best Buy Call Back',
                                      telephone_number=form.cleaned_data['phone'])
            return render(request, 'products/topaccounts/callback/success.html', context)
        context['form'] = form
        return render(request, 'products/topaccounts/callback/form.html', context)
    return render(request, 'products/topaccounts/callback/failure.html', context)


@login_required
def compare_top_accounts(request, portfolio_id=None, template_file="products/topaccounts/compare.html"):
    context = RequestContext(request)
    if portfolio_id is None:
        portfolio_id = request.GET.get('id')
    fixed = request.GET.get('fixed')
    if not fixed:
        try:
            portfolio = ProductPortfolio.objects.get(id=portfolio_id)
        except ProductPortfolio.DoesNotExist:
            return redirect('healthcheck-portfolio')
        context['yourproduct'] = portfolio.master_product.return_product_from_balance(portfolio.balance)
        bestbuy = BestBuy.objects.get(title=portfolio.master_product.get_bestbuy_type, client_type='p')
    else:
        template_file = "products/topaccounts/compare_fixed.html"
        try:
            portfolio = RatetrackerReminder.objects.get(id=portfolio_id)
        except RatetrackerReminder.DoesNotExist:
            return redirect('healthcheck-portfolio')
        bestbuy = BestBuy.objects.get(title=portfolio.account_type, client_type='p')
    context['portfolio'] = portfolio
    context['products'] = bestbuy.get_personal_products(balance=portfolio.balance)

    if portfolio.user != request.user and not request.user.is_staff:
        return redirect('healthcheck-portfolio')

    return render_to_response(template_file,
                              context_instance=context)


@login_required
def print_portfolio(request):
    context = RequestContext(request)

    portfolio = ProductPortfolio.objects.filter(user=request.user, is_deleted=False)
    reminders = RatetrackerReminder.objects.filter(user=request.user, is_deleted=False)

    portfolio = sorted(chain(portfolio, reminders),
                       key=portfolio_sort)

    total = 0
    for p in portfolio:
        total += p.balance

    context['grandtotal'] = total
    context['portfolio'] = portfolio
    return render_to_response("products/healthcheck/print_portfolio.html", context_instance=context)


# class ProductSelect2View(Select2View):
#     def check_all_permissions(self, request, *args, **kwargs):
#         user = request.user
#         if not user.is_authenticated():
#             raise PermissionDenied
#
#     def get_results(self, request, term, page, context):
#         products = Product.objects.filter(provider_id=term)
#         res = [(product.pk, product.title) for product in products]
#         return NO_ERR_RESP, False, res  # Any error response, Has more results, options list


@never_cache
def view_all_bestbuys(request):
    bestbuy_dict = OrderedDict()
    bestbuys = BestBuy.objects.filter(has_table=True, client_type='p').select_related()
    for bestbuy in bestbuys:
        bestbuy_dict[bestbuy.title] = bestbuy.products.all()
    return render(request, 'products/campaign_monitor/campaign.html', {'bestbuys': bestbuy_dict},
                  content_type='text/plain')


def reccuring_bestbuy_emails(request):
    context = {'weekly_form': WeeklyRateAlertsForm()}
    if request.method == 'POST':
        form = WeeklyRateAlertsForm(request.POST)
        if form.is_valid():
            best_buy_table_emails = form.save()
            if 'referer' in request.session:
                referer = Referrer.objects.get(pk=request.session['referer']).name
            else:
                referer = '(Direct)'
            analytics.delay('event', 'Reccuring Best Buy Emails', 'Signup', referer)
            create_profile_output = create_stage_one_profile(request=request, email=best_buy_table_emails.email,
                                                             source='recurring_best_buy_emails', send_activation=False,
                                                             login_user=False)
            if isinstance(create_profile_output, tuple):
                user, user_created, record_stats = create_profile_output
            else:
                return create_profile_output
            record_referral_signup(request=request, user=user, user_created=user_created, action='signup')
            context['weekly_signed_up'] = True
            if best_buy_table_emails.frequency == 1:
                update_subscription_on_email_service.delay(best_buy_table_emails.email, interest_group=u'Daily Best Buy Tables')
                record_referral_signup(request=request, user=user, user_created=user_created,
                                       action='recurring_daily_best_buys')
            if best_buy_table_emails.frequency == 2:
                update_subscription_on_email_service.delay(best_buy_table_emails.email, interest_group=u'Weekly Best Buy Tables')
                record_referral_signup(request=request, user=user, user_created=user_created,
                                       action='recurring_weekly_best_buys')
            if best_buy_table_emails.frequency == 3:
                update_subscription_on_email_service.delay(best_buy_table_emails.email, interest_group=u'Monthly Best Buy Tables')
                record_referral_signup(request=request, user=user, user_created=user_created,
                                       action='recurring_monthly_best_buys')
    return render(request, 'products/topaccounts/reccuring_emails.html', context)


def reccuring_business_bestbuy_emails(request):
    context = {'weekly_form': WeeklyBusinessRateAlertsForm()}
    if request.method == 'POST':
        form = WeeklyBusinessRateAlertsForm(request.POST)
        if form.is_valid():
            best_buy_table_emails = form.save()
            if 'referer' in request.session:
                referer = Referrer.objects.get(pk=request.session['referer']).name
            else:
                referer = '(Direct)'
            analytics.delay('event', 'Recurring Business Best Buy Emails', 'Signup', referer)
            create_profile_output = create_stage_one_profile(request=request, email=best_buy_table_emails.email,
                                                             source='recurring_business_best_buy_emails',
                                                             send_activation=False, login_user=False)
            if isinstance(create_profile_output, tuple):
                user, user_created, record_stats = create_profile_output
            else:
                return create_profile_output
            record_referral_signup(request=request, user=user, user_created=user_created, action='signup')
            context['weekly_signed_up'] = True
            if best_buy_table_emails.frequency == 1:
                update_subscription_on_email_service.delay(best_buy_table_emails.email, interest_group=u'Daily Business Best Buy Tables')
                record_referral_signup(request=request, user=user, user_created=user_created,
                                       action='recurring_business_daily_best_buys')
            if best_buy_table_emails.frequency == 2:
                update_subscription_on_email_service.delay(best_buy_table_emails.email, interest_group=u'Weekly Business Best Buy Tables')
                record_referral_signup(request=request, user=user, user_created=user_created,
                                       action='recurring_business_weekly_best_buys')
            if best_buy_table_emails.frequency == 3:
                update_subscription_on_email_service.delay(best_buy_table_emails.email, interest_group=u'Monthly Business Best Buy Tables')
                record_referral_signup(request=request, user=user, user_created=user_created,
                                       action='recurring_business_monthly_best_buys')
    return render(request, 'products/topaccounts/business_reccuring_emails.html', context)


def outbound_clickthrough(request, product_id):
    product = get_object_or_404(MasterProduct, pk=product_id)
    referer = None
    if request.session.get('referer', None) is not None:
        referer = Referrer.objects.get(pk=request.session.get('referer'))
    if referer is None:
        referer_name = "(Direct)"
    else:
        referer_name = referer.name
    analytics.delay('event', 'Product Outbound', "%s - %s" % (product.provider.title, product.title), referer_name)
    return HttpResponseRedirect(product.url)


def ratetracker_threshold_amount(request, context=None):
    if context is None:
        context = {}

    if request.method == 'POST':
        form = RateTrackerThresholdForm(request.POST)
        if form.is_valid():
            profile = request.user.profile
            profile.ratetracker_threshold = form.cleaned_data['amount']
            profile.ratetracker_threshold_set = True
            profile.save()
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'failed', 'reason': 'Form did not validate'})
    else:
        return JsonResponse({'status': 'failed', 'reason': 'Need to be called via POST'})

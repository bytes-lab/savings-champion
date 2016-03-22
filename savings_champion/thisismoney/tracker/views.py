import datetime
import time
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from common.accounts.utils import MakeUsername
from common.decorators import render_to
from thisismoney.forms import PortfolioFormset, ReminderFormset, TIMRateTrackerForm, RateTrackerForm, \
    ProductReminderForm, TIMFixedRegistrationForm
from products.models import Product, ProductPortfolio, RatetrackerReminder, BestBuy, Provider
from products.forms import ReminderEditForm, PortfolioEditForm
from common.accounts.forms import SCRegistrationForm
from products.utils import get_ISA_bestbuys
from thisismoney.models import TiMSignups
from common.models import UUIDNext
from products.utils import cleaned_data_to_params
import constants


SEARCH = 'search'
TRACK = 'track_me'


def _get_success_view(is_isa):
    if is_isa:
        return 'isa_tracker'
    return 'timrate_tracker'


@csrf_exempt
@render_to()
def tracker(request, is_isa=False, form_class=TIMRateTrackerForm,
            template_file='thisismoney/ratetracker/wizard.html'):
    """
    
    """
    empty_values = ['', ' ', None, 0]
    context = _init_context(is_isa)

    success_view = _get_success_view(is_isa)

    if request.method == 'POST':
        if SEARCH in request.POST.keys():
            # The wizard forks depending on which product type was selected, we need to check what 
            # was in the request keys
            form = form_class(request.POST)

            if form.is_valid():

                # bog standard searching 
                if not form.set_reminder:
                    request.session[constants.RESULTS] = constants.RT_RESULTS
                    form_email = form.cleaned_data.get('email')
                    # if the form is valid we want to then display the results.html 
                    template_file = 'thisismoney/ratetracker/results.html' if not is_isa else 'thisismoney/isatracker/isa_results.html'

                    selected_product = get_object_or_404(Product, pk=form.cleaned_data.get('product'))

                    context['selected_product'] = selected_product

                    bestbuy = BestBuy.objects.get(pk=form.cleaned_data.get('account_type'))
                    context['bestbuy_type'] = bestbuy
                    # set up the Product Form to Track this product 
                    initial = {'provider': selected_product.provider,
                               'account_type': form.cleaned_data.get('account_type'),
                               'product': selected_product,
                               'balance': form.cleaned_data.get('balance'),
                               'notice': selected_product.notice,
                               'bonus_term': selected_product.bonus_term,
                    }
                    #set up the registration form
                    initialDetails = {'username': form.cleaned_data.get('email'),
                                      'email': form.cleaned_data.get('email'),
                                      'email2': form.cleaned_data.get('email'),
                                      'password2': 'doesnotmatterjustneededforformisvalid',
                                      'salutation': 'Mr',
                                      'source': 'This is Money',
                                      'uuid': create_uid_next(form),
                    }

                    if selected_product.bonus_term not in empty_values:  # wtf this is a float?
                        initial['bonus_term'] = selected_product.bonus_term

                    context['track_product_form'] = ProductReminderForm(initial=initial)
                    context['register_form'] = SCRegistrationForm(initial=initialDetails)

                    product_rate = selected_product.get_rate(datetime.datetime.now().date())
                    context['rate'] = product_rate
                    #store user in TiMSignups
                    new_signup = TiMSignups(email=form.cleaned_data.get('email'), completed_signup=False)
                    if not TiMSignups.objects.filter(email=form.cleaned_data.get('email')).exists():
                        new_signup.save()

                    filters = {'%s__gte' % Product.get_ordering(bestbuy.slug): 1}

                    products = Product.objects.filter(bestbuy_type__pk=form.cleaned_data.get('account_type')) \
                        .filter(**filters).order_by(Product.get_ordering(bestbuy.slug)) \
                        .filter(minimum__lte=form.cleaned_data.get('balance'))

                    if 'variable-rate-isa' in bestbuy.slug:
                        products = products.filter(is_isa_transfers_in=True)

                    try:
                        your_interest_balance = form.cleaned_data.get('balance') * (product_rate / 100)
                    except:
                        your_interest_balance = 0

                    if products and len(products) > 0:
                        context['suggested_product'] = products[0]
                        suggested_interest_balance = form.cleaned_data.get('balance') * (products[0].gross_rate / 100)
                        context['suggested_interest_amount'] = suggested_interest_balance + form.cleaned_data.get(
                            'balance')
                        context['extra_interest'] = suggested_interest_balance - your_interest_balance

                    context['your_interest_amount'] = your_interest_balance + form.cleaned_data.get('balance')

                else:
                    # form is valid so we copy straight across from one to another
                    # TODO now needs to check if they are logged in
                    if not request.user.is_authenticated():

                        context = RequestContext(request)
                        new_signup = TiMSignups(email=form.cleaned_data.get('email'), completed_signup=False)
                        if not TiMSignups.objects.filter(email=form.cleaned_data.get('email')).exists():
                            new_signup.save()

                        data = {'username': MakeUsername(),
                                'provider': form.cleaned_data.get('provider'),
                                'account_type': form.cleaned_data.get('account_type'),
                                'balance': form.cleaned_data.get('balance'),
                                'maturity_date': form.cleaned_data.get('maturity_date'),
                                'email': form.cleaned_data.get('email'),
                                'source': 'This is Money'}

                        context['form'] = TIMFixedRegistrationForm(initial=data)
                        template_file = 'thisismoney/registration_form.html'
                        return render_to_response(template_file, context)
                    else:
                        return HttpResponseRedirect(redirect_to=reverse('home'))

        else:
            form = form_class()
    else:
        form = form_class()

    context.update({'TEMPLATE': template_file, 'ratetracker_form': form})
    return context


@render_to()
def portfolio(request, is_isa=False, template_file='thisismoney/ratetracker/portfolio.html'):
    """
    Products are no longer deleted but flagged as deleted as we need to sync this across
    to a third party service. If some of the details have changed then we need to make sure that the sync information is 
    updated to the third party, which requires us to unset the is_synched status.
    """
    # 
    import datetime

    product_formset = None
    reminder_formset = None
    product_total = None
    reminder_total = None
    grand_total = None
    todays_date = datetime.datetime.now()
    context = _init_context(is_isa)

    if request.method == 'POST':
        product_formset = PortfolioFormset(request.POST, prefix='trackers')
        reminder_formset = ReminderFormset(request.POST, prefix='reminders')

        if product_formset.is_valid():
            product_formset.save()

        if reminder_formset.is_valid():
            reminder_formset.save()

        return HttpResponseRedirect('%s?updated=%s' % (reverse(_get_success_view(is_isa)), time.time()))

    else:
        if request.user.is_authenticated():
            product_formset = PortfolioFormset(queryset=_get_portfolio_queryset(is_isa, request.user),
                                               prefix='trackers')

            product_total = _get_portfolio_total(is_isa, request.user)

            reminder_formset = ReminderFormset(queryset=_get_reminder_queryset(is_isa, request.user),
                                               prefix='reminders')

            reminder_total = _get_reminder_total(is_isa, request.user)

            grand_total = product_total + reminder_total

    context['date'] = todays_date.strftime("%Y-%m-%d")
    context['product_formset'] = product_formset
    context['reminder_formset'] = reminder_formset
    context['product_total'] = product_total
    context['reminder_total'] = reminder_total
    context['grand_total'] = grand_total
    context['edit_form'] = PortfolioEditForm()
    context['reminder_edit'] = ReminderEditForm()
    context.update({'TEMPLATE': template_file})
    return context


def _init_context(is_isa):
    context = {constants.SECTION: constants.RATETRACKER if is_isa is False else constants.ISATRACKER,
               constants.RATETRACKER_TYPE: constants.RATE if is_isa is False else constants.ISA}
    return context


def _get_portfolio_queryset(is_isa, user):
    queryset = ProductPortfolio.objects.filter(is_deleted=False,
                                               user=user)
    if is_isa:
        queryset = queryset.filter(account_type__pk__in=get_ISA_bestbuys())
    return queryset


def _get_portfolio_total(is_isa, user):
    total = 0
    queryset = ProductPortfolio.objects.filter(is_deleted=False, user=user)

    for balance in queryset:
        total += balance.balance
    return total


def create_redirect_url(uid_next):
    return '?next=%s' % reverse('redirector', args=[uid_next])


def _get_reminder_queryset(is_isa, user):
    queryset = RatetrackerReminder.objects.filter(is_deleted=False,
                                                  user=user)
    if is_isa:
        queryset = queryset.filter(account_type__pk__in=get_ISA_bestbuys())
    return queryset


def _get_reminder_total(is_isa, user):
    total = 0
    queryset = RatetrackerReminder.objects.filter(is_deleted=False, user=user)

    for balance in queryset:
        total += balance.balance
    return total


def _make_product_reminder(cleaned_data, request):
    portfolio = ProductPortfolio()
    product = cleaned_data.get('product')
    if type(product) != type(Product()):
        product = Product.objects.get(pk=cleaned_data.get('product'))

    portfolio.master_product = product.master_product
    portfolio.provider = product.provider
    bestbuy = cleaned_data.get('account_type')
    if type(bestbuy) != type(BestBuy()):
        bestbuy = BestBuy.objects.get(pk=cleaned_data.get('account_type'))
    portfolio.account_type = bestbuy
    portfolio.user = request.user
    portfolio.balance = cleaned_data.get('balance')
    opening_date = cleaned_data.get('opening_date', None)
    if opening_date:
        portfolio.opening_date = opening_date

    portfolio.bonus_term = product.bonus_term
    portfolio.notice = product.notice
    portfolio.is_synched = False
    portfolio.save()


def _make_reminder(cleaned_data, request):
    reminder = RatetrackerReminder()
    provider = cleaned_data.get('provider')
    if type(provider) != type(Provider()):
        provider = Provider.objects.get(pk=cleaned_data.get('provider'))

    reminder.provider = provider
    reminder.maturity_date = cleaned_data.get('maturity_date')
    reminder.account_type = BestBuy.objects.get(pk=cleaned_data.get('account_type'))
    reminder.balance = cleaned_data.get('balance')
    reminder.user = request.user
    reminder.save()


def _make_uid():
    import uuid

    return str(uuid.uuid1())


def create_uid(form):
    uidnext = UUIDNext()
    uidnext.uuid = _make_uid()
    uidnext.params = cleaned_data_to_params(form.cleaned_data)
    opening_date = form.cleaned_data.get('opening_date', None)
    if opening_date:
        uidnext.next = reverse('timopening_date_rate_check_complete')
    else:
        uidnext.next = reverse('timrate_check_complete')
    uidnext.save()
    return uidnext


def create_uid_next(form):
    return create_uid(form).uuid


def rate_check_complete(request, is_isa=False, form_class=RateTrackerForm):
    """
    Products are no longer deleted but flagged as deleted as we need to sync this across
    to a third party service
    """
    EMPTY_VALUES = ['', ' ', None]
    form = form_class(request.GET)

    if form.is_valid():
        if form.cleaned_data.get('maturity_date', None) not in EMPTY_VALUES:
            _make_reminder(form.cleaned_data, request)
        else:
            _make_product_reminder(form.cleaned_data, request)

        return HttpResponseRedirect('%s?updated=%s' % (reverse('timrate_tracker'), time.time()))

    return HttpResponseRedirect(reverse('home'))


@render_to()
def help_page(request, is_isa=False, section=None, block_key='rate_check.help',
              template_file='pages/page_block_page.html'):
    return {'TEMPLATE': template_file, 'block_key': block_key, 'section': section}

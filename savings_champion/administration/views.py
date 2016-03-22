from itertools import chain
import json
from datetime import datetime, timedelta
from decimal import Decimal
from allauth.account.utils import send_email_confirmation
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import permission_required, login_required, user_passes_test
from django.db.models import Sum
from django.forms import modelformset_factory
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.shortcuts import render_to_response, render, get_object_or_404
from django.template import RequestContext
from django.conf import settings
from django.views.decorators.cache import never_cache
from django.core.cache import cache
from django.shortcuts import redirect
from administration.forms import sccodeForm, UnsubscribeForm, RemoveUserForm, SyncUserForm, ReferrerForm, \
    RemoveConciergeClientForm
from common.tasks import delete_user_profile
from common.utils import record_referral_signup
from concierge.forms import DateFilterForm
from products.forms import PortfolioEditForm
from products.forms import ReminderEditForm
from products.forms import AddOpeningDateForm
from products.forms import RateTrackerThresholdForm
from products.models import Product, ProductPortfolio, RatetrackerReminder, BestBuy, Ranking, Provider, ProductTier
from pages.models import ArticleComment, BlogComment
from administration.forms import AddFixedProductForm, AddProductsForm, EmailForm, BestBuyAddForm, ChangePortfolioForm, \
    ChangeEmailForm, ConciergeForm, ChangePasswordForm
from common.models import Profile, CampaignsSignup, NewsletterSignup, Referrer, UserReferral
from common.accounts.utils import MakeUsername
from products.tasks import sync_ratetracker_portfolio, sync_ratetracker_reminder
import memcache

from rate_tracker.tasks import check_client_portfolios_for_issues
from tasks import async_update_products_from_salesforce

User = get_user_model()


def date_filtering(form):
    month_ago = datetime.now() - timedelta(weeks=4)
    today = datetime.now() + timedelta(days=1)
    try:
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']
    except AttributeError:
        start_date = month_ago
        end_date = today
        return start_date, end_date
    if start_date is None and start_date != '':
        start_date = month_ago
    if end_date is None and end_date != '':
        end_date = today
    return start_date, end_date


def portfolio_sort(portfolio_object):
    return portfolio_object.get_personal_rating


@never_cache
@login_required
@user_passes_test(lambda u: u.is_staff)
def index(request):
    return TemplateResponse(request, 'index.html')


@login_required
@permission_required('user.is_staff')
@permission_required('user.change_sccode')
def change_sccode_initial(request):
    context = {'sccodeform': sccodeForm()}

    if request.method == 'POST':
        requestsccode = request.POST['sccode']
        data = {'sccode': '', 'oldsccode': requestsccode}
        context['sccodeform'] = sccodeForm(initial=data)
        scProduct = ProductTier.objects.get(sc_code=request.POST['sccode'])

        portfolioList = ProductPortfolio.objects.filter(master_product=scProduct.product)

        context['portfolioList'] = portfolioList

        return render_to_response('updatesccode/portfoliolist.html',
                                  context,
                                  context_instance=RequestContext(request))

    return render_to_response('updatesccode/step1.html',
                              context,
                              context_instance=RequestContext(request))


@login_required
@permission_required('user.is_staff')
@permission_required('user.change_sccode')
def change_sccode_process(request):
    context = {}
    if request.method == 'POST':
        oldscProduct = ProductTier.objects.get(sc_code=request.POST['oldsccode'])
        newscProduct = ProductTier.objects.get(sc_code=request.POST['sccode'])
        portfolioList = ProductPortfolio.objects.filter(master_product=oldscProduct.product)

        for portfolio in portfolioList:
            portfolio.master_product = newscProduct.product
            portfolio.provider = newscProduct.product.provider
            portfolio.is_synched = False
            portfolio.save()

        context['portfolioList'] = portfolioList

        return render_to_response('updatesccode/success.html',
                                  context,
                                  context_instance=RequestContext(request))


@never_cache
@login_required
@permission_required('user.is_staff')
def memcached_status(request):
    cachesettings = settings.CACHES

    # get first memcached URI
    if 'default' in cachesettings and 'LOCATION' in cachesettings:

        host = memcache._Host(cachesettings['default']['LOCATION'])
        host.connect()
        host.send_cmd("stats")

        class Stats:
            def __init__(self):
                pass

        stats = Stats()

        while 1:
            line = host.readline().split(None, 2)
            if line[0] == "END":
                break
            _, key, value = line
            try:
                # convert to native type, if possible
                value = int(value)
                if key == "uptime":
                    value = timedelta(seconds=value)
                elif key == "time":
                    value = datetime.fromtimestamp(value)
            except ValueError:
                pass
            setattr(stats, key, value)

        host.close_socket()

        return render_to_response(
            'memcached/memcached_status.html', dict(
                stats=stats,
                hit_rate=100 * stats.get_hits / stats.cmd_get,
                miss_rate=100 * stats.get_misses / stats.cmd_get,
                time=datetime.now(),  # server time
            ))


@login_required
@permission_required('user.is_staff')
@never_cache
def clear_cache(request):
    cache.clear()
    messages.success(request, 'Cache Cleared')
    return redirect('admininstrationindex')


@login_required
@permission_required('user.is_staff')
@permission_required('user.change_comment')
def approve_comment(request, template_file="administration/approvecomments/approved.html"):
    article = request.GET.get('article', None)
    id = request.GET.get('id', None)
    context = {}
    if article:
        comment = ArticleComment.objects.get(id=id)
    else:
        comment = BlogComment.objects.get(id=id)
    comment.approved = True
    comment.save()

    return render_to_response(template_file,
                              context,
                              context_instance=RequestContext(request))


@login_required
@permission_required('user.is_staff')
@permission_required('user.add_product')
def add_new_product_for_customer(request, template_file="administration/add_products/add.html"):
    context = RequestContext(request)

    context['form'] = AddProductsForm()
    context['fixed_product_form'] = AddFixedProductForm()

    return render_to_response(template_file,
                              context_instance=context)


@login_required
@permission_required('user.is_staff')
@permission_required('user.add_product')
@never_cache
def add_product_for_customer_logic(request, template_file="administration/add_products/addsuccess.html"):
    context = RequestContext(request)
    fixed = request.GET.get('fixed', None)
    if request.method == 'POST':
        if fixed:
            form = AddFixedProductForm(request.POST)
            if form.is_valid():
                try:
                    user = User.objects.get(is_active=True, email__iexact=form.cleaned_data.get('email'))
                except User.DoesNotExist:
                    if User.objects.filter(email__iexact=form.cleaned_data.get('email')).exists():
                        messages.error(request, 'User is not activated.')
                    else:
                        messages.error(request, 'User does not exist with this email.')
                    return redirect('admininstrationindex')
                except User.MultipleObjectsReturned:
                    messages.error(request, 'Multiple users were found for this email address.')
                    return redirect('admininstrationindex')

                reminder = RatetrackerReminder()
                reminder.user = user

                reminder.provider = form.cleaned_data.get('fixed_provider')

                account_type = BestBuy.objects.get(id=form.cleaned_data.get('account_type'))
                reminder.account_type = account_type

                reminder.balance = form.cleaned_data.get('balance')

                reminder.maturity_date = form.cleaned_data.get('maturity_date')

                reminder.is_synched = False
                reminder.save()

                return redirect('add_customer_product_logic')
        else:
            form = AddProductsForm(request.POST)
            if form.is_valid():
                try:
                    user = User.objects.get(is_active=True, email__iexact=form.cleaned_data.get('email'))
                except User.DoesNotExist:
                    messages.error(request, 'User does not exist with this email.')
                    return redirect('admininstrationindex')
                except User.MultipleObjectsReturned:
                    messages.error(request, 'Multiple users were found for this email address.')
                    return redirect('admininstrationindex')
                product = Product.objects.get(pk=form.cleaned_data.get('product'))

                portfolio = ProductPortfolio()
                portfolio.user = user

                portfolio.account_type = BestBuy.objects.get(id=product.bestbuy_type.all()[0].id)
                portfolio.balance = form.cleaned_data.get('balance')
                portfolio.master_product = product.master_product
                portfolio.provider = product.provider

                # When making I found some bonus terms can be entered as '' as well as None
                # hence the ugly if statement to ensure it is an int
                # as it only gets evaluated on portfolio.save() which by then a typeerror
                # try/except is too late as it could be any field

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

                return redirect('add_customer_product_logic')

    return render_to_response(template_file,
                              context_instance=context)


@login_required
@permission_required('user.is_staff')
@never_cache
def view_customer_portfolio(request, context=None):
    if context is None:
        context = {}
    if request.method == "POST":
        form = EmailForm(request.POST)
        if form.is_valid():
            try:
                user = User.objects.get(email__iexact=form.cleaned_data.get('email'))
            except User.DoesNotExist:
                messages.error(request, 'User does not exist with this email.')
                return redirect('admininstrationindex')
            except User.MultipleObjectsReturned:
                messages.error(request, 'Multiple users were found for this email address.')
                return redirect('admininstrationindex')

            portfolio = ProductPortfolio.objects.filter(user=user, is_deleted=False).select_related('master_product', 'master_product__provider').prefetch_related('master_product__producttier_set')
            reminders = RatetrackerReminder.objects.filter(user=user, is_deleted=False)
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
            context['concierge'] = CampaignsSignup.objects.filter(email=user.email).exists()
            context['form'] = AddProductsForm()
            context['edit_form'] = PortfolioEditForm()
            context['reminder_edit'] = ReminderEditForm()
            context['fixed_product_form'] = AddFixedProductForm()
            context['opening_date_form'] = AddOpeningDateForm()
            context['threshold_form'] = RateTrackerThresholdForm(
                initial={'amount': user.profile.ratetracker_threshold})
            return render(request, "products/healthcheck/healthcheck_portfolio.html", context)

    context['form'] = EmailForm()
    return render(request, "administration/view/portfolio_form.html", context)


@login_required
@permission_required('user.is_staff')
def check_user_status(request, template_file="administration/userstatus/status.html"):
    context = RequestContext(request)

    if request.method == "POST":
        form = EmailForm(request.POST)
        if form.is_valid():
            try:
                user = User.objects.get(email__iexact=form.cleaned_data.get('email'))
                try:
                    profile = user.profile
                except Profile.DoesNotExist:
                    profile = Profile(user=user)
                    profile.save()
                except Profile.MultipleObjectsReturned:
                    profiles = Profile.objects.filter(user=user)
                    profile = profiles[0]

                if profile.skeleton_user:
                    context[
                        'status'] = "This user hasn't signed up to rate tracker yet, but has signed up for a reminder/instructions email, the newsletter, rate alerts or the concierge service"
                elif not profile.filled_in_name:
                    context['status'] = "This user never finished filling in their name on the initial signup"
                elif not user.is_active:
                    context['status'] = "This user is inactive"
                else:
                    context['status'] = "User has signed up, probably has forgotten their password..."
            except User.DoesNotExist:
                context['status'] = "user doesn't exist"
    else:
        context['form'] = EmailForm()

    return render_to_response(template_file, context_instance=context)


@login_required
@permission_required('user.is_staff')
def get_ip_address_count(request, template_file="administration/ip_list/list.html"):
    context = RequestContext(request)

    profiles = Profile.objects.all()
    ip_dict = {}
    for profile in profiles:
        if profile.ip_address:
            ip_dict[profile.ip_address] = ip_dict.get(profile.ip_address, 0) + 1

    context['ip_dict'] = ip_dict
    return render_to_response(template_file, context_instance=context)


@login_required
@permission_required('user.is_staff')
def get_ip_address_emails(request, template_file="administration/ip_list/email_list.html"):
    context = RequestContext(request)
    ip_address = request.GET.get('ip_address', None)
    context['profiles'] = Profile.objects.filter(ip_address=ip_address)
    return render_to_response(template_file, context_instance=context)


@login_required
@permission_required('user.is_staff')
@permission_required('user.add_bestbuy')
def manual_bestbuy_add(request):
    context = RequestContext(request)
    BestBuyFormset = modelformset_factory(Ranking, form=BestBuyAddForm, extra=1, can_delete=True)
    personal_formset = BestBuyFormset(queryset=Ranking.objects.filter(date_replaced=None, bestbuy__client_type='p'), prefix='personal')
    business_formset = BestBuyFormset(queryset=Ranking.objects.filter(date_replaced=None, bestbuy__client_type='b'), prefix='business')
    charity_formset = BestBuyFormset(queryset=Ranking.objects.filter(date_replaced=None, bestbuy__client_type='c'), prefix='charity')

    if request.method == "POST":
        Ranking.replace()
        personal_formset = BestBuyFormset(request.POST, queryset=Ranking.objects.filter(date_replaced=None, bestbuy__client_type='p'), prefix='personal')
        business_formset = BestBuyFormset(request.POST, queryset=Ranking.objects.filter(date_replaced=None, bestbuy__client_type='b'), prefix='business')
        charity_formset = BestBuyFormset(request.POST, queryset=Ranking.objects.filter(date_replaced=None, bestbuy__client_type='c'), prefix='charity')
        if personal_formset.is_valid():
            personal_formset.save()
        if business_formset.is_valid():
            business_formset.save()
        if charity_formset.is_valid():
            charity_formset.save()
        if personal_formset.is_valid() and business_formset.is_valid() and charity_formset.is_valid():
            return redirect('manual_bestbuy_add')
    context['personal_formset'] = personal_formset
    context['business_formset'] = business_formset
    context['charity_formset'] = charity_formset
    return render_to_response("administration/bestbuys/add.html", context_instance=context)


@login_required
@permission_required('user.is_staff')
def fscs_test(request, template_file="administration/fscs/index.html"):
    context = RequestContext(request)
    context['providers'] = Provider.objects.all()
    return render_to_response(template_file, context_instance=context)


@login_required
@permission_required('user.is_staff')
@permission_required('user.change_user_activation')
def resend_user_activation(request, template_file="administration/resend_activation/index.html"):
    context = RequestContext(request)

    if request.method == "POST":
        form = EmailForm(request.POST)
        if form.is_valid():
            try:
                user = User.objects.get(email__iexact=form.cleaned_data.get('email'))
                if not user.is_active:
                    try:
                        profile = user.profile
                    except Profile.DoesNotExist:
                        profile = Profile(user=user)
                        profile.save()
                    except Profile.MultipleObjectsReturned:
                        profiles = Profile.objects.filter(user=user)
                        profile = profiles[0]
                    if not profile.skeleton_user:
                        send_email_confirmation(request, user)
                        context['message'] = "Activation email has been resent to %s" % user.email
                    else:
                        context['message'] = "This user hasn't signed up for ratetracker"
                else:
                    context[
                        'message'] = "This user has already activated, they should probably use the password reset bit on the login page!"
            except User.DoesNotExist:
                context['message'] = "User doesn't exist!"
    else:
        context['form'] = EmailForm()
    return render_to_response(template_file, context_instance=context)


@login_required
@permission_required('user.is_staff')
@permission_required('user.change_user_portfolios')
def change_user_portfolios(request, template_file="administration/change_user_portfolios/index.html"):
    context = RequestContext(request)
    context['emailform'] = EmailForm()
    if request.method == "POST":
        form = EmailForm(request.POST)
        if form.is_valid():
            user = User.objects.filter(email__iexact=form.cleaned_data.get('email'))
            if user.count() > 1 and user.filter(is_active=True).count() > 0:
                user = user.filter(is_active=True)
            context['portfolios'] = ProductPortfolio.objects.filter(user__in=user, is_deleted=False)
            context['portfolioform'] = ChangePortfolioForm()
            context['emailform'] = False

    return render_to_response(template_file, context_instance=context)


@login_required
@permission_required('user.is_staff')
@permission_required('user.change_user_portfolios')
def change_user_portfolios_logic(request, template_file="administration/change_user_portfolios/updated.html"):
    context = RequestContext(request)
    if request.method == "POST":
        form = ChangePortfolioForm(request.POST)
        if form.is_valid():
            oldportfolio = ProductPortfolio.objects.get(id=form.cleaned_data.get('id'))
            portfolio = ProductPortfolio.objects.get(id=form.cleaned_data.get('id'))
            context['oldportfolio'] = oldportfolio
            new_sc_code = str(form.cleaned_data.get('new_sc_code')).upper()  # SC code needs to be upper case
            newProduct = Product.objects.get(sc_code=new_sc_code)
            opening_date = form.cleaned_data.get('opening_date')

            portfolio.master_product = newProduct.master_product
            portfolio.provider = newProduct.provider

            if opening_date:
                portfolio.opening_date = opening_date
            portfolio.is_synched = False
            portfolio.save()

            context['newportfolio'] = portfolio

    return render_to_response(template_file, context_instance=context)


@login_required
@permission_required('user.is_staff')
@permission_required('user.change_user_email')
def change_user_email(request, template_file="administration/change_email/index.html"):
    context = RequestContext(request)

    if request.method == "POST":
        form = ChangeEmailForm(request.POST)
        if form.is_valid():
            try:
                user = User.objects.get(email__iexact=form.cleaned_data.get('old_email'))
            except User.DoesNotExist:
                messages.error(request, 'User does not exist with this email.')
                return redirect('admininstrationindex')
            except User.MultipleObjectsReturned:
                messages.error(request, 'Multiple users were found for this email address.')
                return redirect('admininstrationindex')

            user.email = form.cleaned_data.get('new_email')
            user.save()
            try:
                profile = user.profile
            except Profile.DoesNotExist:
                profile = Profile(user=user)
                profile.save()
            except Profile.MultipleObjectsReturned:
                profiles = Profile.objects.filter(user=user)
                profile = profiles[0]
            profile.is_synched = False
            profile.save()
        else:
            context['form'] = form
    else:
        context['form'] = ChangeEmailForm()
    return render_to_response(template_file, context_instance=context)


@login_required
@permission_required('user.is_staff')
@permission_required('user.add_concierge_client')
def create_concierge_client(request, template_file="administration/concierge_creation/index.html"):
    context = RequestContext(request)

    if request.method == "POST":
        form = ConciergeForm(request.POST)
        if form.is_valid():
            form_email = form.cleaned_data.get('email')
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            number = form.cleaned_data.get('number')
            try:
                user = User.objects.get(email__iexact=form_email)
                try:
                    profile = user.profile
                except Profile.DoesNotExist:
                    profile = Profile(user=user)
                    profile.save()
                except Profile.MultipleObjectsReturned:
                    profiles = Profile.objects.filter(user=user)
                    profile = profiles[0]

                user.first_name = first_name
                user.last_name = last_name
                user.is_active = True
                user.save()

                profile.telephone = number
                profile.is_synched = False
                profile.skeleton_user = False
                profile.filled_in_name = True
                profile.save()

                try:
                    campaign_signup = CampaignsSignup.objects.get(email__iexact=form_email)
                except CampaignsSignup.DoesNotExist:
                    campaign_signup = CampaignsSignup(email=form_email)

                campaign_signup.name = " ".join([first_name, last_name])
                campaign_signup.telephone = number
                campaign_signup.is_client = True
                campaign_signup.is_synched = False
                campaign_signup.save()

            except User.DoesNotExist:
                try:
                    campaign_signup = CampaignsSignup.objects.get(email__iexact=form_email)
                except CampaignsSignup.DoesNotExist:
                    campaign_signup = CampaignsSignup()
                    campaign_signup.email = form_email
                campaign_signup.name = " ".join([first_name, last_name])
                campaign_signup.telephone = number
                campaign_signup.is_client = True
                campaign_signup.is_synched = False
                campaign_signup.save()

                user = User()
                user.is_active = True
                user.first_name = first_name
                user.last_name = last_name
                user.email = form_email
                user.username = MakeUsername()

                # This should be removed once messaging the client is brought in house
                user.skeleton_user = True   # Set to stop concierge clients getting emails about rate tracker.

                user.save()

                profile = Profile()
                profile.user = user
                profile.telephone = number
                profile.skeleton_user = False
                profile.filled_in_name = True
                profile.is_synched = False
                profile.save()
            context[
                'message'] = "%s has now been changed to a concierge client, this will be reflected in Salesforce over the next 2-3mins" % user.email
            record_referral_signup(request, user, True, 'concierge_client', third_party=True)
        else:
            context['form'] = form
    else:
        context['form'] = ConciergeForm()
    return render_to_response(template_file, context_instance=context)


@login_required
@permission_required('user.is_staff')
@permission_required('user.remove_concierge_client')
def remove_concierge_client(request, context=None):
    if context is None:
        context = {}
    form = RemoveConciergeClientForm()
    if request.method == "POST":
        form = RemoveConciergeClientForm(request.POST)
        if form.is_valid():
            form_email = form.cleaned_data.get('email')
            user = User.objects.get(email__iexact=form_email)
            campaign_signup = get_object_or_404(CampaignsSignup, email__iexact=form_email)
            campaign_signup.is_client = False
            campaign_signup.is_synched = False
            campaign_signup.save()
            user.profile.is_synched = False
            user.profile.save()
            context['message'] = "%s has now been changed to a regular user, this will be reflected in Salesforce " \
                                 "over the next 2-3mins" % user.email
            return render(request, "administration/concierge_removal/index.html", context)
    context['form'] = form
    return render(request, "administration/concierge_removal/index.html", context)

@login_required
@permission_required('user.is_staff')
@permission_required('user.change_user_password')
def change_user_password(request, template_file="administration/change_password/index.html"):
    context = RequestContext(request)

    if request.method == "POST":
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            try:
                user = User.objects.get(email__iexact=form.cleaned_data.get('email'))
            except User.DoesNotExist:
                messages.error(request, 'User does not exist with this email.')
                return redirect('admininstrationindex')
            except User.MultipleObjectsReturned:
                messages.error(request, 'Multiple users were found for this email address.')
                return redirect('admininstrationindex')

            new_password = form.cleaned_data.get('new_password')
            active = form.cleaned_data.get('active')

            user.set_password(new_password)
            if active:
                user.is_active = True
                try:
                    profile = user.profile
                except Profile.DoesNotExist:
                    profile = Profile(user=user)
                    profile.save()
                except Profile.MultipleObjectsReturned:
                    profiles = Profile.objects.filter(user=user)
                    profile = profiles[0]
                profile.is_synched = False
                profile.save()
            user.save()
            context['message'] = "The password for %s has been changed" % user.email
        else:
            context['form'] = form
    else:
        context['form'] = ChangePasswordForm()
    return render_to_response(template_file, context_instance=context)


@login_required
@permission_required('user.is_staff')
def duplicate_user_listing(request):
    users = User.objects.all()
    taken_emails = []
    duplicate_users = []
    for user in users:
        if user.email in taken_emails:
            duplicate_users.append(user)
        else:
            taken_emails.append(user.email)

    if len(duplicate_users) > 0:
        return render(request, 'administration/duplicate_users/index.html', {'duplicate_users': duplicate_users})


@login_required
@permission_required('user.is_staff')
@permission_required('user.change_user_subscriptions')
def unsubscribe_user(request):
    unsubscribe_form = UnsubscribeForm()
    if request.method == 'POST':
        unsubscribe_form = UnsubscribeForm(request.POST)
        if unsubscribe_form.is_valid():
            if CampaignsSignup.objects.filter(email__iexact=unsubscribe_form.email).exists():
                CampaignsSignup.objects.filter(email__iexact=unsubscribe_form.email).delete()
                messages.success(request, 'Removed all instances of %s from CampaignSignup.' % unsubscribe_form.email)
            else:
                messages.info(request, 'No instances of %s found for CampaignSignup.' % unsubscribe_form.email)

            if NewsletterSignup.objects.filter(email__iexact=unsubscribe_form.email).exists():
                NewsletterSignup.objects.filter(email__iexact=unsubscribe_form.email).delete()
                messages.success(request, 'Removed all instances of %s from NewsletterSignup.' % unsubscribe_form.email)
            else:
                messages.info(request, 'No instances of %s found for NewsletterSignup.' % unsubscribe_form.email)

    return render(request, 'administration/unsubscribe_user/form.html', {'form': unsubscribe_form})


@login_required
@permission_required('user.is_staff')
@permission_required('user.delete_user')
def remove_user(request):
    form = RemoveUserForm()
    if request.method == 'POST':
        form = RemoveUserForm(request.POST)
        if form.is_valid():
            user = User.objects.get(email=form.cleaned_data['email'])
            user.is_active = False
            user.save()
            delete_user_profile.apply_async((user.pk,), countdown=1)
            messages.info(request, 'User is being removed in the background.')
            return redirect('admininstrationindex')

    return render(request, 'administration/remove_user/remove_user.html', {'form': form})


@login_required
@permission_required('user.is_staff')
@permission_required('user.change_users_sync')
def force_sync_user(request):
    form = SyncUserForm()
    if request.method == 'POST':
        form = SyncUserForm(request.POST)
        if form.is_valid():
            user = User.objects.get(email=form.cleaned_data['email'])
            portfolio = ProductPortfolio.objects.filter(user=user)
            for product in portfolio:
                sync_ratetracker_portfolio.apply_async((product.pk,))
            reminders = RatetrackerReminder.objects.filter(user=user)
            for reminder in reminders:
                sync_ratetracker_reminder.apply_async((reminder.pk,))
            messages.info(request, 'User %s is now being resynced' % user.email)
    return render(request, 'administration/sync_user/sync_user.html', {'form': form})


@login_required
@permission_required('user.is_staff')
def user_breakdown(request, context=None):
    if context is None:
        context = {}

    end_date = datetime.today().date() - timedelta(days=1)
    start_date = datetime.today().date() - timedelta(days=8)
    context['form'] = DateFilterForm(initial={'start_date': start_date, 'end_date': end_date})
    context['total_users'] = User.objects.all()
    context['users_by_range'] = User.objects.filter(date_joined__lte=end_date,
                                                    date_joined__gte=start_date)

    return render(request, 'administration/user_breakdown/user_breakdown.html', context)


@login_required
@permission_required('user.is_staff')
def user_breakdown_ajax(request, context=None):
    if context is None:
        context = {}

    end_date = datetime.today().date() - timedelta(days=1)
    start_date = datetime.today().date() - timedelta(days=8)

    if request.method == 'GET':
        start_date = request.GET.get('start_date', start_date)
        end_date = request.GET.get('end_date', end_date)
        if isinstance(start_date, basestring):
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if isinstance(end_date, basestring):
            end_date = datetime.strptime(end_date, '%Y-%m-%d')

        context['total_users'] = User.objects.all()
        context['users_by_range'] = User.objects.filter(date_joined__lte=end_date,
                                                        date_joined__gte=start_date)

    context['form'] = DateFilterForm(initial={'start_date': start_date, 'end_date': end_date})
    return render(request, 'administration/user_breakdown/user_breakdown_ajax.html', context)


@login_required
@permission_required('user.is_staff')
def referrer_reporting(request, context=None):
    if context is None:
        context = {}

    referrer = None
    referral_actions = None
    form = ReferrerForm()
    if request.method == "POST":
        form = ReferrerForm(request.POST)
        if form.is_valid():
            referrer = form.cleaned_data['referrer']
            if form.cleaned_data['action'] is not None and form.cleaned_data['action'] != '':
                referral_actions = [form.cleaned_data['action'], ]

    start_date, end_date = date_filtering(form)

    if referral_actions is None:
        referral_actions = UserReferral.REFERRAL_ACTION_CHOICES_FLAT
    referrals = UserReferral.objects.filter(referral_date__gte=start_date, referral_date__lte=end_date,
                                            referral_paid=False,
                                            referral_action__in=referral_actions)
    if referrer is not None:
        referrals = referrals.filter(referrer=referrer)

    referral_counts = []
    for referrer in set(referrals.values_list('referrer', flat=True)):
        if referrer is not None:
            referrer_counts = [
                ('name', Referrer.objects.get(pk=referrer).name),
                ('total', referrals.filter(referrer=referrer).count()),
            ]
            for action in referral_actions:
                referrer_counts.append(
                    (action, referrals.filter(referrer=referrer, referral_action=action).count())
                )
            referral_counts.append(referrer_counts)
    context['referral_counts'] = referral_counts
    context['actions'] = referral_actions
    context['referrals'] = referrals
    context['form'] = form
    context['date_form'] = DateFilterForm(initial={
        'start_date': (datetime.now() - timedelta(weeks=4)).strftime('%Y-%m-%d'),
        'end_date': datetime.now().strftime('%Y-%m-%d')
    })
    return render(request, 'administration/referrer_reporting/referrer_report.html', context)


@login_required
@permission_required('user.is_staff')
@permission_required('user.change_referrer_paid')
def referrer_reporting_paid(request, uuid, context=None):
    user_referral = get_object_or_404(UserReferral, pk=uuid)
    user_referral.referral_paid = True
    user_referral.save()
    status = {'status': 'done'}
    return HttpResponse(json.dumps(status), content_type='application/json')


def provider_logos(request, context=None):

    if context is None:
        context = {}

    context['providers'] = Provider.objects.all()

    return render(request, 'administration/provider_logos/provider_logos.html', context)

@login_required
@permission_required('user.is_staff')
def update_products_from_salesforce(request, context=None):

    if context is None:
        context = {}

    async_update_products_from_salesforce.delay()

    return render(request, 'administration/update_products_from_salesforce/update.html', context)

@login_required
@permission_required('user.is_staff')
def check_client_portfolios_for_issues_view(request, context=None):
    check_client_portfolios_for_issues()
    messages.success(request, 'Client portfolio checks have been queued')
    return redirect('admininstrationindex')

# -*- coding: utf-8 -*-
import urlparse
import uuid
import datetime
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db.utils import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render, get_object_or_404
from django.shortcuts import render_to_response
from django.template.loader import get_template
from django.db.models import Sum
from django.template import RequestContext, Context
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth import login as auth_login
from django.contrib.sites.models import get_current_site
from django.contrib.auth.models import User, check_password
from registration.models import RegistrationProfile
from django.contrib.sites.models import RequestSite
from django.contrib.auth import logout
from django.core.mail import send_mail
from common.utils import record_referral_signup
from concierge.models import AdviserQueue
from stats.client import StatsDClient
from thisismoney.models import TiMSignups
from common.models import ReminderSignup, RateAlertsSignup, NewsletterSignup, Profile, CampaignsSignup, Referrer
from common.accounts.forms import AuthenticationForm, HealthcheckSignUpForm, SignUpForm, ActivateForm, \
    ResendActivationForm
from common.accounts.forms import SubscriptionForm, PersonalDetailsForm, ChangePasswordForm, DeleteAccountForm, \
    RateAlertForm, BasketSignUpForm
from common.accounts.utils import Stage2Profile, is_number, create_stage_one_profile
from products.models import Product, ProductPortfolio, RatetrackerReminder, BestBuy, Provider, MasterProduct
from thisismoney.forms import TIMFixedRegistrationForm
from common.tasks import delete_user_profile, analytics

UUID = 'uuid'


class TIMRegister(object):
    def __init__(self):
        super(TIMRegister, self).__init__(template_name="thisismoney/registration_form.html",
                                          form_class=TIMFixedRegistrationForm,
                                          success_url=reverse('timregistration_complete'))


@csrf_protect
@never_cache
def login(request,
          template_name='',
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=AuthenticationForm,
          current_app=None, extra_context=None):
    """
    Displays the login form and handles the login action.
    """
    redirect_to = request.REQUEST.get(redirect_field_name, '')

    if request.method == "POST":
        form = authentication_form(data=request.POST)
        if form.is_valid():
            request.session['email'] = form.cleaned_data.get('email', None)
            netloc = urlparse.urlparse(redirect_to)[1]

            # Use default setting if redirect_to is empty
            if not redirect_to:
                redirect_to = settings.LOGIN_REDIRECT_URL

            # Security check -- don't allow redirection to a different
            # host.
            elif netloc and netloc != request.get_host():
                redirect_to = settings.LOGIN_REDIRECT_URL

            # Okay, security checks complete. Log the user in.
            auth_login(request, form.user_cache)

            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()

            return HttpResponseRedirect(redirect_to)
    else:
        data = {'email': request.session.get('email', None)}
        form = AuthenticationForm(initial=data)

    request.session.set_test_cookie()

    current_site = get_current_site(request)
    context = {
        'form': form,
        redirect_field_name: redirect_to,
        'site': current_site,
        'site_name': current_site.name,
    }
    context.update(extra_context or {})
    return render_to_response('accounts/login.html', context,
                              context_instance=RequestContext(request, current_app=current_app))


@never_cache
def healthcheck_signup(request, form_class=HealthcheckSignUpForm, template_name='common/healthcheck_signup.html'):
    context = RequestContext(request)
    if request.method == "POST":
        if request.user.is_authenticated():
            return redirect('healthcheck-portfolio')
        form = SignUpForm(request.POST)
        if form.is_valid():
            if 'referer' in request.session:
                referer = Referrer.objects.get(pk=request.session['referer']).name
            else:
                referer = '(Direct)'
            analytics.delay('event', 'Healthcheck', 'Signup', referer)
            email = form.cleaned_data.get('email')
            request.session['email'] = email
            create_profile_output = create_stage_one_profile(request=request, email=email,
                                                             source='healthcheck_basket_initial')
            if isinstance(create_profile_output, tuple):
                user, user_created, record_stats = create_profile_output
            else:
                return create_profile_output

            if not user_created and user.is_active:
                login_url = reverse('auth_login')
                return redirect('{login_url}?next=/rate-tracker/'.format(login_url=login_url))

            user.profile.newsletter = True
            user.profile.save()

            record_referral_signup(request=request, user=user, user_created=user_created, action='signup')
            record_referral_signup(request=request, user=user, user_created=user_created, action='rate_tracker')
        else:
            return redirect('home')
        return redirect('healthcheck_signup')

    email = request.session.get('email', None)
    if email is None:
        return redirect('home')

    data = {'email': email}

    form = form_class(initial=data)
    return render_to_response(template_name, {'form': form}, context_instance=context)


@never_cache
def healthcheck_add_initial_products(request):
    # Inner function creates a dictionary to be sent through the context
    # for the email message for users who signup with >= 100k
    def append_account(is_fixed, account_object, balance):
        # account_object is either- a RatetrackerReminder (for fixed rate)
        # or a Product (for variable rate)- and contains the variables we need.

        account_dict = {
            'provider': account_object.provider.title,
            'balance': balance,
        }

        if is_fixed:
            # Account object should be a RatetrackerReminder
            if isinstance(account_object, RatetrackerReminder):
                account_dict['type'] = "Fixed Rate"
                account_dict['account_type'] = account_object.account_type.get_title_display()
                account_dict['maturity_date'] = account_object.maturity_date.strftime("%A %d. %B %Y")
        else:
            # Account object should be a Product
            if isinstance(account_object, Product):
                account_dict['type'] = "Variable Rate"
                account_dict['account_type'] = account_object.get_account_type()
                account_dict['rates'] = {'aer': account_object.aer,
                                         'gr': account_object.gross_rate,
                                         'ugr': account_object.underlying_gross_rate}
                account_dict['bonus'] = {'amount': account_object.bonus_amount,
                                         'term': account_object.bonus_term,
                                         'end_date': account_object.bonus_end_date}

        signup_accounts.append(account_dict)

    if request.method == "POST":
        site = RequestSite(request)
        form = HealthcheckSignUpForm(request.POST, extra=request.POST.get('extra_field_count'))

        if form.is_valid():
            email = form.cleaned_data.get('email')
            first_name = form.cleaned_data.get('first_name')
            surname = form.cleaned_data.get('surname')
            telephone = form.cleaned_data.get('telephone')
            password = form.cleaned_data.get('password')
            Stage2Profile(email, first_name, surname, telephone)
            user = User.objects.get(email__iexact=email)
            user.set_password(password)

            # provider is only used to make sure someone entered something
            provider = form.cleaned_data.get('provider', None)
            id = form.cleaned_data.get('product', None)
            balance = form.cleaned_data.get('balance', None)

            record_referral_signup(request=request, user=user, user_created=False, action='signup')
            record_referral_signup(request=request, user=user, user_created=False, action='rate_tracker')

            total = 0

            # We want to keep a record of all the signup accounts as they're processed
            # so that we can display them in an email later if the total balance is over
            # the threshold.
            signup_accounts = []
            is_fixed = form.cleaned_data.get('is_fixed', None)
            if is_fixed:
                account_type = form.cleaned_data.get('account_type')
                reminder = RatetrackerReminder()
                reminder.user = user
                if BestBuy.objects.filter(pk=account_type).exists() and \
                        Provider.objects.filter(pk=provider.id).exists() and balance > 0:
                    reminder.account_type = BestBuy.objects.get(id=account_type)
                    reminder.provider = provider
                    reminder.balance = balance
                    reminder.maturity_date = form.cleaned_data.get('maturity_date')
                    reminder.is_synched = False
                    reminder.save()

                    append_account(is_fixed, reminder, balance)
                    total += balance

            elif id > 0 and balance > 0 and provider > 0 and is_number(id) and is_number(balance):
                product = Product.objects.get(pk=id)
                portfolio = ProductPortfolio()
                portfolio.user = user

                portfolio.account_type = BestBuy.objects.get(id=product.bestbuy_type.all()[0].id)
                portfolio.balance = form.cleaned_data.get('balance')
                portfolio.master_product = product.master_product
                portfolio.provider = product.provider

                # When making I found some bonus terms can be entered as '' as well as None
                # hence the ugly if statement to ensure it is an int
                # as it only gets evaluated on portfolio.save() which by then a typeerror try/except is too late as it could be any field

                if product.bonus_term:
                    if product.bonus_term > 0:
                        portfolio.bonus_term = product.bonus_term
                    else:
                        portfolio.bonus_term = None
                else:
                    portfolio.bonus_term = None
                portfolio.opening_date = form.cleaned_data.get('opening_date')
                portfolio.notice = product.notice
                portfolio.is_synched = False
                portfolio.save()

                append_account(is_fixed, product, balance)
                total += balance

            record_referral_signup(request=request, user=user, user_created=False, action='rate_tracker_used',
                                   third_party=False)

            for index in range(int(form.cleaned_data.get('extra_field_count'))):
                provider = form.cleaned_data.get('provider_field_%i' % index)
                id = form.cleaned_data.get('product_field_%i' % index)
                balance = form.cleaned_data.get('balance_field_%i' % index)
                opening_date_month = form.cleaned_data.get('opening_date_month_field_%i' % index)
                opening_date_year = form.cleaned_data.get('opening_date_year_field_%i' % index)
                is_fixed = form.cleaned_data.get('is_fixed_field_%i' % index)
                if is_fixed:
                    account_type = form.cleaned_data.get('account_type_field_%i' % index)
                    reminder = RatetrackerReminder()
                    reminder.user = user
                    if account_type > 0 and account_type != "0" and provider > 0 and balance > 0:
                        reminder.account_type = BestBuy.objects.get(id=account_type)
                        reminder.provider = Provider.objects.get(id=provider)
                        reminder.balance = balance
                        maturity_date_month = form.cleaned_data.get('maturity_date_month_field_%i' % index)
                        maturity_date_year = form.cleaned_data.get('maturity_date_year_field_%i' % index)
                        if maturity_date_month > 0 and maturity_date_year > 0:
                            reminder.maturity_date = datetime.datetime(maturity_date_year, maturity_date_month,
                                                                       1).date()

                            reminder.is_synched = False
                            reminder.save()

                            append_account(is_fixed, reminder, balance)
                            total += balance
                elif id > 0 and balance > 0 and provider > 0 and is_number(id) and is_number(balance):
                    product = Product.objects.get(pk=id)
                    portfolio = ProductPortfolio()
                    portfolio.user = user

                    portfolio.account_type = BestBuy.objects.get(id=product.bestbuy_type.all()[0].id)
                    portfolio.balance = balance
                    portfolio.master_product = product.master_product
                    portfolio.provider = product.provider
                    if product.bonus_term > 0:
                        portfolio.bonus_term = product.bonus_term
                    else:
                        portfolio.bonus_term = None
                    portfolio.notice = product.notice

                    if product.show_opening_date():
                        if opening_date_month > 0 and opening_date_year > 0:
                            portfolio.opening_date = datetime.datetime(opening_date_year, opening_date_month, 1).date()
                            portfolio.is_synched = False
                            portfolio.save()
                    else:
                        portfolio.is_synched = False
                        portfolio.save()

                    append_account(is_fixed, product, balance)
                    total += balance

            if total >= 100000:
                text_email = get_template('core/100k_signup_email.txt')
                mail_context = Context({'user': user,
                                        'total': total,
                                        'signup_accounts': signup_accounts})
                text_content = text_email.render(mail_context)
                subject = '%s %s signed up with more than 100k' % (first_name, surname)
                send_mail(subject,
                          text_content,
                          'savings.champion@savingschampion.co.uk',
                          ['concierge@savingschampion.co.uk'], fail_silently=False)
                adviser_queue, _ = AdviserQueue.objects.get_or_create(email=email)
                adviser_queue.telephone = telephone
                adviser_queue.name = "%s %s" % (first_name, surname)
                adviser_queue.source = 'Rate Tracker > 100K'
                adviser_queue.save()

                AdviserQueue.add_to_queue(email, first_name, surname, 'Rate Tracker > 100K',
                                          telephone_number=telephone)

            # Only allow non activated users untl the browser closes
            request.session.set_expiry(0)
            # required so we don;t have to call authenticate()
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            auth_login(request, user)
            user.save()
            return redirect('healthcheck-portfolio')
    return redirect('healthcheck_signup')


@never_cache
def healthcheck_remind(request, template_name='common/remind.html'):
    context = RequestContext(request)
    email = request.session.get('email', None)
    if email:
        try:
            signup = ReminderSignup.objects.get(email=email)
        except ReminderSignup.DoesNotExist:
            signup = ReminderSignup()
            signup.email = email
            signup.is_synched = False
            signup.healthcheck = True
            signup.save()
        data = {'email': email}
        context['raform'] = RateAlertForm(initial=data)

    return render_to_response(template_name, context_instance=context)


def send_ratealert_activation(request, signup):
    site = RequestSite(request)
    send_mail('Please activate your subscription',
              'Please click the following link to activate %s%s%s%s%s' % (
                  'https://', site.domain, '/signup/ratealert/activate/', signup.activation_key, '/'),
              'savings.champion@savingschampion.co.uk',
              [signup.email], fail_silently=False)


@never_cache
def healthcheck_remind_finished(request, template_name="common/remind_finished.html"):
    context = RequestContext(request)
    if request.method == "POST":
        form = RateAlertForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            try:
                signup = RateAlertsSignup.objects.get(email=email)
                # someone has tried resigning up - now we need to check if they have activated anywhere else on the site

                if signup.is_activated is False:
                    if NewsletterSignup.objects.filter(email=email).exists():
                        newssignup = NewsletterSignup.objects.get(email=email)
                        if newssignup.is_activated:
                            signup.is_activated = True
                            signup.save()
                            return redirect('healthcheck_remind_already_activated')
                        else:
                            send_ratealert_activation(request, signup)
                    elif User.objects.filter(email__iexact=email).exists():
                        user = User.objects.get(email__iexact=email)
                        if user.is_active:
                            signup.is_activated = True
                            signup.save()
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
                            return redirect('healthcheck_remind_already_activated')
                        else:
                            send_ratealert_activation(request, signup)

                    else:
                        send_ratealert_activation(request, signup)
            except RateAlertsSignup.DoesNotExist:
                signup = RateAlertsSignup()
                signup.email = email
                signup.is_synched = False
                signup.activation_key = str(uuid.uuid4()).replace('-', '')
                while RateAlertsSignup.objects.filter(activation_key=signup.activation_key).exists():
                    signup.activation_key = str(uuid.uuid4()).replace('-', '')
                signup.is_activated = False
                signup.save()
                send_ratealert_activation(request, signup)
            context['rate_alerts'] = True

    return render_to_response(template_name, context_instance=context)


def healthcheck_remind_already_activated(request, template_name='common/signups/rathankyou.html'):
    context = RequestContext(request)
    return render_to_response(template_name, context_instance=context)


@never_cache
def activate(request, activation_key, form_class=ActivateForm, template_name='common/activate.html'):
    # get user email from activation key - if key does not exist say oops! we have sent you a new activation key
    context = RequestContext(request)
    registration_profiles = RegistrationProfile.objects.filter(activation_key=activation_key)

    if not registration_profiles.exists():
        return redirect('resend_activation')

    for registration_profile in registration_profiles:
        user = registration_profile.user
        portfolio_total = ProductPortfolio.objects.filter(user=user, is_deleted=False).aggregate(Sum('balance'))
        reminders_total = RatetrackerReminder.objects.filter(user=user, is_deleted=False).aggregate(Sum('balance'))
        grand_total = 0
        if portfolio_total['balance__sum'] is not None:
            grand_total += portfolio_total['balance__sum']
        if reminders_total['balance__sum'] is not None:
            grand_total += reminders_total['balance__sum']

        try:
            profile = user.profile
        except Profile.DoesNotExist:
            profile = Profile(user=user)
            profile.save()
        except Profile.MultipleObjectsReturned:
            profiles = Profile.objects.filter(user=user)
            profile = profiles[0]
        phone_required = False
        data = {'email': user.email, 'telephone': profile.telephone}
        form = form_class(initial=data, grand_total=grand_total)
        if grand_total >= 100000:
            phone_required = True
    return render_to_response(template_name, {'form': form, 'telephone_required': phone_required},
                              context_instance=context)


@never_cache
def finish_activation(request, template_name='common/activation_complete.html'):
    # Inner function creates a dictionary to be sent through the context
    # for the email message for users who signup with >= 100k
    def append_account(is_fixed, account_object, balance):
        # account_object is either- a RatetrackerReminder (for fixed rate)
        # or a Product (for variable rate)- and contains the variables we need.

        account_dict = {
            'provider': account_object.provider.title,
            'balance': balance,
        }

        if is_fixed:
            # Account object should be a RatetrackerReminder
            if isinstance(account_object, RatetrackerReminder):
                account_dict['type'] = "Fixed Rate"
                account_dict['account_type'] = account_object.account_type.get_title_display()
                account_dict['maturity_date'] = account_object.maturity_date.strftime("%A %d. %B %Y")
        else:
            # Account object should be a Product
            if isinstance(account_object, MasterProduct):
                old_product_tier = account_object.get_latest_old_product_tier(balance)
                account_dict['type'] = "Variable Rate"
                account_dict['account_type'] = account_object.get_account_type()
                account_dict['rates'] = {'aer': old_product_tier.aer,
                                         'gr': old_product_tier.gross_rate,
                                         'ugr': old_product_tier.underlying_gross_rate}
                account_dict['bonus'] = {'amount': old_product_tier.bonus_amount,
                                         'term': old_product_tier.bonus_term,
                                         'end_date': old_product_tier.bonus_end_date}

        signup_accounts.append(account_dict)

    context = RequestContext(request)
    if request.method == "POST":
        form = ActivateForm(request.POST)
        if form.is_valid():
            user = User.objects.get(email__iexact=form.cleaned_data.get('email'))
            user.set_password(form.cleaned_data.get('password'))
            user.is_active = True
            user.save()
            regProfile = RegistrationProfile.objects.get(user=user)
            regProfile.activation_key = 'ALREADY_ACTIVATED'
            regProfile.save()
            try:
                profile = user.profile
            except Profile.DoesNotExist:
                profile = Profile(user=user)
                profile.save()
            except Profile.MultipleObjectsReturned:
                profiles = Profile.objects.filter(user=user)
                profile = profiles[0]
            profile.telephone = form.cleaned_data.get('telephone')
            dob = form.cleaned_data.get('dob')
            if dob > 0:
                profile.dob = datetime.datetime(dob, 01, 01)

            profile.postcode = form.cleaned_data.get('postcode')
            profile.replaced_password = True
            profile.is_synched = False

            profile.newsletter = form.cleaned_data.get('newsletter')
            profile.ratealerts = form.cleaned_data.get('ratealert')
            profile.save()

            signup_accounts = []
            portfolios = ProductPortfolio.objects.filter(user=user, is_deleted=False)
            reminders = RatetrackerReminder.objects.filter(user=user, is_deleted=False)
            portfolio_total = portfolios.aggregate(Sum('balance'))
            reminders_total = reminders.aggregate(Sum('balance'))
            for reminder in reminders:
                append_account(True, reminder, reminder.balance)
            for portfolio in portfolios:
                append_account(False, portfolio.master_product, portfolio.balance)

            grand_total = 0
            if portfolio_total['balance__sum'] is not None:
                grand_total += portfolio_total['balance__sum']
            if reminders_total['balance__sum'] is not None:
                grand_total += reminders_total['balance__sum']
            if grand_total >= 100000:
                AdviserQueue.add_to_queue(user.email, user.first_name, user.last_name, 'Rate Tracker > 100K',
                                          telephone_number=profile.telephone, date_of_birth=profile.dob)


            # log them back in and set their session expiry back to global (in case they never closed their browser)
            request.session.set_expiry(None)
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            auth_login(request, user)
            # REDIRECT THEM TO STOP ADDITIONAL POSTS
            return redirect('activation_complete')
        else:
            template_name = 'common/activate.html'
            return render_to_response(template_name, {'form': form},
                                      context_instance=context)

    return render_to_response(template_name,
                              context_instance=context)


def tim_activate(request, activation_key, template_name='common/activation_complete.html'):
    # get user email from activation key - if key does not exist say oops! we have sent you a new activation key
    context = RequestContext(request)
    try:
        user = RegistrationProfile.objects.get(activation_key=activation_key).user
    except RegistrationProfile.DoesNotExist:
        return redirect('resend_activation')
    user.is_active = True
    user.save()
    try:
        profile = user.profile
    except Profile.DoesNotExist:
        profile = Profile(user=user)
        profile.save()
    except Profile.MultipleObjectsReturned:
        profiles = Profile.objects.filter(user=user)
        profile = profiles[0]
    profile.skeleton_user = False
    profile.is_synched = False
    profile.save()
    if TiMSignups.objects.filter(email=user.email).exists():
        timSignup = TiMSignups.objects.get(email=user.email)
        timSignup.completed_activation = True
        timSignup.save()

    user.backend = 'django.contrib.auth.backends.ModelBackend'
    auth_login(request, user)
    return render_to_response(template_name, context_instance=context)


@never_cache
def resend_activation(request, form_class=ResendActivationForm, template_name='common/resend_activation.html', context=None):
    if context is None:
        context = {}

    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            request.session['email'] = form.cleaned_data.get('email')
            return redirect('resend_activation')

    else:
        email = request.session.get('email', None)

        if email:
            site = get_current_site(request)
            user = User.objects.get(email__iexact=email)
            RegistrationProfile.objects.get(user=user).send_activation_email(site)
            context['email'] = email
        else:
            data = {'email': request.session.get('email', None)}
            context['form'] = form_class(initial=data)

    return render(request, template_name, context)


@login_required
@never_cache
def your_account(request, template_name='common/youraccount/your_account.html'):
    context = RequestContext(request)
    user = request.user
    try:
        profile = user.profile
    except Profile.DoesNotExist:
        profile = Profile(user=user)
        profile.save()
    except Profile.MultipleObjectsReturned:
        profiles = Profile.objects.filter(user=user)
        profile = profiles[0]
    context['user'] = user
    context['profile'] = profile

    personal_details = {'first_name': user.first_name, 'last_name': user.last_name,
                        'email': user.email, 'telephone': profile.telephone,
                        'postcode': profile.postcode,
                        'old_email': request.user.email,
                        'ratetracker_alert_threshold': request.user.profile.ratetracker_threshold
                        }

    if profile.dob:
        personal_details['dob'] = profile.dob.year
    subscriptions = {'newsletter': profile.newsletter, 'ratealert': profile.ratealerts}

    delete_details = {'user_id': user.id}

    context['subscriptionform'] = SubscriptionForm(initial=subscriptions)
    context['personalform'] = PersonalDetailsForm(initial=personal_details)
    context['deleteform'] = DeleteAccountForm(initial=delete_details)
    context['passwordform'] = ChangePasswordForm()
    return render_to_response(template_name,
                              context_instance=context)


@login_required
@never_cache
def update_subscriptions(request, template_name='common/youraccount/your_account.html'):
    context = RequestContext(request)

    if request.method == "POST":
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            try:
                profile = request.user.profile
            except Profile.DoesNotExist:
                profile = Profile(user=request.user)
                profile.save()
            except Profile.MultipleObjectsReturned:
                profiles = Profile.objects.filter(user=request.user)
                profile = profiles[0]
            profile.newsletter = form.cleaned_data.get('newsletter', None)
            profile.ratealerts = form.cleaned_data.get('ratealert', None)
            profile.is_synched = False
            profile.save()
            return redirect('your_account')

    return render_to_response(template_name, context_instance=context)


@login_required
@never_cache
def delete_account(request, template_name='common/youraccount/account_deleted.html'):
    context = RequestContext(request)

    if request.method == "POST":
        form = DeleteAccountForm(request.POST)

        if form.is_valid():
            id = form.cleaned_data.get('user_id')

            if request.user.id == id:
                send_mail('%s has deleted their account' % request.user.email,
                          '%s requested an account deletion. This is now handled automatically and this email is just a notification.' % request.user.email,
                          'savings.champion@savingschampion.co.uk',
                          ['info@savingschampion.co.uk'], fail_silently=False)
                user = User.objects.get(pk=request.user.pk)
                user.is_active = False
                user.save()
                logout(request)
                delete_user_profile.apply_async((user.pk,))
    return render_to_response(template_name, context_instance=context)


@login_required
@never_cache
def update_details(request, template_name='common/youraccount/formerrors/personal_details.html'):
    context = RequestContext(request)

    if request.method == "POST":
        form = PersonalDetailsForm(request.POST)

        if form.is_valid():
            try:
                profile = request.user.profile
            except Profile.DoesNotExist:
                profile = Profile(user=request.user)
                profile.save()
            except Profile.MultipleObjectsReturned:
                profiles = Profile.objects.filter(user=request.user)
                profile = profiles[0]
            request.user.first_name = form.cleaned_data.get('first_name')
            request.user.last_name = form.cleaned_data.get('last_name')
            request.user.email = form.cleaned_data.get('email')

            profile.telephone = form.cleaned_data.get('telephone')
            dob = form.cleaned_data.get('dob')
            if dob > 0:
                profile.dob = datetime.datetime(dob, 01, 01)
            profile.postcode = form.cleaned_data.get('postcode')
            if profile.ratetracker_threshold != form.cleaned_data.get('ratetracker_alert_threshold'):
                profile.ratetracker_threshold = form.cleaned_data.get('ratetracker_alert_threshold')
                profile.ratetracker_threshold_set = True
            profile.is_synched = False
            request.user.save()
            profile.save()
            template_name = 'common/youraccount/success/personal_details.html'
        else:
            context['form'] = form
    return render_to_response(template_name, context_instance=context)


@login_required
@never_cache
def change_password(request, template_name='common/youraccount/formerrors/password.html'):
    context = RequestContext(request)
    context['form'] = ChangePasswordForm()
    if request.method == "POST":
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            old_password = form.cleaned_data.get('old_password')
            new_password = form.cleaned_data.get('new_password1')

            if check_password(old_password, request.user.password):
                request.user.set_password(new_password)
                request.user.save()
                context['passwordform'] = form
                template_name = 'common/youraccount/success/password.html'
            else:
                context['form'] = form
        else:
            context['form'] = form
    return render_to_response(template_name, context_instance=context)


def tim_fixed_register(request):
    # sigh
    if request.method == "POST":
        form = TIMFixedRegistrationForm(request.POST)
        if form.is_valid():
            try:
                timSignup = TiMSignups.objects.get(email=form.cleaned_data.get('email'))
                timSignup.completed_signup = True
                timSignup.save()
            except:
                # User changed email on results page
                timSignup = TiMSignups(email=form.cleaned_data.get('email'), completed_signup=True)
                timSignup.save()
            email, password, first_name, last_name = form.cleaned_data.get('email'), form.cleaned_data.get(
                'password1'), form.cleaned_data.get('first_name'), form.cleaned_data.get('surname')
            newsletter = form.cleaned_data.get('newsletter', False)
            ratealerts = form.cleaned_data.get('ratealerts', False)
            user_created = False
            try:
                user = User.objects.get(email__iexact=email)
            except User.DoesNotExist:

                user, user_created, record_stats = create_stage_one_profile(request, email=email, source='tim_fixed_register')

            try:
                profile = user.profile
            except Profile.DoesNotExist:
                profile = Profile(user=user)
                profile.save()
            except Profile.MultipleObjectsReturned:
                profiles = Profile.objects.filter(user=user)
                profile = profiles.first()

            user.first_name = first_name
            user.last_name = last_name
            user.set_password(password)
            user.is_active = False
            user.save()

            profile.newsletter = newsletter
            profile.ratealerts = ratealerts
            profile.source = form.cleaned_data.get('source')
            profile.is_synched = False
            profile.skeleton_user = False
            if RateAlertsSignup.objects.filter(email=email).exists():
                profile.ratealerts = True
            if NewsletterSignup.objects.filter(email=email).exists():
                profile.newsletter = True

            profile.save()
            # add the fixed rate product
            provider = request.POST['provider']
            balance = request.POST['balance']
            account_type = request.POST['account_type']
            bestbuy = BestBuy.objects.get(id=account_type)

            if bestbuy.is_fixed:
                reminder = RatetrackerReminder()
                reminder.user = user
                reminder.account_type = bestbuy
                reminder.balance = balance
                reminder.provider = Provider.objects.get(id=provider)
                reminder.maturity_date = datetime.datetime(month=int(request.POST['maturity_date_month']),
                                                           year=int(request.POST['maturity_date_month']),
                                                           day=1)
                reminder.is_synched = False
                reminder.save()
            else:
                product = request.POST['product']
                provider = request.POST['provider']
                opening_date_month = int(request.POST['opening_date_month'])
                opening_date_year = int(request.POST['opening_date_year'])
                portfolio = ProductPortfolio()
                portfolio.user = user
                portfolio.balance = balance
                portfolio.account_type = bestbuy
                portfolio.master_product = get_object_or_404(Product, pk=product).master_product
                portfolio.provider = get_object_or_404(Provider, pk=provider)
                portfolio.opening_date = datetime.datetime(month=opening_date_month, year=opening_date_year, day=1)
                portfolio.is_synched = False
                portfolio.save()

            record_referral_signup(request=request, user=user, user_created=user_created, action='signup')

            return redirect('timregistration_complete')
        return render(request, 'thisismoney/registration_form.html', {'form': form})
    return redirect('timregistration_register')


@never_cache
def healthcheck_basket_signup(request, form_class=BasketSignUpForm, template_name='common/basket/basket_signup.html'):
    context = RequestContext(request)
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            if 'referer' in request.session:
                referer = Referrer.objects.get(pk=request.session['referer']).name
            else:
                referer = '(Direct)'
            analytics.delay('event', 'Healthcheck Basket', 'Signup', referer)
            email = form.cleaned_data.get('email')
            request.session['email'] = email
            create_profile_output = create_stage_one_profile(request=request, email=email,
                                                             source='healthcheck_basket_signup', send_activation=False)
            if isinstance(create_profile_output, tuple):
                user, user_created, record_stats = create_profile_output
            else:
                return create_profile_output
            if not user_created and user.is_active:
                login_url = reverse('auth_login')
                return redirect('{login_url}?next=/rate-tracker/'.format(login_url=login_url))
            record_referral_signup(request=request, user=user, user_created=user_created, action='signup')
            record_referral_signup(request=request, user=user, user_created=user_created, action='rate_tracker')
            return redirect('healthcheck_basket_signup')
        else:
            return redirect('home')

    healthcheck_initial = True if 'healthcheck' in request.GET else False
    concierge_initial = True if 'concierge' in request.GET else False

    form = form_class(initial={"email": request.session.get("email", None),
                               "advice": healthcheck_initial,
                               "concierge": concierge_initial})
    return render_to_response(template_name, {'form': form}, context_instance=context)


@never_cache
def healthcheck_basket_initial(request):
    if request.method == "POST":
        site = RequestSite(request)
        form = BasketSignUpForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            request.session['email'] = email
            ratetracker = form.cleaned_data.get('ratetracker', None)
            advice = form.cleaned_data.get('advice', None)
            concierge = form.cleaned_data.get('concierge', None)
            newsletter = form.cleaned_data.get('newsletter', True)
            ratealert = form.cleaned_data.get('ratealert', True)
            first_name = form.cleaned_data.get('first_name', None)
            surname = form.cleaned_data.get('surname', None)
            telephone = form.cleaned_data.get('telephone', None)
            password = form.cleaned_data.get('password', None)

            create_profile_output = create_stage_one_profile(request=request, email=email,
                                                             source='healthcheck_basket_initial',
                                                             send_activation=ratetracker)
            if isinstance(create_profile_output, tuple):
                user, user_created, record_stats = create_profile_output
            else:
                return create_profile_output

            user.set_password(password)
            user.first_name = first_name
            user.last_name = surname
            user.save()
            profile = Profile.objects.filter(user=user).latest()
            profile.telephone = telephone
            profile.newsletter = newsletter
            profile.ratealerts = ratealert
            profile.save()

            record_referral_signup(request, user, user_created, 'signup')
            if ratealert:
                record_referral_signup(request, user, user_created, 'rate_alerts')
            if newsletter:
                record_referral_signup(request, user, user_created, 'newsletter')
            if ratetracker:
                record_referral_signup(request, user, user_created, 'rate_tracker')

            if advice or concierge:
                record_referral_signup(request, user, user_created, 'concierge_enquiry')
                if advice and concierge:
                    message = "Healthcheck and Concierge"
                else:
                    message = "Concierge" if concierge else "Healthcheck"

                profile.source = "%s (%s)" % (profile.source, message)
                profile.save()

                send_mail('New %s Enquiry from the basket' % message,
                          u'Email: %s\nName: %s\nTelephone %s\nSource: %s\n' % (
                              user.email, " ".join([user.first_name, user.last_name]), profile.telephone,
                              profile.source),
                          'savings.champion@savingschampion.co.uk',
                          ['concierge@savingschampion.co.uk'], fail_silently=True)
                signup = CampaignsSignup()
                signup.email = user.email
                signup.name = '{first_name} {last_name}'.format(first_name=user.first_name, last_name=user.last_name)
                signup.telephone = profile.telephone
                signup.source = profile.source
                signup.is_synched = False
                try:
                    signup.save()
                except IntegrityError:
                    pass  # If they've already signed up, then move along.
                try:
                    AdviserQueue.add_to_queue(signup.email, user.first_name, user.last_name, profile.source,
                                              telephone_number=profile.telephone)
                except IntegrityError:
                    if AdviserQueue.new_lead(signup.email):
                        adviser_queue = AdviserQueue.objects.get(email=signup.email)
                        if adviser_queue.status in [2, 8, 9, 10] and adviser_queue.adviser is not None:
                            adviser_queue.adviser = None
                        adviser_queue.interaction_started = datetime.datetime.now()
                        adviser_queue.save()
                        AdviserQueue.add_to_queue(signup.email, user.first_name, user.last_name, profile.source,
                                                  telephone_number=profile.telephone)

            # Only allow non activated users until the browser closes
            request.session.set_expiry(0)
            # required so we don;t have to call authenticate()
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            auth_login(request, user)
            user.save()
            if ratetracker:
                return redirect('healthcheck_basket_ratetracker')
            return redirect('healthcheck_thankyou')


@login_required
@never_cache
def healthcheck_basket_ratetracker(request, template_name='common/basket/basket_ratetracker.html'):
    context = RequestContext(request)

    # Inner function creates a dictionary to be sent through the context
    # for the email message for users who signup with >= 100k
    def append_account(is_fixed, account_object, balance):
        # account_object is either- a RatetrackerReminder (for fixed rate)
        # or a Product (for variable rate)- and contains the variables we need.

        account_dict = {
            'provider': account_object.provider.title,
            'balance': balance,
        }

        if is_fixed:
            # Account object should be a RatetrackerReminder
            if isinstance(account_object, RatetrackerReminder):
                account_dict['type'] = "Fixed Rate"
                account_dict['account_type'] = account_object.account_type.get_title_display()
                account_dict['maturity_date'] = account_object.maturity_date.strftime("%A %d. %B %Y")
        else:
            # Account object should be a Product
            if isinstance(account_object, Product):
                account_dict['type'] = "Variable Rate"
                account_dict['account_type'] = account_object.get_account_type()
                account_dict['rates'] = {'aer': account_object.aer,
                                         'gr': account_object.gross_rate,
                                         'ugr': account_object.underlying_gross_rate}
                account_dict['bonus'] = {'amount': account_object.bonus_amount,
                                         'term': account_object.bonus_term,
                                         'end_date': account_object.bonus_end_date}

        signup_accounts.append(account_dict)

    if request.method == "POST":
        form = HealthcheckSignUpForm(request.POST, extra=request.POST.get('extra_field_count'))
        if form.is_valid():
            user = request.user
            # provider is only used to make sure someone entered something
            provider = form.cleaned_data.get('provider', None)
            id = form.cleaned_data.get('product', None)
            balance = form.cleaned_data.get('balance', None)

            total = 0
            signup_accounts = []
            is_fixed = form.cleaned_data.get('is_fixed', None)
            if is_fixed:
                account_type = form.cleaned_data.get('account_type')
                reminder = RatetrackerReminder()
                reminder.user = user
                if account_type > 0 and account_type != "0" and provider > 0 and balance > 0:
                    reminder.account_type = BestBuy.objects.get(id=account_type)
                    reminder.provider = Provider.objects.get(id=provider.id)
                    reminder.balance = balance
                    reminder.maturity_date = form.cleaned_data.get('maturity_date')
                    reminder.is_synched = False
                    reminder.save()

                    append_account(is_fixed, reminder, balance)
                    total += balance

            elif id > 0 and balance > 0 and provider > 0 and is_number(id) and is_number(balance):
                product = Product.objects.get(pk=id)
                portfolio = ProductPortfolio()
                portfolio.user = user

                portfolio.account_type = BestBuy.objects.get(id=product.bestbuy_type.all()[0].id)
                portfolio.balance = form.cleaned_data.get('balance')
                portfolio.master_product = product.master_product
                portfolio.provider = product.provider

                #  When making I found some bonus terms can be entered as '' as well as None
                #  hence the ugly if statement to ensure it is an int
                #  as it only gets evaluated on portfolio.save() which by then a typeerror try/except is too late as
                #  it could be any field

                if product.bonus_term:
                    if product.bonus_term > 0:
                        portfolio.bonus_term = product.bonus_term
                    else:
                        portfolio.bonus_term = None
                else:
                    portfolio.bonus_term = None
                portfolio.opening_date = form.cleaned_data.get('opening_date')
                portfolio.notice = product.notice
                portfolio.is_synched = False
                portfolio.save()

                append_account(is_fixed, product, balance)
                total += balance

            for index in range(int(form.cleaned_data.get('extra_field_count'))):
                provider = form.cleaned_data.get('provider_field_%i' % index)
                id = form.cleaned_data.get('product_field_%i' % index)
                balance = form.cleaned_data.get('balance_field_%i' % index)
                opening_date_month = form.cleaned_data.get('opening_date_month_field_%i' % index)
                opening_date_year = form.cleaned_data.get('opening_date_year_field_%i' % index)
                is_fixed = form.cleaned_data.get('is_fixed_field_%i' % index)
                if is_fixed:
                    account_type = form.cleaned_data.get('account_type_field_%i' % index)
                    reminder = RatetrackerReminder()
                    reminder.user = user
                    if account_type > 0 and account_type != "0" and provider > 0 and balance > 0:
                        reminder.account_type = BestBuy.objects.get(id=account_type)
                        reminder.provider = Provider.objects.get(id=provider)
                        reminder.balance = balance
                        maturity_date_month = form.cleaned_data.get('maturity_date_month_field_%i' % index)
                        maturity_date_year = form.cleaned_data.get('maturity_date_year_field_%i' % index)
                        if maturity_date_month > 0 and maturity_date_year > 0:
                            reminder.maturity_date = datetime.datetime(maturity_date_year, maturity_date_month,
                                                                       1).date()
                            reminder.is_synched = False
                            reminder.save()
                            append_account(is_fixed, reminder, balance)
                            total += balance

                elif id > 0 and balance > 0 and provider > 0 and is_number(id) and is_number(balance):
                    product = Product.objects.get(pk=id)
                    portfolio = ProductPortfolio()
                    portfolio.user = user

                    portfolio.account_type = BestBuy.objects.get(id=product.bestbuy_type.all()[0].id)
                    portfolio.balance = balance
                    portfolio.master_product = product.master_product
                    portfolio.provider = product.provider
                    if product.bonus_term:
                        if product.bonus_term > 0:
                            portfolio.bonus_term = product.bonus_term
                        else:
                            portfolio.bonus_term = None
                    else:
                        portfolio.bonus_term = None
                    portfolio.notice = product.notice

                    if product.show_opening_date():
                        if opening_date_month > 0 and opening_date_year > 0:
                            portfolio.opening_date = datetime.datetime(opening_date_year, opening_date_month, 1).date()
                            portfolio.is_synched = False
                            portfolio.save()
                    else:
                        portfolio.is_synched = False
                        portfolio.save()
                        append_account(is_fixed, product, balance)
                        total += balance
            if total >= 100000:
                text_email = get_template('core/100k_signup_email.txt')
                mail_context = Context({'user': user,
                                        'total': total,
                                        'signup_accounts': signup_accounts})
                text_content = text_email.render(mail_context)
                subject = '%s %s signed up with more than 100k' % (user.first_name, user.last_name)
                send_mail(subject,
                          text_content,
                          'savings.champion@savingschampion.co.uk',
                          ['concierge@savingschampion.co.uk'], fail_silently=False)
                adviser_queue, _ = AdviserQueue.objects.get_or_create(email=user.email)
                try:
                    adviser_queue.telephone = user.profile_set.all()[0].telephone
                except:
                    pass
                adviser_queue.name = "%s %s" % (user.first_name, user.last_name)
                adviser_queue.source = 'Rate Tracker > 100K'
                adviser_queue.save()

                AdviserQueue.add_to_queue(user.email, user.first_name, user.last_name, 'Rate Tracker > 100K',
                                          telephone_number=user.profile.telephone)

            record_referral_signup(request=request, user=user, user_created=False, action='signup')
            record_referral_signup(request=request, user=user, user_created=False, action='rate_tracker')

            record_referral_signup(request=request, user=user, user_created=False, action='rate_tracker_used',
                                   third_party=False)
            return redirect('healthcheck-portfolio')
    else:
        # fill in the fields not needed on the basket page
        data = {'email': 'hidden@hidden.com',
                'first_name': 'name',
                'surname': 'surname',
                'password': 'abcd'}
        form = HealthcheckSignUpForm(initial=data)

    context['form'] = form
    return render_to_response(template_name, context_instance=context)


def healthcheck_basket_thankyou(request):
    return render_to_response('common/basket/healthcheck_basket_thankyou.html')

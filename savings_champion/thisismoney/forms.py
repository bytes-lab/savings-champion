from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.core.urlresolvers import reverse
from django.db import ProgrammingError
from django.templatetags.static import static
from tinymce.widgets import TinyMCE
from decimal import *
from django import forms
from django.conf import settings
from django.forms.models import modelformset_factory
from common.accounts.utils import MakeUsername, create_stage_one_profile
from common.models import Profile, RateAlertsSignup, NewsletterSignup
from common.widgets import MonthYearWidget
from products.fields import CurrencyField, CurrencyInput
from products.models import Provider, Product, ProductPortfolio, BestBuy, RatetrackerReminder
from products.utils import get_maturity_based_bestbuys, get_ISA_bestbuys
import datetime
from thisismoney.models import TiMSignups

EMPTY_VALUES = ['', ' ', None]

IDONTKNOW = 'i don\'t know'

BESTBUY_THRESHOLD = getattr(settings, 'BESTBUY_THRESHOLD', 85000)

UNKNOWN = 'unknown'


class BestBuyModelForm(forms.ModelForm):
    class Meta:
        model = BestBuy
        widgets = {
            'description': TinyMCE,
            'landing_page_description': TinyMCE,
            'meta_description': forms.Textarea,
            'comparison_meta_description': forms.Textarea
        }


ACCOUNT_TYPE_CHOICES = (('', 'Non Tax Payer'),
                        ('Starting Rate', 'Starting Rate'),
                        ('Basic Rate', 'Basic Rate'),
                        ('Higher Rate', 'Higher Rate'),
                        ('Additional Rate', 'Additional Rate'))


def _get_years():
    now = datetime.datetime.now()
    return range(now.year, 1990, -1)


def _get_maturity_years():
    now = datetime.datetime.now()
    return range(now.year, now.year + 10, 1)


def _get_rt_account_type_choices():
    vals = BestBuy.objects.values('id', 'title').order_by('title')
    retval = [('', 'Savings Type')]
    try:
        for val in vals:
            retval.append([val['id'], val['title']])
    except ProgrammingError:
        pass
    retval.append(('unknown', 'I don\'t know'))
    return retval


def _get_isa_account_type_choices():
    vals = get_ISA_bestbuys().values('id', 'title').order_by('title')
    retval = [('', 'Select account type')]
    try:
        for val in vals:
            retval.append([val['id'], val['title']])
    except ProgrammingError:
        pass

    retval.append(('unknown', 'I don\'t know'))
    return retval


class RateTrackerForm(forms.Form):
    """ When the user is searching if they specify a Fixed Rate Bond type, 
    the Account Name is not applicable and not required. 
    """
    provider = forms.ModelChoiceField(
        Provider.objects.all().exclude(title="Kent Reliance Building Society").exclude(title="Sainsbury's Finance"),
        empty_label='Provider', widget=forms.Select(attrs={'class': 'required number'}))
    account_type = forms.ChoiceField(widget=forms.Select(attrs={'class': 'required number'}),
                                     choices=_get_rt_account_type_choices())

    balance = CurrencyField(widget=CurrencyInput(attrs={'class': 'text required commaNumber'}), initial=Decimal('1'))
    product = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'text required'}), required=False)

    maturity_date = forms.DateField(widget=MonthYearWidget(years=_get_maturity_years(), attrs={'min': '1'}),
                                    required=False)


    def __init__(self, *args, **kwargs):
        super(RateTrackerForm, self).__init__(*args, **kwargs)
        self.set_reminder = False
        self.high_balance = False

    def in_bestbuy_list(self, account_type):
        for val in get_maturity_based_bestbuys().values('id'):
            if account_type == val['id']:
                return True
        return False

    def clean(self):
        super(RateTrackerForm, self).clean()

        data = self.cleaned_data

        account_type = data.get('account_type', None)
        balance = data.get('balance', None)

        if account_type in EMPTY_VALUES:
            self.errors['account_type'] = 'Please enter an account type'
            return

        if self.in_bestbuy_list(int(account_type)):
            # Maturity date is a required field
            self.set_reminder = True
            maturity_date = data.get('maturity_date', None)
            if maturity_date in EMPTY_VALUES:
                self.errors['maturity_date'] = 'Please enter a maturity date'
            else:
                today = datetime.datetime.date(datetime.datetime.now())
                if maturity_date < today:
                    self.errors['maturity_date'] = 'Please enter a maturity date in the future'
        else:
            # we need either product or maturity date to be populated
            product = data.get('product', None)
            if product in EMPTY_VALUES:
                self.errors['product'] = 'Please choose an Account Name'

        if balance in EMPTY_VALUES or balance <= 0:
            self.errors['balance'] = 'Please enter your balance'
        return data


def _get_provider_isa_best_buys():
    return Provider.objects.filter(providerbestbuy__bestbuys__in=get_ISA_bestbuys()).distinct()


class TIMRateTrackerForm(RateTrackerForm):
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'required email'}), required=True)

    def clean(self):
        super(TIMRateTrackerForm, self).clean()
        data = self.cleaned_data

        form_email = data.get('email')

        return data


class TrackProductForm(forms.Form):
    """
    Please note we'll only display the RateTracker Date if the product has Bonus values.
    """
    track = forms.BooleanField(widget=forms.HiddenInput(), initial=True, required=False)
    sc_code = forms.CharField(widget=forms.HiddenInput())


    def __init__(self, product=None, *args, **kwargs):
        super(TrackProductForm, self).__init__(*args, **kwargs)
        self._product = product

        if product:
            self.fields['sc_code'].initial = product.sc_code
            if self._is_trackable_with_date(product):
                self.fields['ratetracker_date'] = forms.DateField(required=False,
                                                                  widget=forms.TextInput(attrs={'class': 'datepicker'}),
                                                                  label="Please let us know when you opened the account")

    def _is_trackable_with_date(self, product):
        return product.bonus_amount > 0 and product.bonus_term != None


class BestBuyForm(forms.Form):
    initial_deposit = CurrencyField(widget=CurrencyInput(attrs={'class': 'text'}), required=False,
                                    initial=Decimal('0.00'))

    def __init__(self, *args, **kwargs):
        super(BestBuyForm, self).__init__(*args, **kwargs)
        self.is_over_threshold = False

    def clean(self):
        data = self.cleaned_data
        initial_deposit = data.get('initial_deposit', 0)
        self.is_over_threshold = initial_deposit > BESTBUY_THRESHOLD

        return data


class GenericBestBuyForm(BestBuyForm):
    """ 
    Easy Access, Notice Accounts, Over 50s
    """
    monthly_deposit = CurrencyField(widget=CurrencyInput(attrs={'class': 'text'}), required=False,
                                    initial=Decimal('0.00'))
    tax_rate = forms.ChoiceField(choices=ACCOUNT_TYPE_CHOICES, required=False)

    def clean(self):
        """
        At least the initial deposity or the monthly deposit have to have a value
        """
        super(GenericBestBuyForm, self).clean()
        data = self.cleaned_data
        monthly = data.get('monthly_deposit', 0)
        initial = data.get('initial_deposit', 0)
        if monthly in EMPTY_VALUES:
            data['monthly_deposit'] = 0

        if initial in EMPTY_VALUES:
            data['initial_deposit'] = 0

        if monthly <= 0 and initial <= 0:
            self._errors["initial_deposit"] = self.error_class(["Please enter a monthly or initial deposit"])
            raise forms.ValidationError("Please enter a value for the Best Buy Tool")
        return data


class FixedRateBondsBestBuysForm(BestBuyForm):
    tax_rate = forms.ChoiceField(choices=ACCOUNT_TYPE_CHOICES, required=False)


class VariableCashISABestBuyForm(BestBuyForm):
    monthly_deposit = CurrencyField(widget=CurrencyInput(attrs={'class': 'text'}), required=False,
                                    initial=Decimal('0.00'))


class FixedRateCashISABestBuyForm(BestBuyForm):
    pass


class ChildrensAccountForm(BestBuyForm):
    monthly_deposit = CurrencyField(widget=CurrencyInput(attrs={'class': 'text'}), required=False,
                                    initial=Decimal('0.00'))


class RegularSavingsAccountForm(forms.Form):
    monthly_deposit = CurrencyField(widget=CurrencyInput(attrs={'class': 'text'}), required=True,
                                    initial=Decimal('0.00'))
    tax_rate = forms.ChoiceField(choices=ACCOUNT_TYPE_CHOICES, required=False)


class MonthlyIncomeAccountForm(BestBuyForm):
    tax_rate = forms.ChoiceField(choices=ACCOUNT_TYPE_CHOICES, required=False)
    pass


class ProductPortfolioForm(forms.ModelForm):
    ratetracker_date = forms.CharField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = ProductPortfolio
        exclude = ('product',)


class ProductReminderForm(forms.ModelForm):
    track_me = forms.BooleanField(widget=forms.HiddenInput, required=False, initial=True)
    search = forms.BooleanField(widget=forms.HiddenInput, required=False, initial=True)
    opening_date = forms.DateField(widget=MonthYearWidget(years=_get_years(), attrs={'class': 'required', 'min': '1'}),
                                   required=False)

    class Meta:
        model = ProductPortfolio
        exclude = ('user', )
        widgets = {
            'provider': forms.HiddenInput,
            'account_type': forms.HiddenInput,
            'product': forms.HiddenInput,
            'balance': forms.HiddenInput,
            'bonus_term': forms.HiddenInput,
            'notice': forms.HiddenInput,
            'user': forms.HiddenInput,
        }

    def clean(self):
        user = self.cleaned_data.get('user', None)
        if user:
            try:
                ProductPortfolio.objects.get(user=self.cleaned_data['user'],
                                             product=self.cleaned_data['product'],
                                             is_deleted=False)

                raise forms.ValidationError("You have already this product")

            except ProductPortfolio.DoesNotExist:
                pass

        product = self.cleaned_data.get('product', None)
        if product.show_opening_date():
            opening_date = self.cleaned_data.get('opening_date', None)
            if opening_date in EMPTY_VALUES:
                self.errors['opening_date'] = 'Please enter an opening date'
                raise forms.ValidationError('Please enter an opening date')

        return self.cleaned_data


class Deleter_ProductReminderForm(forms.ModelForm):
    is_synched = forms.BooleanField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = ProductPortfolio
        fields = ('id', 'is_deleted', 'is_synched')

    def clean(self):
        is_deleted = self.cleaned_data.get('is_deleted', False)

        if is_deleted:
            self.cleaned_data['is_synched'] = False

        return self.cleaned_data


class Deleter_TrackerReminderForm(forms.ModelForm):
    is_synched = forms.BooleanField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = RatetrackerReminder
        fields = ('id', 'is_deleted', 'is_synched')

    def clean(self):
        is_deleted = self.cleaned_data.get('is_deleted', False)

        if is_deleted:
            self.cleaned_data['is_synched'] = False

        return self.cleaned_data


class TrackerReminderForm(forms.ModelForm):
    remind_me = forms.BooleanField(widget=forms.HiddenInput, required=False, initial=True)
    maturity_date = forms.DateField(widget=MonthYearWidget(years=_get_maturity_years()))

    def __init__(self, *args, **kwargs):
        super(TrackerReminderForm, self).__init__(*args, **kwargs)
        self.message_key = None

    class Meta:
        model = RatetrackerReminder
        exclude = ('user',)
        widgets = {
            'provider': forms.HiddenInput,
            'account_type': forms.HiddenInput,
            'balance': forms.HiddenInput,
        }


PortfolioFormset = modelformset_factory(ProductPortfolio, form=Deleter_ProductReminderForm, extra=0, can_delete=False)
ReminderFormset = modelformset_factory(RatetrackerReminder, form=Deleter_TrackerReminderForm, extra=0, can_delete=False)


class ContactForm(forms.Form):
    subject = forms.CharField(max_length=100)
    message = forms.CharField()
    sender = forms.EmailField()
    cc_myself = forms.BooleanField(required=False)


class TIMFixedRegistrationForm(forms.Form):
    """ When the user is searching if they specify a Fixed Rate Bond type, 
    the Account Name is not applicable and not required. 
    """
    attrs_dict = {'required': ''}
    provider = forms.ModelChoiceField(
        Provider.objects.all().exclude(title="Kent Reliance Building Society").exclude(title="Sainsbury's Finance"),
        empty_label='Provider', widget=forms.Select(attrs={'class': 'number'}),
        required=False
    )
    account_type = forms.ChoiceField(widget=forms.Select(attrs={'class': 'number'}),
                                     choices=_get_rt_account_type_choices(),
                                     required=False
    )

    balance = CurrencyField(widget=CurrencyInput(attrs={'class': 'text commaNumber'}), initial=Decimal('1'),
                            required=False
    )

    maturity_date = forms.DateField(widget=MonthYearWidget(years=_get_maturity_years(), attrs={'min': '1'}),
                                    required=False)

    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'required email'}), required=True)
    password1 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
                                label="Password")
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'required'}), max_length=100)
    surname = forms.CharField(widget=forms.TextInput(attrs={'class': 'required'}), max_length=100)
    newsletter = forms.BooleanField(label="I would like to receive the Savings Champion newsletter", required=False,
                                    initial=True)
    ratealerts = forms.BooleanField(label="I would like to receive the Savings Champion Rate Alerts email",
                                    required=False, initial=True)

    source = forms.CharField(required=False, widget=forms.HiddenInput())

    username = forms.CharField(label="Username",
                               max_length=30,
                               min_length=6,
                               widget=forms.HiddenInput(),
                               required=False)

    helper = FormHelper()
    helper.add_input(Submit('Submit', 'Submit', src=static('img/register.png'), type='image'))

    def __init__(self, *args, **kwargs):
        super(TIMFixedRegistrationForm, self).__init__(*args, **kwargs)
        self.helper.form_action = reverse('tim_fixed_register')

    def clean_username(self):
        return MakeUsername()

    def save(self, request):
        email = self.cleaned_data('email')
        user, user_created, record_stats = create_stage_one_profile(request, email=email, source=self.cleaned_data.get('source'))

        tim_signup, _ = TiMSignups.objects.get_or_create(email=user.email)
        user.profile.newsletter = self.cleaned_data.get('newsletter', False)
        user.profile.ratealerts = self.cleaned_data.get('ratealerts', False)

        if RateAlertsSignup.objects.filter(email=user.email).exists():
            user.profile.ratealerts = True
        if NewsletterSignup.objects.filter(email=user.email).exists():
            user.profile.newsletter = True

        user.profile.is_synched = False
        user.profile.skeleton_user = False

        user.profile.save()

        # add the fixed rate product
        provider = request.POST['provider']
        balance = request.POST['balance']
        account_type = request.POST['account_type']
        if account_type != '' and provider != '' and balance != '':
            bestbuy = BestBuy.objects.get(id=account_type)
            reminder = RatetrackerReminder()
            reminder.user = user
            reminder.account_type = bestbuy
            reminder.balance = balance
            reminder.provider = Provider.objects.get(id=provider)
            if 'maturity_date_month' not in request.POST and 'maturity_date_year' not in request.POST:
                product = Product.objects.get(pk=request.POST['product'])
                product_term = product.term if product.term is not None else 0
                month = int(request.POST['opening_date_month'])
                year = int(request.POST['opening_date_year'])
                maturity_date = datetime.date(day=1,
                                              month=month,
                                              year=year) + datetime.timedelta(days=product_term)
            else:
                month = int(request.POST['maturity_date_month'])
                year = int(request.POST['maturity_date_year'])
                maturity_date = datetime.date(day=1,
                                              month=month,
                                              year=year)
            reminder.maturity_date = maturity_date
            reminder.is_synched = False
            reminder.save()
        return user

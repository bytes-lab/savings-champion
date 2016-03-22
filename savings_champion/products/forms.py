# coding=utf-8
from crispy_forms.bootstrap import PrependedText, AppendedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from django.db import ProgrammingError
from django.forms.fields import IntegerField
from django_select2.forms import ModelSelect2Widget
from tinymce.widgets import TinyMCE
from decimal import *
from django import forms
from django.conf import settings
from django.forms.models import modelformset_factory
from common.widgets import MonthYearWidget
from products.fields import CurrencyField, CurrencyInput
from products.models import Provider, Product, ProductPortfolio, BestBuy, RatetrackerReminder, WeeklyRateAlert, \
    EMAIL_TIMEFRAME, WeeklyBusinessRateAlert
from products.utils import get_maturity_based_bestbuys, get_ISA_bestbuys
from common.html5inputs import *
import datetime

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
            'comparison_meta_description': forms.Textarea,
            'tips': TinyMCE
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
    return range(now.year, now.year + 15, 1)


def _get_rt_account_type_choices():

    retval = [('', 'Select savings type')]
    vals = BestBuy.objects.values('id', 'title').order_by('title')
    try:
        for val in vals:
            retval.append([val['id'], val['title']])
    except ProgrammingError:  # Typically appears during deployment when model tables do not exist yet.
        pass
    retval.append(('unknown', 'I don\'t know'))
    return retval



def _get_isa_account_type_choices():
    vals = get_ISA_bestbuys().values('id', 'title').order_by('title')
    retval = [('', 'Select account type')]
    try:
        for val in vals:
            retval.append([val['id'], val['title']])
    except ProgrammingError:  # Typically appears during deployment when model tables do not exist yet.
        pass
    retval.append(('unknown', 'I don\'t know'))
    return retval


def _get_fixed_bestbuys():
    bestbuys = BestBuy.objects.filter(is_fixed=True).values('id', 'title')
    choices = [(0, 'Please Select An Option')]
    try:
        for bestbuy in bestbuys:
            choices.append([bestbuy['id'], bestbuy['title']])
    except ProgrammingError:  # Typically appears during deployment when model tables do not exist yet.
        pass
    return choices


class RateTrackerForm(forms.Form):
    """ When the user is searching if they specify a Fixed Rate Bond type, 
    the Account Name is not applicable and not required. 
    """
    provider = forms.ModelChoiceField(
        Provider.objects.all().exclude(title="Kent Reliance Building Society").exclude(title="Sainsbury's Finance"),
        empty_label='Select provider', widget=forms.Select(attrs={'class': 'required number'}))
    account_type = forms.ChoiceField(widget=forms.Select(attrs={'class': 'required number'}),
                                     choices=_get_rt_account_type_choices())

    balance = CurrencyField(widget=CurrencyInput(attrs={'class': 'text commaNumber'}), initial=1,
                            help_text='Your interest rate changes depending upon the account balance.')
    product = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'text', 'min': '1'}), required=False)

    maturity_date = forms.DateField(
        widget=MonthYearWidget(
            years=_get_maturity_years()),
        required=False)
    opening_date = forms.DateField(
        widget=MonthYearWidget(
            years=_get_years()),
        required=False)

    def __init__(self, *args, **kwargs):
        super(RateTrackerForm, self).__init__(*args, **kwargs)
        self.set_reminder = False
        self.high_balance = False
        self.opening_date_required = False

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
                return
            try:
                if Product.objects.get(pk=product).show_opening_date():
                    opening_date = self.cleaned_data.get('opening_date', None)
                    if opening_date in EMPTY_VALUES:
                        self.opening_date_required = True
                        self.errors['opening_date'] = 'Please enter an opening date'
                        raise forms.ValidationError('Please enter an opening date')
            except Product.DoesNotExist:
                self.errors['product'] = 'Please choose an Account Name'
                return

        if balance in EMPTY_VALUES or balance <= 0:
            self.errors['balance'] = 'Please enter your balance'
        return data


def _get_provider_isa_best_buys():
    return Provider.objects.filter(providerbestbuy__bestbuys__in=get_ISA_bestbuys()).distinct()



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
    opening_date = forms.DateField(widget=MonthYearWidget(years=_get_years()), required=False)

    class Meta:
        model = ProductPortfolio
        exclude = ('product',)


class ProductReminderForm(forms.ModelForm):
    track_me = forms.BooleanField(widget=forms.HiddenInput, required=False, initial=True)
    search = forms.BooleanField(widget=forms.HiddenInput, required=False, initial=True)
    opening_date = forms.DateField(widget=MonthYearWidget(years=_get_years()), required=False)

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


class PortfolioEditForm(forms.Form):
    id = forms.IntegerField(widget=forms.HiddenInput(attrs={'class': 'portfolioeditid'}), required=True)
    balance = CurrencyField(
        widget=CurrencyInput(attrs={'class': 'commaNumber minComma editbalance form-control', 'min': 1}))

    def clean(self):
        balance = self.cleaned_data.get('balance', False)
        if balance < 1:
            return False

        return self.cleaned_data

    def __init__(self):
        super(PortfolioEditForm, self).__init__()
        self.form_helper = FormHelper()
        self.form_helper.form_tag = False
        self.form_helper.layout = Layout(
            'id',
            PrependedText('balance', '£')
        )


class ReminderEditForm(PortfolioEditForm):
    id = forms.IntegerField(widget=forms.HiddenInput(attrs={'id': 'reminder_id'}), required=True)
    balance = forms.DecimalField(max_digits=3, decimal_places=2, widget=forms.NumberInput(attrs={'id': 'reminder_balance'}))
    rate = forms.DecimalField(max_digits=3, decimal_places=2,)

    def __init__(self):
        super(ReminderEditForm, self).__init__()
        self.form_helper = FormHelper()
        self.form_helper.form_tag = False
        self.form_helper.layout = Layout(
            'id',
            PrependedText('balance', '£'),
            AppendedText('rate', '%'),
        )


PortfolioFormset = modelformset_factory(ProductPortfolio, form=Deleter_ProductReminderForm, extra=0, can_delete=False)
ReminderFormset = modelformset_factory(RatetrackerReminder, form=Deleter_TrackerReminderForm, extra=0, can_delete=False)


class AddProductsForm(forms.Form):
    provider = forms.ModelChoiceField(queryset=Provider.objects.all(),
                                      empty_label='Select provider',
                                      widget=ModelSelect2Widget(attrs={'class': 'providerselect',
                                                                       'style': 'width:100%!important;',
                                                                       'required': True},
                                                                search_fields=['title']),
                                      required=True)
    balance = forms.DecimalField(max_digits=14, decimal_places=2, required=True)
    product = IntegerField(
        widget=forms.Select(attrs={'class': 'text productselect', 'min': '1', 'style': 'width:100%!important;',
                                   'required': True}), required=True)
    opening_date = forms.DateField(widget=MonthYearWidget(attrs={'required': True},
                                                          years=_get_years()),
                                   required=True)

    def __init__(self, *args, **kwargs):
        super(AddProductsForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            u'provider',
            PrependedText(u'balance', u'£', placeholder=1),
            u'product',
            u'opening_date'
        )


class AddFixedProductForm(forms.Form):
    fixed_provider = forms.ModelChoiceField(queryset=Provider.objects.all(), empty_label='Select provider',
                                       widget=ModelSelect2Widget(attrs={'class': 'required number fixedproviderselect',
                                                                  'style': 'width:100%!important;'}, search_fields=['title']),
                                       label="Provider", required=True)
    account_type = forms.ChoiceField(choices=_get_fixed_bestbuys(),
                                     widget=forms.Select(attrs={'class': 'required number account-type form-control', 'min': '1',
                                                                'style': 'width:100%!important;',
                                                                'required': True}), required=True)
    balance = CurrencyField(widget=CurrencyInput(attrs={'class': 'text commaNumber form-control',
                                                        'style': 'width:100%!important;',
                                                        'required': True}), initial=1, required=True)
    rate = forms.DecimalField(widget=forms.NumberInput(attrs={'class': 'form-control', 'required': True}), max_digits=3, decimal_places=2, initial=0, required=True)
    maturity_date = forms.DateField(
        widget=MonthYearWidget(attrs={'class': 'number datestyle form-control', 'min': '1', 'required': True}, years=_get_maturity_years()),
        required=True)

    def clean(self):
        return self.cleaned_data

    def __init__(self, *args, **kwargs):
        super(AddFixedProductForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            u'fixed_provider',
            u'account_type',
            PrependedText(u'balance', u'£', placeholder=1),
            u'rate',
            u'maturity_date'
        )


class AddOpeningDateForm(forms.Form):
    portfolio_id = forms.IntegerField(widget=forms.HiddenInput(attrs={'class': 'portfolio_id'}), required=True)
    opening_date = forms.DateField(
        widget=MonthYearWidget(attrs={'class': 'number datefield', 'min': '1'}, years=_get_years()), required=False)

    def clean(self):
        return self.cleaned_data


class EmailInstructionsForm(forms.Form):
    formattrs = {'required': '',
                 'autofocus': '',
                 'class': 'email',
                 'placeholder': 'Enter your email address'}
    email = forms.EmailField(widget=Html5EmailInput(attrs=dict(formattrs, maxlength=75)),
                             label="Email")


class WeeklyRateAlertsForm(forms.ModelForm):
    frequency = forms.ChoiceField(widget=forms.RadioSelect(), choices=EMAIL_TIMEFRAME, initial=2, label='')
    email = forms.EmailField(widget=Html5EmailInput(attrs={'maxlength': 75,
                                                           'placeholder': 'Enter your email'}), label='')

    class Meta:
        model = WeeklyRateAlert
        fields = ('frequency', 'email', )

    def __init__(self, *args, **kwargs):
        super(WeeklyRateAlertsForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-inline'
        self.helper.field_template = 'bootstrap3/layout/inline_field.html'
        self.helper.form_tag = False


class WeeklyBusinessRateAlertsForm(forms.ModelForm):
    frequency = forms.ChoiceField(widget=forms.RadioSelect(), choices=EMAIL_TIMEFRAME, initial=2, label='')
    email = forms.EmailField(widget=Html5EmailInput(attrs={'maxlength': 75,
                                                           'placeholder': 'Enter your email'}), label='')

    class Meta:
        model = WeeklyBusinessRateAlert
        fields = ('frequency', 'email', )

    def __init__(self, *args, **kwargs):
        super(WeeklyBusinessRateAlertsForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-inline'
        self.helper.field_template = 'bootstrap3/layout/inline_field.html'
        self.helper.form_tag = False

class RateTrackerThresholdForm(forms.Form):
    amount = forms.DecimalField(max_digits=16, decimal_places=2)

    def __init__(self, *args, **kwargs):
        super(RateTrackerThresholdForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-inline'
        self.helper.field_template = 'bootstrap3/layout/inline_field.html'
        self.helper.layout = Layout(
            PrependedText('amount', '&pound;')
        )


class BestBuyCallbackForm(forms.Form):
    name = forms.CharField()
    phone = forms.CharField()
    email = forms.EmailField()

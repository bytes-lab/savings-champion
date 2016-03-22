import datetime
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Div, Button

from django import forms
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.db import ProgrammingError
from django_select2.forms import ModelSelect2Widget

from common.html5inputs import *
from common.models import Referrer, UserReferral
from products.models import Provider, BestBuy, Ranking, Product
from products.fields import CurrencyField, CurrencyInput
from common.widgets import MonthYearWidget

User = get_user_model()


def _get_years():
    now = datetime.datetime.now()
    return range(now.year, 1990, -1)


def _get_fixed_bestbuys():
    bestbuys = BestBuy.objects.filter(is_fixed=True).values('id', 'title')
    choices = [(0, 'Please Select An Option')]
    try:
        for bestbuy in bestbuys:
            choices.append([bestbuy['id'], bestbuy['title']])
    except ProgrammingError:
        pass
    return choices


def _get_maturity_years():
    now = datetime.datetime.now()
    return range(now.year, now.year + 10, 1)


class sccodeForm(forms.Form):
    sccode = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    oldsccode = forms.CharField(widget=forms.HiddenInput(), required=False)


class AddProductsForm(forms.Form):
    formattrs = {'required': '',
                 'class': 'email',
                 'placeholder': 'Enter your email address'}
    email = forms.EmailField(widget=Html5EmailInput(attrs=dict(formattrs, maxlength=75)),
                             label="Email")
    provider = forms.ModelChoiceField(Provider.objects.all(), empty_label='Select provider',
                                      widget=forms.Select(attrs={'class': 'required number providerselect'}))
    balance = CurrencyField(widget=CurrencyInput(attrs={'class': 'text commaNumber balanceinput'}), initial=1)
    product = forms.IntegerField(widget=forms.Select(attrs={'class': 'text productselect', 'min': '1'}), required=False)
    opening_date = forms.DateField(widget=MonthYearWidget(attrs={'class': 'number datefield'}, years=_get_years()),
                                   required=False)

    def __init__(self, *args, **kwargs):
        super(AddProductsForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.field_class = 'col-lg-8'
        self.helper.label_class = 'col-lg-4'
        self.helper.form_class = 'form-horizontal'
        self.helper.form_tag = False
        self.helper.add_input(Submit(name='add_product', value='Add Product'))

    def clean(self):
        return self.cleaned_data


class AddFixedProductForm(forms.Form):
    formattrs = {'required': '',
                 'class': 'email',
                 'placeholder': 'Enter your email address'}
    email = forms.EmailField(widget=Html5EmailInput(attrs=dict(formattrs, maxlength=75)), label="Email", required=True)
    fixed_provider = forms.ModelChoiceField(Provider.objects.all(), empty_label='Select provider',
                                            widget=forms.Select(attrs={'class': 'required number fixedproviderselect'}),
                                            label="Provider")
    account_type = forms.ChoiceField(choices=_get_fixed_bestbuys(),
                                     widget=forms.Select(attrs={'class': 'required number account-type'}))
    balance = CurrencyField(widget=CurrencyInput(attrs={'class': 'text commaNumber'}), initial=1)
    rate = forms.DecimalField(widget=CurrencyInput(attrs={'class': 'text commaNumber'}), initial=0, max_digits=3,
                              decimal_places=2)
    maturity_date = forms.DateField(
        widget=MonthYearWidget(attrs={'class': 'number datefield', 'min': '1'}, years=_get_maturity_years()),
        required=True)

    def __init__(self, *args, **kwargs):
        super(AddFixedProductForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.field_class = 'col-lg-8'
        self.helper.label_class = 'col-lg-4'
        self.helper.form_class = 'form-horizontal'
        self.helper.form_tag = False
        self.helper.add_input(Submit(name='add_product', value='Add Product'))

    def clean(self):
        return self.cleaned_data


class EmailForm(forms.Form):
    formattrs = {'required': '',
                 'class': 'email',
                 'placeholder': 'Enter your email address'}
    email = forms.EmailField(widget=Html5EmailInput(attrs=dict(formattrs, maxlength=75)),
                             label="Email")

    def clean(self):
        return self.cleaned_data

def best_buy_add_choices():
    bestbuys = []
    for bestbuy in BestBuy.objects.all():
        bestbuys.append((bestbuy.pk, "{bestbuy} - {client_type}".format(bestbuy=bestbuy.title, client_type=bestbuy.get_client_type_display())))
    return tuple(bestbuys)

class BestBuySelect(forms.ModelChoiceField):

    def label_from_instance(self, obj):
        return "{bestbuy} - {client_type}".format(bestbuy=obj.title, client_type=obj.get_client_type_display())

class ProductChoices(ModelSelect2Widget):
    search_fields = ['title__icontains', 'sc_code__icontains']

class BestBuyAddForm(forms.ModelForm):

    product = forms.ModelChoiceField(queryset=Product.objects.filter(deleted=False), widget=ProductChoices(attrs={'style': 'width: 100%;'}))
    bestbuy = BestBuySelect(queryset=BestBuy.objects, widget=forms.Select())

    class Meta:
        model = Ranking
        exclude = ('hidden', 'date_replaced')

    def __init__(self, *args, **kwargs):
        super(BestBuyAddForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False


class ChangePortfolioForm(forms.Form):
    id = forms.IntegerField(widget=forms.TextInput(), required=True)
    new_sc_code = forms.CharField(widget=forms.TextInput(), required=True)
    opening_date = forms.DateField(widget=MonthYearWidget(attrs={'class': 'number datefield'}, years=_get_years()),
                                   required=False)

    def clean(self):
        return self.cleaned_data


class ChangeEmailForm(forms.Form):
    formattrs = {'required': '',
                 'class': 'email',
                 'placeholder': 'Enter your email address'}
    old_email = forms.EmailField(widget=Html5EmailInput(attrs=dict(formattrs, maxlength=75)), required=True)
    new_email = forms.EmailField(widget=Html5EmailInput(attrs=dict(formattrs, maxlength=75)), required=True)

    def clean(self):
        data = self.cleaned_data
        form_email = data.get('new_email', None)
        old_email = data.get('old_email', None)

        if form_email != old_email:
            if User.objects.filter(email=form_email).exists():
                raise forms.ValidationError("This email is already in use")

        return self.cleaned_data


class ConciergeForm(forms.Form):
    formattrs = {'required': '',
                 'class': 'email',
                 'placeholder': 'Enter your email address'}
    email = forms.EmailField(widget=Html5EmailInput(attrs=dict(formattrs, maxlength=75)), required=True)
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'required'}), max_length=100, required=True)
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'required'}), max_length=100, required=True)
    number = forms.CharField(required=True, max_length=40)

    def clean(self):
        return self.cleaned_data


class ChangePasswordForm(forms.Form):
    formattrs = {'required': '',
                 'class': 'email',
                 'placeholder': 'Enter your email address'}
    email = forms.EmailField(widget=Html5EmailInput(attrs=dict(formattrs, maxlength=75)), required=True)
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'required', 'required': ''}, render_value=False), required=True,
        label="New Password")
    active = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': 'checkbox'}), required=False, initial=True)

    def clean(self):
        return self.cleaned_data


class UnsubscribeForm(forms.Form):
    formattrs = {'required': 'true',
                 'class': 'email',
                 'placeholder': 'Enter clients email address'}
    email = forms.EmailField(widget=Html5EmailInput(attrs=dict(formattrs, maxlength=75)), required=True)


class RemoveUserForm(forms.Form):
    email = forms.EmailField(widget=Html5EmailInput())

    def __init__(self, *args, **kwargs):
        super(RemoveUserForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit(name='delete', value='Delete this user', css_class='btn btn-danger'))


class RemoveConciergeClientForm(forms.Form):
    email = forms.EmailField(widget=Html5EmailInput())

    def __init__(self, *args, **kwargs):
        super(RemoveConciergeClientForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('remove_concierge_client')
        self.helper.add_input(
            Submit(name='Remove from Concierge', value='Remove from Concierge', css_class='btn btn-danger'))


class SyncUserForm(forms.Form):
    email = forms.EmailField(widget=Html5EmailInput())

    def __init__(self, *args, **kwargs):
        super(SyncUserForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit(name='sync', value='Force resync', css_class='btn btn-danger'))


referral_action_with_blank = ((None, '---------'),) + UserReferral.REFERRAL_ACTION_CHOICES


class ReferrerForm(forms.Form):
    referrer = forms.ModelChoiceField(queryset=Referrer.objects.all(), required=False, widget=ModelSelect2Widget(model=Referrer, search_fields=['name__icontains']))
    action = forms.ChoiceField(choices=referral_action_with_blank, required=False)
    start_date = forms.DateTimeField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    end_date = forms.DateTimeField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)

    def __init__(self, *args, **kwargs):
        super(ReferrerForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('referral_reporting')
        self.helper.add_input(Submit('Filter', 'Filter'))
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-4'
        self.helper.field_class = 'col-lg-8'
        self.helper.layout = Layout(
            Div(
                Div(
                    'referrer',
                    css_class='col-md-6',
                ),
                Div(
                    'action',
                    css_class='col-md-6',
                ),

                css_class='row',
            ),
            Div(
                Div(
                    'start_date',
                    css_class='col-md-6'
                ),
                Div(
                    'end_date',
                    css_class='col-md-6'
                ),
                css_class='row'
            )
        )

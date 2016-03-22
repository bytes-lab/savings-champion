# -*- coding: utf-8 -*-
from crispy_forms.bootstrap import StrictButton
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout
from django import forms
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.core.urlresolvers import reverse
from django.db import ProgrammingError
from django.forms.extras.widgets import SelectDateWidget
from django.contrib.auth import authenticate, get_user_model
from django.utils.safestring import mark_safe
from django_select2.forms import Select2Widget, ModelSelect2Widget
from common.html5inputs import Html5EmailInput
from products.models import Provider, BestBuy
from products.fields import CurrencyField, CurrencyInput
from common.widgets import MonthYearWidget
import datetime

User = get_user_model()


def _get_years():
    now = datetime.datetime.now()
    return range(now.year, 1900, -1)


def _get_full_dob_years():
    now = datetime.datetime.now()
    year_range = range(now.year, 1900, -1)
    choices = [(0, '---')]
    for year in year_range:
        choices.append([year, year])
    return choices


def _get_opening_years():
    now = datetime.datetime.now()
    return range(now.year, 1990, -1)


def _get_maturity_years():
    now = datetime.datetime.now()
    return range(now.year, now.year + 10, 1)


def _get_fixed_bestbuys():
    bestbuys = BestBuy.objects.filter(is_fixed=True).values('id', 'title')
    choices = [(0, 'Please Select An Option')]
    try:
        for bestbuy in bestbuys:
            choices.append([bestbuy['id'], bestbuy['title']])
    except ProgrammingError:
        pass
    return choices


attrs_dict = {'required': ''}
SALUTATION_CHOICES = (('Mr', 'Mr'), ('Mrs', 'Mrs'), ('Miss', 'Miss'), ('Ms', 'Ms'), ('Dr', 'Dr'))

EMPTY_VALUES = ['', ' ', None]


class SCRegistrationForm(forms.Form):
    uuid = forms.CharField(max_length=255, required=False, widget=forms.HiddenInput)

    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'required email', "maxlength": "75"}),
                             label="E-mail Address")

    email2 = forms.EmailField(widget=forms.TextInput(attrs=dict(attrs_dict,
                                                                maxlength=75)),
                              label="Confirm E-mail Address")

    password1 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
                                label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
                                label="Confirm Password")

    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'required'}), max_length=100)
    surname = forms.CharField(widget=forms.TextInput(attrs={'class': 'required'}), max_length=100)
    salutation = forms.ChoiceField(choices=SALUTATION_CHOICES)

    telephone = forms.CharField(required=False)
    dob = forms.DateField(widget=SelectDateWidget(years=_get_years()), label="Date of birth", required=False)
    postcode = forms.CharField(required=False)
    newsletter = forms.BooleanField(label="I would like to receive the Savings Champion newsletter", required=False,
                                    initial=True)
    ratealerts = forms.BooleanField(label="I would like to receive the Savings Champion Rate Alerts email",
                                    required=False, initial=True)

    source = forms.CharField(required=False)

    helper = FormHelper()

    def clean(self):
        super(SCRegistrationForm, self).clean()
        data = self.cleaned_data

        email = data.get('email', None)
        email2 = data.get('email2', None)

        if ((email in EMPTY_VALUES) or (email2 in EMPTY_VALUES)):
            self.errors['email'] = 'Please enter your email address'
            return
        if (email != email2):
            self.errors['email2'] = 'Please confirm your email address'
            return
        if User.objects.filter(email=email2).exists():
            if not User.objects.filter(email=email2)[0].profile.skeleton_user:
                self.errors['email'] = 'This email is already associated with a user account'
                return
        return data


class TIMRegistrationForm(SCRegistrationForm):
    def clean(self):
        data = self.cleaned_data

        email = data.get('email', None)
        email2 = data.get('email2', None)
        if User.objects.filter(email=email2).exists():
            if not User.objects.filter(email=email2)[0].profile.skeleton_user:
                self.errors['email'] = 'This email is already associated with a user account'
                return
        return data


class AuthenticationForm(forms.Form):
    """
    Base class for authenticating users. Extend this to get a form that accepts
    username/password logins.
    """
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(attrs_dict,
                                                               maxlength=75)),
                             label="E-mail Address")
    password = forms.CharField(label="Password",
                               widget=forms.PasswordInput,
                               required=False)

    redirect_to = forms.CharField(widget=forms.HiddenInput(), required=False)

    def __init__(self, request=None, *args, **kwargs):
        """
        If request is passed in, the form will validate that cookies are
        enabled. Note that the request (a HttpRequest object) must have set a
        cookie with the key TEST_COOKIE_NAME and value TEST_COOKIE_VALUE before
        running this validation.
        """
        self.request = request
        self.user_cache = None
        super(AuthenticationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('Sign In', 'Sign In', css_class='btn btn-success pull-right'))


    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(email=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    "Please enter a correct e-mail address and password. Note that both fields are case-sensitive.")
            if not self.user_cache.is_active:
                raise forms.ValidationError(
                    mark_safe("This account is inactive. <a href='{activation_url}'>Resend my activation email</a>".format(
                        activation_url=reverse('resend_activation'))))
        elif email:
            raise forms.ValidationError(
                "Please enter your e-mail address.")
        elif password:
            raise forms.ValidationError(
                "Please enter your password.")
        else:
            raise forms.ValidationError(
                "Please enter your email address and your password.")

        self.check_for_test_cookie()
        return self.cleaned_data

    def check_for_test_cookie(self):
        if self.request and not self.request.session.test_cookie_worked():
            raise forms.ValidationError(
                "Your Web browser doesn't appear to have cookies enabled. "
                "Cookies are required for logging in.")

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    def get_user(self):
        return self.user_cache


class GetEmailFromUsername(forms.Form):
    username = forms.RegexField(regex=r'^[\w.@+-]+$',
                                max_length=30,
                                widget=forms.TextInput(attrs=attrs_dict),
                                label="Username",
                                error_messages={
                                    'invalid': "This value must contain only letters, numbers and underscores."})

    password = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
                               label="Password")


class SignUpForm(forms.Form):
    formattrs = {'required': '',
                 'type': 'email',
                 'class': 'email form-control',
                 'placeholder': 'Enter your email address'}
    email = forms.EmailField(widget=Html5EmailInput(attrs=dict(formattrs, maxlength=75)),
                             label=" ", )

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-4'
        self.helper.field_class = 'col-lg-8'
        self.helper.add_input(Submit('submit', 'Take the One Minute Healthcheck'))


class IndexSignupform(SignUpForm):
    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.form_action = reverse('healthcheck_basket_signup')
        self.helper.layout = Layout(
            'email',
            StrictButton('Choose your free services <span class="glyphicon glyphicon-chevron-right"></span>',
                         css_class="btn btn-savchamp js-index-submit"),
        )


class HealthcheckSignUpForm(SignUpForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'required form-control', 'max_length': 100}))
    surname = forms.CharField(widget=forms.TextInput(attrs={'class': 'required form-control', 'max_length': 100}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'text required form-control'}), required=True)
    telephone = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'max_length': 100}),
                                required=False)
    provider = forms.ModelChoiceField(queryset=Provider.objects.all(), empty_label='Select provider', required=False,
                                 widget=ModelSelect2Widget(
                                     attrs={'class': 'number providerselect', 'style': 'width:100%!important;'}))
    balance = CurrencyField(widget=CurrencyInput(
        attrs={'class': 'commaNumber balanceinput form-control', 'style': 'width:100%!important;'}), required=False,
                            initial=1)
    product = forms.IntegerField(
        widget=Select2Widget(attrs={'class': 'text productselect', 'min': '1', 'style': 'width:100%!important;'}),
        required=False)
    opening_date = forms.DateField(
        widget=MonthYearWidget(attrs={'class': 'datestyle number', 'min': '1'}, years=_get_opening_years()),
        required=False)
    extra_field_count = forms.CharField(widget=forms.HiddenInput())
    maturity_date = forms.DateField(
        widget=MonthYearWidget(attrs={'class': 'datestyle number', 'min': '1'}, years=_get_maturity_years()),
        required=False)
    account_type = forms.ChoiceField(
        widget=Select2Widget(attrs={'class': 'accounttype number', 'style': 'width:100%!important;'}),
        choices=_get_fixed_bestbuys(), required=False)
    is_fixed = forms.BooleanField(widget=forms.HiddenInput(attrs={'class': 'fixedindicator'}), required=False)

    def __init__(self, *args, **kwargs):
        extra_fields = kwargs.pop('extra', 0)
        super(HealthcheckSignUpForm, self).__init__(*args, **kwargs)
        self.fields['extra_field_count'].initial = extra_fields
        for index in xrange(int(extra_fields)):
            self.fields['provider_field_%i' % index] = forms.IntegerField(required=False)
            self.fields['balance_field_%i' % index] = CurrencyField(
                widget=CurrencyInput(attrs={'class': 'commaNumber balanceinput form-control'}), required=False,
                initial=1)
            self.fields['product_field_%i' % index] = forms.IntegerField(required=False)
            self.fields['opening_date_month_field_%i' % index] = forms.IntegerField(required=False)
            self.fields['opening_date_year_field_%i' % index] = forms.IntegerField(required=False)
            self.fields['maturity_date_month_field_%i' % index] = forms.IntegerField(required=False)
            self.fields['maturity_date_year_field_%i' % index] = forms.IntegerField(required=False)
            self.fields['account_type_field_%i' % index] = forms.IntegerField(required=False)
            self.fields['is_fixed_field_%i' % index] = forms.BooleanField(required=False)
        self.helper = FormHelper()

    def clean(self):
        return self.cleaned_data


class ActivateForm(SignUpForm):
    formattrs = {'required': '',
                 'class': 'required',
                 'autofocus': '', }
    password = forms.CharField(widget=forms.PasswordInput(attrs=formattrs, render_value=False),
                               label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
                                label="Confirm password")

    telephone = forms.CharField(required=False)
    dob = forms.IntegerField(widget=forms.Select(choices=_get_full_dob_years()), label="Year of birth", required=False)
    postcode = forms.CharField(required=False)

    newsletter = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': 'checkbox'}), required=False,
                                    initial=True)

    ratealert = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': 'checkbox'}), required=False,
                                   initial=True)

    def __init__(self, *args, **kwargs):
        grand_total = kwargs.pop('grand_total', 0)
        super(ActivateForm, self).__init__(*args, **kwargs)
        if grand_total >= 100000:
            self.fields['telephone'].widget.required = True
            self.fields['telephone'].widget.attrs = attrs_dict

    def clean(self):
        data = self.cleaned_data
        password = data.get('password', None)
        password2 = data.get('password2', None)
        postcode = data.get('postcode', None)

        if password != password2:
            raise forms.ValidationError("Your passwords didn't match")
        if len(postcode) > 10:
            raise forms.ValidationError("Your postcode is too long")
        return self.cleaned_data


class SubscriptionForm(forms.Form):
    newsletter = forms.BooleanField(widget=forms.CheckboxInput(), required=False)
    ratealert = forms.BooleanField(widget=forms.CheckboxInput(), required=False)


class PersonalDetailsForm(forms.Form):
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'required form-control', 'style': 'width:100%;'}), required=True)
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'required form-control', 'style': 'width:100%;'}), required=True)
    email = forms.EmailField(
        widget=forms.TextInput(attrs={'class': 'required email form-control', 'style': 'width:100%;'}), required=True)
    telephone = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'style': 'width:100%;'}),
                                required=False)
    dob = forms.IntegerField(widget=forms.Select(attrs={'class': 'form-control'},
                                                 choices=_get_full_dob_years()), label="Year of birth", required=False)
    postcode = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'style': 'width:100%;'}),
                               required=False)
    old_email = forms.EmailField(widget=forms.HiddenInput(), required=True)
    ratetracker_alert_threshold = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'required form-control', 'style': 'width:100%;'}),
        max_digits=16, decimal_places=2)

    def clean(self):
        data = self.cleaned_data
        form_email = data.get('email', None)
        old_email = data.get('old_email', None)

        if form_email != old_email:
            if User.objects.filter(email=form_email).exists():
                raise forms.ValidationError("This email is already in use")

        return self.cleaned_data


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'required form-control', 'style': 'width:100%;'},
                                   render_value=False),
        label="Current Password")
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'required form-control', 'style': 'width:100%;'},
                                   render_value=False),
        label="New Password")
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'required form-control', 'style': 'width:100%;'},
                                   render_value=False),
        label="Reenter your new Password")

    def clean(self):
        data = self.cleaned_data
        password = data.get('new_password1', None)
        password2 = data.get('new_password2', None)

        if password != password2:
            raise forms.ValidationError("Your new password didn't match")

        return self.cleaned_data


class DeleteAccountForm(forms.Form):
    user_id = forms.IntegerField(widget=forms.HiddenInput())


class RateAlertForm(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(), label="E-mail Address", required=True)

    def __init__(self, *args, **kwargs):
        super(RateAlertForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Give me these!'))
        self.helper.form_action = reverse('signup_all')


class BasketSignUpForm(SignUpForm):
    ratetracker = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': 'checkbox'}), required=False,
                                     initial=False,
                                     label="Get the savings healthcheck")
    advice = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': 'checkbox'}), required=False, initial=False,
                                label="Advice for savers with over £100k")
    newsletter = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': 'checkbox'}), required=False,
                                    initial=True,
                                    label="Sign up to our super duper newsletter")
    ratealert = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': 'checkbox'}), required=False,
                                   initial=True,
                                   label="Sign up for our rate alerts")
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'required email'}), required=True)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'text required'}), required=True)
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'text required'}), required=True)
    surname = forms.CharField(widget=forms.TextInput(attrs={'class': 'text required'}), required=True)
    telephone = forms.CharField(widget=forms.TextInput(attrs={'style': 'display: none'}), required=False,
                                label="Telephone:")

    all_content = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': 'checkbox', 'disabled': 'true'}),
                                     required=False, initial=True,
                                     label="Get access to all site content")

    concierge = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': 'checkbox'}), required=False,
                                   initial=False,
                                   label="Concierge Enquiry")

    def clean(self):
        return self.cleaned_data

    def __init__(self, *args, **kwargs):
        super(BasketSignUpForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            'email',
            'password',
            'first_name',
            'surname',
            'telephone',
        )


class SCPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super(SCPasswordResetForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(
            Submit('Reset My Password', 'Reset My Password')
        )


class SCSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super(SCSetPasswordForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(
            Submit('Reset My Password', 'Reset My Password')
        )


class ResendActivationForm(forms.Form):
    formattrs = {'required': '',
                 'type': 'email',
                 'class': 'email',
                 'placeholder': 'Enter your email address'}
    email = forms.EmailField(widget=Html5EmailInput(attrs=dict(formattrs, maxlength=75)))

    def __init__(self, *args, **kwargs):
        super(ResendActivationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-4'
        self.helper.field_class = 'col-lg-8'
        self.helper.add_input(Submit('submit', 'Resend my Activation', css_class='pull-right'))

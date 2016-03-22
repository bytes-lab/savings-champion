from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Div, HTML
from django import forms
from django.core.urlresolvers import reverse
from django.forms.extras.widgets import SelectDateWidget
import datetime
from common.models import AuthorProfile, NewsletterSignup, RateAlertsSignup, Profile, CampaignsSignup, \
    HealthcheckSignup, \
    CarouselTab
from tinymce.widgets import TinyMCE
from pages.forms import SavingsPriorityListForm

INCOME_GROWTH_CHOICES = (('none', 'Please select'), ('Growth', 'Growth'), ('Income', 'Income'))

TERM_CHOICES = (('none', 'Please select'),
                ('1 Year', 'Less than 1 Year'),
                ('More than 1 Year', 'More than 1 Year'),
                ('More than 5 Years', 'More than 5 Years')
                )
MARITAL_STATUS_CHOICES = (('none', 'Please select'),
                          ('Single', 'Single'),
                          ('Married', 'Married'),
                          ('Divorced', 'Divorced'),
                          ('Widowed', 'Widowed'),
                          )
TAX_RATE_CHOICES = (('Non', 'Non'),
                    ('Basic', 'Basic'),
                    ('Higher', 'Higher'),
                    ('Additional', 'Additional'),
                    )
ACCESS_YOUR_MONEY = (('none', 'Please select'),
                     ('instant', 'Instant'),
                     ('notice', 'Notice'),
                     ('none_needed', 'None needed'),
                     )
ACCOUNT_TYPE_CHOICES = (('none', 'Please select'),
                        ('savings_ac', 'Savings a/c'),
                        ('cash_isa', 'Cash ISA'),
                        ('kids_ac', 'Kids a/c'),
                        ('regular', 'Regular Savings'),
                        )
YES_NO_CHOICES = (('none', 'Please select'),
                  ('Yes', 'Yes'),
                  ('No', 'No'),)
MONTHLY_INCOME = (('none', 'Please select'),
                  ('Yes', 'Yes'),
                  ('No', 'No'),)

BEST_CALL_TIME = (('Morning', 'Morning'),
                  ('Afternoon', 'Afternoon'),)

TIMES_TO_CALL = (('09:00', '09:00'),
                 ('10:00', '10:00'),
                 ('11:00', '11:00'),
                 ('12:00', '12:00'),
                 ('13:00', '13:00'),
                 ('14:00', '14:00'),
                 ('15:00', '15:00'),
                 ('16:00', '16:00'),
                 ('17:00', '17:00'))


class AuthorProfileForm(forms.ModelForm):
    class Meta:
        model = AuthorProfile
        widgets = {
            'biography': TinyMCE
        }


def _get_years():
    now = datetime.datetime.now()
    return range(now.year, 1900, -1)


attrs_dict = {'class': 'field'}
select_attrs_dict = {'class': 'field'}


class DecisionTreeForm(forms.Form):
    investment_amount = forms.IntegerField(label="Initial Investment",
                                           widget=forms.TextInput(attrs={'class': 'field required number'}))
    estate_value = forms.IntegerField(label="Total Estate value",
                                      widget=forms.TextInput(attrs={'class': 'field required number'}))
    easy_access_required = forms.ChoiceField(choices=YES_NO_CHOICES,
                                             label="Do you require easy access to your account?",
                                             widget=forms.Select(attrs=select_attrs_dict))
    terms = forms.ChoiceField(choices=TERM_CHOICES, label="Term of potential investment",
                              widget=forms.Select(attrs=select_attrs_dict))
    growth_income = forms.ChoiceField(choices=INCOME_GROWTH_CHOICES, label="Is growth of income more important?",
                                      widget=forms.Select(attrs=select_attrs_dict))
    tax_rate = forms.ChoiceField(choices=TAX_RATE_CHOICES, widget=forms.Select(attrs=select_attrs_dict))
    # dob = forms.DateField(widget = SelectDateWidget(years=_get_years()), label = "What is your date of birth", )
    # postcode = forms.CharField(max_length = 100)
    uk_tax_payer = forms.ChoiceField(choices=YES_NO_CHOICES, label="Are you a UK tax payer?",
                                     widget=forms.Select(attrs=select_attrs_dict))
    marital_status = forms.ChoiceField(choices=MARITAL_STATUS_CHOICES, widget=forms.Select(attrs=select_attrs_dict))


class AccountPickerForm(forms.Form):
    account_type = forms.ChoiceField(choices=ACCOUNT_TYPE_CHOICES, label="What type of account")
    access = forms.ChoiceField(choices=ACCESS_YOUR_MONEY, label="Do you need access to your money?")
    lump_sum = forms.IntegerField(label="How much?")
    is_monthly_income = forms.ChoiceField(choices=MONTHLY_INCOME, label="Do you need monthly income?")
    dob = forms.DateField(widget=SelectDateWidget(years=_get_years()), label="What is your date of birth", )


class NewsletterForm(forms.ModelForm):
    source = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = NewsletterSignup

    def clean(self):
        data = self.cleaned_data
        email = data.get('email', None)

        if NewsletterSignup.objects.filter(email=email).count() > 0:
            msg = 'This email address is already registered to receive Newsletters'
            self._errors['email'] = msg
            raise forms.ValidationError(msg)

        return data


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile


class RateAlertForm(forms.ModelForm):
    source = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = RateAlertsSignup

    def clean(self):
        data = self.cleaned_data
        email = data.get('email', None)

        if RateAlertsSignup.objects.filter(email=email).count() > 0:
            msg = 'This email address is already registered to receive Rate Alerts'
            self._errors['email'] = msg
            raise forms.ValidationError(msg)

        return data


class ConciergeForm(forms.ModelForm):
    telephone = forms.CharField(label="Telephone Number", widget=forms.TextInput(attrs={'class': 'required'}),
                                required=True)
    alt_telephone = forms.CharField(label="Alternate Telephone Number", widget=forms.TextInput(), required=False)
    best_call_time = forms.ChoiceField(choices=BEST_CALL_TIME, widget=forms.Select(attrs=select_attrs_dict),
                                       label="Best Time to Call")
    newsletterForm = forms.BooleanField(label="I would also like to receive the Savings Champion newsletter",
                                        required=False, initial=True)

    class Meta:
        model = CampaignsSignup

    def clean(self):
        data = self.cleaned_data
        email = data.get('email', None)
        data['newsletter'] = data['newsletterForm']

        if CampaignsSignup.objects.filter(email=email).count() > 0:
            msg = 'This email address has already been used to register interest'
            self._errors['email'] = msg
            raise forms.ValidationError(msg)

        return data


class CallbackForm(ConciergeForm):
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'required email'}), required=True)
    best_call_time = forms.ChoiceField(choices=TIMES_TO_CALL, widget=forms.Select(attrs=select_attrs_dict),
                                       label="Best Time to Call")


class CarouselForm(forms.ModelForm):
    class Meta:
        model = CarouselTab
        widgets = {
            'title': TinyMCE,
            'description': TinyMCE
        }


class RateAlertsUpsellForm(forms.Form):
    signup_id = forms.IntegerField(widget=forms.HiddenInput(), required=True)


class SavingsHealthCheckForm(forms.ModelForm):
    class Meta:
        model = HealthcheckSignup
        fields = ['first_name', 'last_name', 'email', 'telephone']

    def __init__(self, *args, **kwargs):
        super(SavingsHealthCheckForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.disable_csrf = False
        self.helper.form_action = reverse('savings_health_check')
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Enquire Now', css_class="btn-primary"))
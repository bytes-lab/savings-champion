# coding=utf-8
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Div
from datetime import datetime
from django import forms
from django.core.urlresolvers import reverse
from ifa.models import IFASignup, BJSignup


class IFAForm(forms.ModelForm):
    postcode = forms.CharField(widget=forms.TextInput(), required=True)
    class Meta:
        model = IFASignup
        fields = ('name', 'last_name', 'email', 'postcode', 'telephone', 'signup_amount')
        
    def clean(self):
        data = self.cleaned_data
        email = data.get('email', None)
        if IFASignup.objects.filter(email=email).exists():
            msg = 'This email address has already been used to register interest'
            self._errors['email'] = msg
            raise forms.ValidationError(msg)
        
        return data

    def __init__(self, *args, **kwargs):
        super(IFAForm, self).__init__(*args, **kwargs)  # populates the post
        self.fields['telephone'] = forms.CharField(widget=forms.TextInput(attrs={'parsley-type': 'phone'}))
        self.fields['signup_amount'] = forms.CharField(widget=forms.HiddenInput(), required=False)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-4'
        self.helper.field_class = 'col-lg-8'
        self.helper.form_method = "POST"
        self.helper.form_action = reverse('tpo_signup')
        self.helper.add_input(Submit('submit', 'Download Now', css_class="btn-success"))


class BJForm(forms.ModelForm):

    class Meta:
        model = BJSignup
        exclude = ['location', 'comments']

    def __init__(self, *args, **kwargs):
        super(BJForm, self).__init__(*args, **kwargs)  # populates the post
        self.fields['name'] = forms.CharField(widget=forms.TextInput(attrs={'style': 'width:100%;'}))
        self.fields['email'] = forms.CharField(widget=forms.TextInput(attrs={'style': 'width:100%;'}))
        self.fields['telephone'] = forms.CharField(widget=forms.TextInput(attrs={'style': 'width:100%;'}))
        self.fields['postcode'] = forms.CharField(label='Postcode', widget=forms.TextInput(attrs={'style': 'width:100%;'}))
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-4'
        self.helper.field_class = 'col-lg-8'
        self.helper.form_method = "POST"
        self.helper.form_action = reverse('bj_signup')
        self.helper.add_input(Submit('submit', 'Enquire Now', css_class="btn-success"))

    def clean(self):
        data = self.cleaned_data
        email = data.get('email', None)
        if BJSignup.objects.filter(email=email).exists():
            msg = 'This email address has already been used to register interest'
            self._errors['email'] = msg
            raise forms.ValidationError(msg)

        return data


class TPOFactFindForm(forms.Form):

    MARITAL_STATUS = (
        ('not_disclosed', 'Not Disclosed'),
        ('single', 'Single'),
        ('married', 'Married/Civil Partner'),
        ('divorced', 'Divorced/Person whose Civil Partnership has been dissolved'),
        ('widowed', 'Widowed/Surviving Civil Partner'),
        ('seperated', 'Separated'),
    )

    EMPLOYMENT_STATUS = (
        ('not_disclosed', 'Not Disclosed or Not Applicable'),
        ('not_employed', 'Not Employed'),
        ('worker', 'Worker'),
        ('employee', 'Employee'),
        ('self_employed', 'Self-employed or Contractor'),
        ('retired', 'Retired'),
        ('director', 'Director'),
        ('office_holder', 'Office Holder'),
    )

    ANNUAL_INCOME = (
        ('0', 'None'),
        ('<50k', '£0 - £50k'),
        ('50k - 150k', '£50k - £150k'),
        ('150k+', '£150k+'),
    )

    TOTAL_ASSETS = (
        ('0', 'None'),
        ('<250k', '£0 - £250k'),
        ('250k - 1m', '£250k - £1million'),
        ('1m+', '£1million+'),
    )

    name = forms.CharField(label='Full name')
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': '3', 'style': 'max-width: 100%;'}))
    office_number = forms.CharField()
    home_number = forms.CharField()
    mobile_number = forms.CharField()
    email = forms.EmailField()
    dob = forms.CharField(label='Date of Birth')
    marital_status = forms.ChoiceField(choices=MARITAL_STATUS)

    employment_status = forms.ChoiceField(choices=EMPLOYMENT_STATUS, help_text='<a href="https://www.gov.uk/employment-status/overview" target="_blank">Definition of employment status</a>')
    partner_employment_status = forms.ChoiceField(choices=EMPLOYMENT_STATUS, help_text='<a href="https://www.gov.uk/employment-status/overview" target="_blank">Definition of employment status</a>')

    occupation = forms.CharField()
    partner_occupation = forms.CharField()

    total_asset_value = forms.ChoiceField(choices=TOTAL_ASSETS, label='Your assets value')
    partner_total_asset_value = forms.ChoiceField(choices=TOTAL_ASSETS, label='Partners assets value')
    joint_total_asset_value = forms.ChoiceField(choices=TOTAL_ASSETS,label='Joint assets value')

    total_income = forms.ChoiceField(choices=ANNUAL_INCOME, label='Your income')
    partner_total_income = forms.ChoiceField(choices=ANNUAL_INCOME, label='Partners income')
    joint_total_income = forms.ChoiceField(choices=ANNUAL_INCOME, label='Joint income')

    protection = forms.BooleanField(required=False)
    retirement_planning = forms.BooleanField(required=False)
    estate_planning = forms.BooleanField(required=False)
    investment_planning = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super(TPOFactFindForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Section 1: Please outline which service areas you would like to discuss with one of our qualified Advisers',
                Div(
                    'protection',
                    css_class='col-md-3'
                ),
                Div(
                    'retirement_planning',
                    css_class='col-md-3'
                ),
                Div(
                    'investment_planning',
                    css_class='col-md-3'
                ),
                Div(
                    'estate_planning',
                    css_class='col-md-3'
                ),
            ),
            Fieldset(
                'Section 2: Employment details',
                Div(
                    'employment_status',
                    css_class='col-md-6'
                ),
                Div(
                    'partner_employment_status',
                    css_class='col-md-6'
                ),
                Div(
                    'occupation',
                    css_class='col-md-6'
                ),
                Div(
                    'partner_occupation',
                    css_class='col-md-6'
                ),

            ),
            Fieldset(
                'Section 3: Assets (Including cash savings, excluding property)',
                Div(
                    'total_asset_value',
                    css_class='col-md-4'
                ),
                Div(
                    'partner_total_asset_value',
                    css_class='col-md-4'
                ),
                Div(
                    'joint_total_asset_value',
                    css_class='col-md-4'
                ),
            ),
            Fieldset(
                'Section 4: Income (per annum)',
                Div(
                    'total_income',
                    css_class='col-md-4'
                ),
                Div(
                    'partner_total_income',
                    css_class='col-md-4'
                ),
                Div(
                    'joint_total_income',
                    css_class='col-md-4'
                ),
            ),
            Fieldset(
                'Section 5: Contact details',
                Div(
                    'name',
                    css_class='col-md-6'
                ),
                Div(
                    'email',
                    css_class='col-md-6'
                ),
                'address',
                Div(
                    'office_number',
                    css_class='col-md-4'
                ),
                Div(
                    'home_number',
                    css_class='col-md-4'
                ),
                Div(
                    'mobile_number',
                    css_class='col-md-4'
                ),
            ),
            Fieldset(
                'Section 6: Personal infomation',
                Div(
                    'dob',
                    css_class='col-md-6'
                ),
                Div(
                    'marital_status',
                    css_class='col-md-6'
                ),
            ),
            Submit('Submit Enquiry', 'Submit Enquiry', css_class='pull-right')
        )
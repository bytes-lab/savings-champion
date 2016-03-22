# coding=utf-8
from crispy_forms.bootstrap import StrictButton, PrependedText, AppendedText, PrependedAppendedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Button, Layout, Div, Submit, Fieldset, HTML, Field
from django import forms
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from common.accounts.utils import create_stage_one_profile
from common.models import Profile, Referrer
from concierge.models import AdviserQueue, ConciergeUserOption, ConciergeUserNotes, EmailTemplate, SOURCE_LIST, \
    ConciergeLeadCapture, ConciergeUserPool
from products.models import Provider

User = get_user_model()


class SignedForm(forms.ModelForm):
    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-lg-4'
    helper.field_class = 'col-lg-8'
    helper.form_method = "POST"

    class Meta:
        model = AdviserQueue
        fields = ['portfolio_value', 'fee']


class AddClientForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput())
    email = forms.CharField(widget=forms.TextInput())
    telephone = forms.CharField(widget=forms.TextInput())
    source = forms.ChoiceField(choices=SOURCE_LIST)

    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-lg-4'
    helper.field_class = 'col-lg-8'
    helper.form_method = "POST"

    class Meta:
        model = AdviserQueue
        fields = ['name', 'email', 'telephone', 'source']


class DateFilterForm(forms.Form):
    referrer = forms.ModelChoiceField(queryset=Referrer.objects)
    start_date = forms.DateTimeField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateTimeField(widget=forms.DateInput(attrs={'type': 'date'}))
    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-lg-4'
    helper.field_class = 'col-lg-8'

    def __init__(self, *args, **kwargs):
        super(DateFilterForm, self).__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Div(
                Div(
                    'referrer',
                    css_class='col-md-4'
                ),
                Div(
                    'start_date',
                    css_class='col-md-3'
                ),
                Div(
                    'end_date',
                    css_class='col-md-3'
                ),
                Div(
                    Button('Filter', 'Filter', data_url=reverse('user_breakdown_ajax')),
                    css_class='col-md-2'
                ),
                css_class='row'
            )
        )


class ConciergeUserForm(forms.Form):
    email = forms.EmailField()

    def __init__(self, *args, **kwargs):
        super(ConciergeUserForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-10'
        self.helper.form_method = "POST"
        self.helper.add_input(Button('Manage User', 'Manage User', data_url=reverse('engine_load_user'),
                                     data_source='id_email'))


class ConciergeUserOptionForm(forms.ModelForm):
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False, label='To take advantage of age related accounts')

    def __init__(self, *args, **kwargs):
        super(ConciergeUserOptionForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-10'

    class Meta:
        model = ConciergeUserOption
        exclude = (
        'user', 'enquiry', 'no_lowest_rate', 'existing_customer', 'local_customer', 'open_branch', 'access_branch')


class ConciergeUserOptionPublicForm(ConciergeUserOptionForm):
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False,
                                 label='To take advantage of age related accounts', help_text='Enter your date of birth')

    def __init__(self, *args, **kwargs):
        super(ConciergeUserOptionPublicForm, self).__init__(*args, **kwargs)
        self.helper.label_class = 'col-lg-6'
        self.helper.field_class = 'col-lg-6'
        self.helper.layout = Layout(
            Div(
                Div(
                    Div(
                        Div(
                            HTML('<h4>I am happy to open accounts via:</h4>'),
                            css_class='panel-heading'
                        ),
                        Div(
                            'open_post',
                            'open_internet',
                            'open_telephone',
                            css_class='panel-body'
                        ),
                        css_class="panel panel-default"
                    ),
                    css_class='col-md-6'
                ),
                Div(
                    Div(
                        Div(
                            HTML('<h4>I am happy to access accounts via:</h4>'),
                            css_class='panel-heading'
                        ),
                        Div(
                            'access_post',
                            'access_internet',
                            'access_telephone',
                            css_class='panel-body'
                        ),
                        css_class="panel panel-default"
                    ),
                    css_class='col-md-6'
                ),
                css_class="row"
            ),
            Div(
                Div(
                    Div(
                        Div(
                            HTML('<h4>I would also like:</h4>'),
                            css_class='panel-heading'
                        ),
                        Div(
                            'monthly_interest',
                            'joint_name',
                            'birth_date',
                            css_class='panel-body'
                        ),
                        css_class="panel panel-default"
                    ),
                    css_class="col-md-12"
                ),
                css_class="row"
            )
        )

    class Meta:
        model = ConciergeUserOption
        exclude = ('user', 'enquiry', 'no_lowest_rate', 'existing_customer', 'local_customer', 'open_branch',
                   'access_branch', 'minimum_opening_balance', 'maximum_opening_balance', 'business', 'child',
                   'charity', 'ignore_fscs', 'dual_portfolio', 'current_accounts', 'shariaa', 'use_existing_accounts')


class ConciergeUserNotesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ConciergeUserNotesForm, self).__init__(*args, **kwargs)
        self.fields['user'] = forms.ModelChoiceField(widget=forms.HiddenInput(), queryset=User.objects.all())
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal js-client-notes-form'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-10'
        self.helper.form_method = "POST"
        self.helper.form_action = reverse('adviser_client_notes')
        self.helper.add_input(
            Button('Update User Notes', 'Update User Notes', data_url=reverse('adviser_client_notes')))

    class Meta:
        model = ConciergeUserNotes
        fields = ('user', 'note',)


class ConciergeUserPoolForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ConciergeUserPoolForm, self).__init__(*args, **kwargs)
        self.helper = ConciergeUserPoolFormHelper()
        self.helper.form_tag = False

    class Meta:
        model = ConciergeUserPool

class ConciergeUserPoolFormHelper(FormHelper):
    def __init__(self, uuid=None, *args, **kwargs):
        super(ConciergeUserPoolFormHelper, self).__init__(*args, **kwargs)
        self.form_action = reverse('engine_update_pool')
        self.form_class = 'form-horizontal'
        self.label_class = 'col-lg-4'
        self.field_class = 'col-lg-8'
        self.form_method = "post"
        self.render_unmentioned_fields = True
        self.layout = Layout(
            Div(
                AppendedText('term', 'Months'),
                PrependedText('balance', '&pound;'),
                'uuid',
                'user',
                css_class='js-pool-form'
            )
        )


class ConciergeUserPrivatePoolForm(ConciergeUserPoolForm):
    def __init__(self, *args, **kwargs):
        super(ConciergeUserPrivatePoolForm, self).__init__(*args, **kwargs)

class ConciergeUserPublicPoolForm(ConciergeUserPoolForm):
    def __init__(self, *args, **kwargs):
        super(ConciergeUserPublicPoolForm, self).__init__(*args, **kwargs)
        self.helper.disable_csrf = True
        self.helper.label_class = 'col-sm-4 col-sm-offset-2'
        self.helper.field_class = 'col-sm-4'
        self.fields['term'] = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'clearfix',}),
                                                 label='Account term')
        self.fields['balance'] = forms.DecimalField(widget=forms.NumberInput(),
                                                    label='Amount held in cash savings')
        self.helper.layout = Layout(
            Div(
                Div(
                    PrependedText('balance', '&pound;'),
                    css_class='row'
                ),
                HTML('<br/>'),
                Div(
                    AppendedText('term', 'Months'),
                    css_class='row'
                ),
                'uuid',
                'user',
                css_class='js-pool-form row'
            )
        )


ACCOUNT_TYPES = (
    ('personal', 'Personal'),
    ('charity', 'Charity'),
    ('business', 'Business')
)

class ConciergeUserPoolType(forms.Form):
    account_type = forms.ChoiceField(widget=forms.RadioSelect(), choices=ACCOUNT_TYPES, label='What type of accounts can we help you with?')

    def __init__(self, *args, **kwargs):
        super(ConciergeUserPoolType, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-4'
        self.helper.field_class = 'col-lg-8'
        self.helper.form_tag = False


class ConciergeUserRequiredProductForm(forms.Form):
    concierge_user = forms.ModelChoiceField(queryset=ConciergeUserOption.objects,
                                            widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(ConciergeUserRequiredProductForm, self).__init__(*args, **kwargs)
        self.fields['provider'] = forms.ModelChoiceField(queryset=Provider.objects, widget=forms.Select(
            attrs={'data-url': reverse('engine_get_master_products_from_provider')}))
        self.fields['products'] = forms.IntegerField(widget=forms.Select())
        self.fields['balance'] = forms.DecimalField()
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-4'
        self.helper.field_class = 'col-lg-8'
        self.helper.form_method = "post"


class ConciergeUserAddExistingProductForm(forms.Form):
    input_formats = ['%Y-%m-%dT%H:%M']

    def __init__(self, *args, **kwargs):
        super(ConciergeUserAddExistingProductForm, self).__init__(*args, **kwargs)
        self.fields['provider'] = forms.ModelChoiceField(queryset=Provider.objects, widget=forms.Select(
            attrs={'data-url': reverse('engine_get_products_from_provider')}), required=True)
        self.fields['product'] = forms.IntegerField(widget=forms.Select(), required=True)
        self.fields['balance'] = forms.DecimalField(max_digits=19, decimal_places=3, required=True)
        self.fields['maturity_date'] = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False,
                                                       help_text='Only for fixed term product')
        self.fields['rate'] = forms.DecimalField(max_digits=19, decimal_places=3, required=False,
                                                 help_text='Only for fixed term product')
        self.fields['term'] = forms.IntegerField(required=False, help_text='Only for fixed term product',
                                                 label='Term (months)')
        self.fields['fee_exempt'] = forms.BooleanField(initial=False, required=False,
                                                       help_text='Only for fixed term product')
        self.fields['user'] = forms.ModelChoiceField(widget=forms.HiddenInput(), queryset=User.objects, required=True)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal js-add-existing-products-form'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-10'
        self.helper.form_method = "POST"
        self.helper.form_action = reverse('engine_add_existing_product')
        self.helper.add_input(
            Button('Add Existing Product', 'Add Existing Product', css_class="btn btn-success js-add-existing-product",
                   data_url=reverse('engine_add_existing_product'))
        )


class ConciergeBasicWizardForm(forms.Form):
    def __init__(self, client_id, *args, **kwargs):
        super(ConciergeBasicWizardForm, self).__init__(*args, **kwargs)
        self.client_id = client_id
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-10'
        self.helper.form_method = "POST"
        self.helper.form_action = reverse('concierge_wizard', args=[client_id])

    def save(self):
        raise NotImplementedError


class ConciergeBasicInformationForm(ConciergeBasicWizardForm):
    MARITAL_STATUS = (
        (1, 'Single'),
        (2, 'Engaged'),
        (3, 'Married'),
        (4, 'Civil Partnership'),
        (5, 'Divorced')
    )

    RESIDENTIAL_STATUS = (
        (1, 'UK Renter'),
        (2, 'UK Homeowner'),
        (3, 'Non-UK Resident')
    )

    def __init__(self, *args, **kwargs):
        super(ConciergeBasicInformationForm, self).__init__(*args, **kwargs)
        self.fields['email'] = forms.EmailField(required=True)
        self.fields['title'] = forms.CharField(required=False)
        self.fields['first_name'] = forms.CharField(required=False)
        self.fields['last_name'] = forms.CharField(required=False)
        self.fields['phone'] = forms.CharField(required=False)
        self.fields['marital_status'] = forms.ChoiceField(choices=self.MARITAL_STATUS)
        self.fields['residential_status'] = forms.ChoiceField(choices=self.RESIDENTIAL_STATUS)
        self.fields['date_of_birth'] = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
        self.helper.form_class = 'form-horizontal js-wizard-basic-information'
        self.helper.add_input(
            Submit('Update Basic Information', 'Update Basic Information')
        )

    def save(self):
        data = self.cleaned_data
        user_exists = False
        if 'email' in data:
            email = data['email']
            if User.objects.filter(email=email).exists():
                # This user already exists, maybe they have details that need to be updated
                user_exists = True
                user = User.objects.get(email=email)
            else:
                # User does not already exist, we'll need to create one.
                create_profile_output = create_stage_one_profile(None, email, '', send_activation=False,
                                                                 login_user=False, use_site_framework=False)
                if isinstance(create_profile_output, tuple):
                    user, user_created, record_stats = create_profile_output
                else:
                    return create_profile_output
                user_exists = True

        if 'title' in data and user_exists:
            title = data['title']
            profile = Profile.objects.get(user=user)
            profile.salutation = title
            profile.save()

        if 'first_name' in data and user_exists:
            first_name = data['first_name']
            user.first_name = first_name

        if 'last_name' in data and user_exists:
            last_name = data['last_name']
            user.last_name = last_name

        if 'phone' in data and user_exists:
            phone = data['phone']
            profile = Profile.objects.get(user=user)
            profile.telephone = phone
            profile.save()
        if 'marital_status' in data:
            pass
        if 'residential_status' in data:
            pass
        if 'date_of_birth' in data:
            dob = data['date_of_birth']
            profile = Profile.objects.get(user=user)
            profile.dob = dob
            profile.save()


class ConciergeNotQualifiedForm(ConciergeBasicWizardForm):
    input_formats = ['%Y-%m-%dT%H:%M']


    def __init__(self, *args, **kwargs):
        super(ConciergeNotQualifiedForm, self).__init__(*args, **kwargs)
        self.fields['where_did_you_hear_about_us'] = forms.CharField(required=False)
        self.fields['reason_for_unqualification'] = forms.CharField(required=False)
        self.fields['call_back_time'] = forms.DateTimeField(widget=forms.DateInput(attrs={'type': 'datetime-local'}),
                                                            input_formats=self.input_formats,
                                                            required=False)
        self.helper.form_class = 'form-horizontal js-wizard-not-qualified'
        self.helper.add_input(
            Submit('Client Not Qualified', 'Client Not Qualified')
        )


class ConciergeNotSuitableForm(ConciergeBasicWizardForm):
    def __init__(self, *args, **kwargs):
        super(ConciergeNotSuitableForm, self).__init__(*args, **kwargs)
        self.fields['why_is_lead_unsuitable_for_concierge'] = forms.CharField(required=False)
        self.fields['why_is_lead_unsuitable_for_ifa'] = forms.CharField(required=False)
        self.helper.form_class = 'form-horizontal js-wizard-not-suitable'
        self.helper.add_input(
            Submit('Client Not Suitable', 'Client Not Suitable')
        )


class IllustrationForm(forms.Form):
    funds_under_management = forms.DecimalField()

    def __init__(self, *args, **kwargs):
        super(IllustrationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal js-illustrated-form'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-10'
        self.helper.form_method = "POST"


class RecommendedForm(forms.Form):
    funds_under_management = forms.DecimalField()

    def __init__(self, *args, **kwargs):
        super(RecommendedForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal js-recommended-form'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-10'
        self.helper.form_method = "POST"


class UnsuitableForm(forms.Form):
    reason = forms.CharField(widget=forms.Textarea())

    def __init__(self, *args, **kwargs):
        super(UnsuitableForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal js-unsuitable-form'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-10'
        self.helper.form_method = "POST"


class FakeForm(forms.Form):
    reason = forms.CharField(widget=forms.Textarea())

    def __init__(self, *args, **kwargs):
        super(FakeForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal js-fake-form'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-10'
        self.helper.form_method = "POST"


class NoContactForm(forms.Form):
    template = forms.ModelChoiceField(queryset=EmailTemplate.objects)
    client_name = forms.CharField()

    def __init__(self, *args, **kwargs):
        super(NoContactForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal js-no-contact-form'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-10'
        self.helper.form_method = "POST"


class ConciergeLeadCaptureForm(forms.ModelForm):
    date_attrs = {'type': 'date'}

    date_of_birth = forms.DateField(widget=forms.TextInput(attrs=date_attrs))
    date_moved_in = forms.DateField(widget=forms.TextInput(attrs=date_attrs))
    passport_issue_date = forms.DateField(widget=forms.TextInput(attrs=date_attrs))
    passport_expiry_date = forms.DateField(widget=forms.TextInput(attrs=date_attrs))

    class Meta:
        model = ConciergeLeadCapture
        exclude = ('user', 'named_user')

    def __init__(self, *args, **kwargs):
        super(ConciergeLeadCaptureForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal js-lead-capture-form'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-10'
        self.helper.form_method = "POST"
        self.helper.add_input(
            Button('Save Client Details', 'Save Client Details', css_class="btn-success js-save-client-details",
                   data_url=reverse('update_client_details', args=(self.instance.user.pk, ))))


class ConciergePoolForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(ConciergePoolForm, self).__init__(*args, **kwargs)
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-10'
        self.helper.form_method = "POST"


class ConciergeUserAcceptedProductForm(forms.Form):
    concierge_user = forms.ModelChoiceField(queryset=ConciergeUserOption.objects,
                                            widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(ConciergeUserAcceptedProductForm, self).__init__(*args, **kwargs)
        self.fields['provider'] = forms.ModelChoiceField(queryset=Provider.objects, widget=forms.Select(
            attrs={'data-url': reverse('engine_get_master_products_from_provider')}))
        self.fields['products'] = forms.IntegerField(widget=forms.Select())
        self.fields['balance'] = forms.DecimalField()
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-4'
        self.helper.field_class = 'col-lg-8'
        self.helper.form_method = "post"

class ConciergeLandingContactForm(forms.Form):

    name = forms.CharField(widget=forms.TextInput())
    email = forms.EmailField(widget=forms.EmailInput())
    phone = forms.CharField(widget=forms.TextInput())

    def __init__(self, *args, **kwargs):
        super(ConciergeLandingContactForm, self).__init__(*args, **kwargs)


class ConciergeLandingContactFormHelper(FormHelper):

    def __init__(self):
        super(ConciergeLandingContactFormHelper, self).__init__()
        self.layout = Layout(
            'name',
            'email',
            'phone',
            StrictButton('<span class="glyphicon glyphicon-earphone"></span> Book Call Back',
                         css_class='btn-success js-concierge-enquire', type='submit'),
        )


class ThisIsMoneyConciergeWidgetPoolForm(forms.ModelForm):
    balance = forms.IntegerField(min_value=0,
                                 label='Deposit',
                                 required=True
                                 )
    term = forms.IntegerField(min_value=0,
                              label='for',
                              required=True
                              )
    user = forms.ModelChoiceField(widget=forms.HiddenInput(), queryset=User.objects)

    def __init__(self, *args, **kwargs):
        super(ThisIsMoneyConciergeWidgetPoolForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'hidden'
        self.helper.field_class = 'col-xs-9'
        self.helper.html5_required = True
        self.helper.layout = Layout(
            'user',
            PrependedText('balance', 'Deposit £'),
            AppendedText('term', 'months'),
            Div(
                Div(
                    Submit('Calculate', 'Calculate', css_class='btn btn-success'),
                    css_class='col-xs-6',
                ),
                Div(
                    HTML('<p>Powered by <a target="_blank" href="https://savingschampion.co.uk"><img class="img-responsive" src="https://savingschampion.co.uk/static/img/logo.updated.dark_bg.24.11.2014.png"/></a></p>'),
                    css_class='col-xs-6',
                ),
                css_class="row",
            ),
        )

    class Meta:
        model = ConciergeUserPool
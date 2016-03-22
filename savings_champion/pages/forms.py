# coding=utf-8
import logging
from ckeditor.widgets import CKEditorWidget
from crispy_forms.bootstrap import AppendedText, PrependedText, InlineField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Button, Div, Layout, Fieldset
from django import forms
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.utils.encoding import force_text
from pages.models import Page, PageBody, Article, PageBlock, FormMessage, BlogItem, ArticleComment, BlogComment, \
    Petition, SevenPitfallsSignup, IHTGuideSignup, PressAppearancePublication, NISAGuideSignup, \
    SavingsPriorityListSignup, SavingsPriorityListOptionSignup, FiftyPoundChallengeSignup, FiftyPoundChallengeAccount, \
    ProductQuestionaireSignup, TheBiggestMistakeSignup, FactFindSignup, FactFindAccount, PensionOptionSignup, \
    MindfulMoneyHealthcheckSignup, MoneyToTheMassesSignup, ChallengerBankGuideSignup, IHTSqueezePageSignup, \
    PSASqueezePageSignup, HighWorthSqueezePageSignup
from tinymce.widgets import TinyMCE
from ckeditor.fields import RichTextField
from common.html5inputs import *
from common.models import CampaignsSignup
from products.models import Provider

User = get_user_model()


class FormMessageForm(forms.ModelForm):
    class Meta:
        model = FormMessage
        widgets = {
            'text': TinyMCE()
        }


class PageBodyForm(forms.ModelForm):
    class Meta:
        model = PageBody
        widgets = {
            'text': TinyMCE()
        }


log = logging.getLogger(__name__)


class BlogItemForm(forms.ModelForm):
    author = forms.ModelChoiceField(queryset=User.objects.filter(is_staff=True))
    genre = forms.CharField(widget=forms.Select(choices=BlogItem.GENERE_CHOICES))

    def is_valid(self):
        log.error(force_text(self.errors))
        return super(BlogItemForm, self).is_valid()

    class Meta:
        model = BlogItem
        widgets = {
            'body': TinyMCE()
        }


class PageBlockForm(forms.ModelForm):
    author = forms.ModelChoiceField(queryset=User.objects.filter(is_staff=True))

    class Meta:
        model = PageBlock
        widgets = {
            'text': TinyMCE()
        }


ARTICLE_GUIDE_CHOICES = (
    ('article', 'Article'),
    ('guide', 'Guide'),
)


class ArticleForm(forms.ModelForm):
    type = forms.ChoiceField(choices=ARTICLE_GUIDE_CHOICES)
    author = forms.ModelChoiceField(queryset=User.objects.filter(is_staff=True))

    class Meta:
        model = Article
        widgets = {
            'body': CKEditorWidget(),
            'teaser': CKEditorWidget(),
            'meta_description': forms.Textarea
        }


class PageForm(forms.ModelForm):
    """ 
    This is a simple simple tree hierarchy structure - the only hard part is 
    that we need to tell the users to enter the URL in order to tell us where the 
    page should sit in the site. 
    """
    #url = forms.CharField(help_text = """Please enter the where you would like to place this page""", required = False)
    parent_page = forms.ModelChoiceField(queryset=(), required=True)

    def __init__(self, *args, **kwargs):
        super(PageForm, self).__init__(*args, **kwargs)

        initial = None

        if self.instance.id:
            # gets the right work for the parent page - but cant move based on this
            queryset = Page.objects.filter(lft__lt=self.instance.lft, rgt__gt=self.instance.rgt).order_by('-lft')

            if len(queryset) > 0:
                initial = queryset[0]

        else:
            queryset = Page.objects.all()

        self.fields['parent_page'].queryset = queryset
        self.fields['parent_page'].initial = initial


    class Meta:
        model = Page
        widgets = {
            'meta_description': forms.Textarea
        }


class ConciergeSignupForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'required': 'true', 'class': 'required form-control'}),
                           label="Name", required=True)

    formattrs = {'required': '',
                 'type': 'email',
                 'class': 'email required form-control',
                 'placeholder': 'Enter your email address'}
    email = forms.EmailField(widget=Html5EmailInput(attrs=dict(formattrs, maxlength=75)),
                             label="Email Address", required=True)

    telephone = forms.CharField(widget=forms.TextInput(attrs={'class': 'required phonesUK form-control'}),
                                required=True,
                                label="Phone number (so we can call you back)")

    CALL_CHOICES = (
        ('Anytime', 'Anytime (9-5 weekdays)'),
        ('Morning', 'Morning (9-12 weekdays)'),
        ('Afternoon', 'Afternoon (12-5 weekdays)'))

    timetocall = forms.ChoiceField(choices=CALL_CHOICES, label="Best time to call", required=False,
                                   widget=forms.Select(attrs={'class': 'form-control'}))
    source = forms.CharField(widget=forms.HiddenInput(), required=False)

    def clean(self):
        return self.cleaned_data

    class Meta:
        model = CampaignsSignup


class BaseCommentForm(forms.ModelForm):
    comment = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control required'}), required=True)
    comment_date = forms.DateTimeField(widget=forms.HiddenInput(), required=False)

    def is_valid(self):
        if self.errors:
            log.error(force_text(self.errors))
        return super(BaseCommentForm, self).is_valid()

    def __init__(self, *args, **kwargs):
        super(BaseCommentForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit(name='add_comment', value='Add comment'))
        self.helper.form_tag = False


class ArticleCommentForm(BaseCommentForm):
    class Meta:
        model = ArticleComment


class BlogCommentForm(BaseCommentForm):
    class Meta:
        model = BlogComment


class PetitionForm(forms.ModelForm):
    email = forms.EmailField()
    first_name = forms.CharField(widget=forms.TextInput())
    last_name = forms.CharField(widget=forms.TextInput())
    postcode = forms.CharField(widget=forms.TextInput())

    class Meta:
        model = Petition
        fields = ['first_name', 'last_name', 'email', 'postcode']

    def __init__(self, *args, **kwargs):
        super(PetitionForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-4'
        self.helper.field_class = 'col-lg-8'
        self.helper.add_input(Submit(value='Add to petition', name='submit', css_class='btn-success'))


class PetitionEmailForm(forms.Form):
    email_addresses = forms.CharField(widget=Html5EmailInput(attrs={'placeholder': 'or choose from your inbox by clicking share via email below.'}
                                                            ), required=False)
    subject = forms.CharField(widget=forms.TextInput())
    body = forms.CharField(widget=forms.Textarea())

    class Meta:
        model = Petition

    def __init__(self, *args, **kwargs):
        super(PetitionEmailForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-3'
        self.helper.field_class = 'col-sm-9'
        self.helper.add_input(Button(value='Share via Email', name='update',
                                     css_class='btn btn-success', style="font-size:18px;"))

class SevenPitfallsForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Your name'}))
    email = forms.CharField(widget=Html5EmailInput(attrs={'placeholder': 'Where should we send your guide?'}))
    phone = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Your phone number'}))

    class Meta:
        model = SevenPitfallsSignup
        fields = ('name', 'email', 'phone')

    def __init__(self, *args, **kwargs):
        super(SevenPitfallsForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-4'
        self.helper.field_class = 'col-lg-8'
        self.helper.form_method = "POST"
        self.helper.form_action = reverse('seven_pitfalls_for_savers')
        self.helper.add_input(Submit('submit', 'Download guide', css_class="btn-success"))


class NISAGuideForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Your name'}))
    email = forms.CharField(widget=Html5EmailInput(attrs={'placeholder': 'Where should we send your guide?'}))

    class Meta:
        model = NISAGuideSignup
        fields = ('name', 'email')

    def __init__(self, *args, **kwargs):
        super(NISAGuideForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-4'
        self.helper.field_class = 'col-lg-8'
        self.helper.form_method = "POST"
        self.helper.form_action = reverse('nisa_savings_guide_signup')
        self.helper.add_input(Submit('submit', 'Send me the NISA guide', css_class="btn-success pull-right"))


class IHTGuideForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Your name'}))
    email = forms.CharField(widget=Html5EmailInput(attrs={'placeholder': 'Where should we send your guide?'}))
    phone = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Your phone number'}))

    class Meta:
        model = IHTGuideSignup
        fields = ('name', 'email', 'phone')

    def __init__(self, *args, **kwargs):
        super(IHTGuideForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-4'
        self.helper.field_class = 'col-lg-8'
        self.helper.form_method = "POST"
        self.helper.form_action = reverse('iht_guide_signup')
        self.helper.add_input(Submit('submit', 'Download guide', css_class="btn-success pull-right"))

class FBIHTGuideForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Your name'}))
    email = forms.CharField(widget=Html5EmailInput(attrs={'placeholder': 'Where should we send your guide?'}))
    phone = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Your phone number'}))

    class Meta:
        model = IHTGuideSignup
        fields = ('name', 'email', 'phone')

    def __init__(self, *args, **kwargs):
        super(FBIHTGuideForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-10'
        self.helper.form_method = "POST"
        self.helper.form_action = reverse('fb_iht_guide_signup')
        self.helper.add_input(Submit('submit', 'Download guide', css_class="btn-savchamp pull-right"))

class OBIHTGuideForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Your name'}))
    email = forms.CharField(widget=Html5EmailInput(attrs={'placeholder': 'Where should we send your guide?'}))
    phone = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Your phone number'}))

    class Meta:
        model = IHTGuideSignup
        fields = ('name', 'email', 'phone')

    def __init__(self, *args, **kwargs):
        super(OBIHTGuideForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-10'
        self.helper.form_method = "POST"
        self.helper.form_action = reverse('outbrain_iht_guide_signup')
        self.helper.add_input(Submit('submit', 'Download guide', css_class="btn-savchamp pull-right"))


class FilterForm(forms.ModelForm):

    def __init__(self):
        super(FilterForm, self).__init__()
        self.fields['name'] = forms.ModelChoiceField(queryset=PressAppearancePublication.objects.all(),
                                                     widget=forms.Select(attrs={'data-url': reverse('in_the_press_ajax')}),
                                                     label='Publications')

    helper = FormHelper()

    class Meta:
        model = PressAppearancePublication
        fields = ('name',)


class SavingsPriorityListForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Your name'}))
    email = forms.CharField(widget=Html5EmailInput(attrs={'placeholder': 'Your email address'}))

    class Meta:
        model = SavingsPriorityListSignup

    def __init__(self, *args, **kwargs):
        super(SavingsPriorityListForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-10'
        self.helper.form_method = "POST"
        self.helper.form_action = reverse('savings_priority_list_signup')
        self.helper.add_input(Submit('submit', 'Register my interest', css_class="btn-success"))


class SavingsPriorityListOptionForm(forms.ModelForm):

    class Meta:
        model = SavingsPriorityListOptionSignup

    def __init__(self, *args, **kwargs):
        super(SavingsPriorityListOptionForm, self).__init__(*args, **kwargs)
        self.fields['user'] = forms.CharField(widget=forms.HiddenInput())
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-10'
        self.helper.form_method = "POST"
        self.helper.form_action = reverse('savings_priority_list_options')
        self.helper.add_input(Submit('submit', 'Update my product interests', css_class="btn-success"))


class SavingsPriorityProductForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Your name'}), required=True)
    email = forms.CharField(widget=Html5EmailInput(attrs={'placeholder': 'Your email address'}), required=True)

    class Meta:
        model = SavingsPriorityListSignup

    def __init__(self, *args, **kwargs):
        super(SavingsPriorityProductForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal js-spl'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-10'
        self.helper.form_method = "POST"
        self.helper.form_action = reverse('savings_priority_list_signup')
        self.helper.add_input(Submit('submit', 'Join and open account', css_class="btn-success js-join-spl pull-right"))
        self.helper.add_input(
            Button('Continue to Provider', 'Open account without joining',
                   css_class='btn-primary js-to-provider pull-right')
        )


class FiftyPoundChallengeForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Your name'}))
    email = forms.CharField(widget=Html5EmailInput(attrs={'placeholder': 'Your email address'}))
    phone = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Your phone number'}))

    class Meta:
        model = FiftyPoundChallengeSignup
        fields = ('name', 'email', 'phone')

    def __init__(self, *args, **kwargs):
        super(FiftyPoundChallengeForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal js-challenge'
        self.helper.label_class = 'col-lg-4'
        self.helper.field_class = 'col-lg-8'
        self.helper.form_method = "POST"
        self.helper.form_action = reverse('fifty_pound_challenge')


class FiftyPoundChallengeAccountForm(forms.ModelForm):

    account_type = forms.ChoiceField(choices=FiftyPoundChallengeAccount.ACCOUNT_TYPES, required=False)
    amount = forms.CharField(required=False)
    rate = forms.CharField(required=False)

    class Meta:
        exclude = ('challenge_signup',)

class FiftyPoundChallengeAccountFormHelper(FormHelper):

    def __init__(self, *args, **kwargs):
        super(FiftyPoundChallengeAccountFormHelper, self).__init__(*args, **kwargs)
        self.form_class = 'form-horizontal js-accounts'
        self.label_class = 'col-lg-4'
        self.field_class = 'col-lg-8'
        self.form_method = "post"
        self.layout = Layout(
            Div(
                Div(
                    'account_type',
                    PrependedText('amount', '£'),
                    AppendedText('rate', '%'),
                    css_class="panel-body"
                ),
                css_class="js-account-row panel"
            )
        )

class ProductQuestionaireForm(forms.ModelForm):

    first_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Your First name'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Your Last name'}))
    email = forms.EmailField()
    phone = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Your phone number'}))

    easy_access = forms.BooleanField(widget=forms.CheckboxInput(), required=False)
    notice_1_3 = forms.BooleanField(widget=forms.CheckboxInput(), label="Notice (1 to 3 months)", required=False)
    notice_3_6 = forms.BooleanField(widget=forms.CheckboxInput(), label="Notice (3 to 6 months)", required=False)
    fixed_rate_1 = forms.BooleanField(widget=forms.CheckboxInput(), label="1 to 3 Year Fixed Rate", required=False)
    fixed_rate_2 = forms.BooleanField(widget=forms.CheckboxInput(), label="Over 3 Year Fixed Rate", required=False)

    funds = forms.CharField(widget=forms.Select(choices=ProductQuestionaireSignup.FUND_CHOICES), label='Total funds')



    class Meta:
        model = ProductQuestionaireSignup

    def __init__(self, *args, **kwargs):
        super(ProductQuestionaireForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-5'
        self.helper.field_class = 'col-lg-7'
        self.helper.form_method = "POST"
        self.helper.form_action = reverse('product_questionaire')
        self.helper.layout = Layout(
            Div(
                Div(
                    Fieldset(
                        'Which accounts are of interest to you?',
                        'easy_access',
                        'notice_1_3',
                        'notice_3_6',
                        'fixed_rate_1',
                        'fixed_rate_2',
                    ),
                    css_class='col-md-6'
                ),
                Div(
                    Fieldset(
                        'Where can we contact you with matching new products?',
                        'funds',
                        'first_name',
                        'last_name',
                        'email',
                        'phone',
                    ),
                    css_class='col-md-6'
                ),
                css_class='row'
            ),
            Div(
                Div(
                    Submit('submit', 'Register Interest', css_class="btn-success pull-right"),
                    css_class='col-md-12',
                ),
                css_class='row'
            ),
        )


class TheBiggestMistakeForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Your name'}))
    email = forms.CharField(widget=Html5EmailInput(attrs={'placeholder': 'Where should we send your guide?'}))
    phone = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Your phone number'}))

    class Meta:
        model = TheBiggestMistakeSignup
        fields = ('name', 'email', 'phone')

    def __init__(self, *args, **kwargs):
        super(TheBiggestMistakeForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-10'
        self.helper.form_method = "POST"
        self.helper.form_action = reverse('the_biggest_mistake')
        self.helper.add_input(Submit('submit', 'Download guide', css_class="btn-savchamp col-lg-offset-4"))


class FactFindForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Your name'}))
    email = forms.CharField(widget=Html5EmailInput(attrs={'placeholder': 'Your email address'}))
    phone = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Your phone number'}))

    class Meta:
        model = FactFindSignup
        fields = ('name', 'email', 'phone')

    def __init__(self, *args, **kwargs):
        super(FactFindForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal js-challenge'
        self.helper.label_class = 'col-lg-4'
        self.helper.field_class = 'col-lg-8'
        self.helper.form_method = "POST"
        self.helper.form_action = reverse('fact_find')


class FactFindAccountForm(forms.ModelForm):

    account_type = forms.ChoiceField(choices=FactFindAccount.ACCOUNT_TYPES, required=False)
    provider = forms.ModelChoiceField(queryset=Provider.objects, required=False)
    amount = forms.CharField(required=False)
    rate = forms.CharField(required=False)

    class Meta:
        model = FactFindAccount
        exclude = ('challenge_signup',)

class FactFindAccountFormHelper(FormHelper):

    form_class = 'form-inline js-accounts'
    #field_template = 'bootstrap3/layout/inline_field.html'
    form_method = "post"
    layout = Layout(
        Div(
            Div(
                'account_type',
                css_class='col-md-3'
            ),
            Div(
                'provider',
                css_class='col-md-3'
            ),
            Div(
                PrependedText('amount', '£'),
                css_class='col-md-3'
            ),
            Div(
                AppendedText('rate', '%'),
                css_class='col-md-3'
            ),
            css_class="js-account-row"
        )
    )



class PensionOptionsForm(forms.ModelForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Your first name'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Your last name'}))
    email = forms.CharField(widget=Html5EmailInput(attrs={'placeholder': 'Where should we send your guide?'}))
    postcode = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Your postcode'}))
    phone = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Your phone number'}))

    class Meta:
        model = PensionOptionSignup
        fields = ('first_name', 'last_name', 'email', 'postcode', 'phone')

    def __init__(self, *args, **kwargs):
        super(PensionOptionsForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-4'
        self.helper.field_class = 'col-lg-8'
        self.helper.form_method = "POST"
        self.helper.form_action = reverse('pension_options_signup')
        self.helper.add_input(Submit('submit', 'Download guide', css_class="btn-success pull-right"))

class MindfulMoneyHealthcheckForm(forms.ModelForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Your first name'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Your last name'}))
    email = forms.CharField(widget=Html5EmailInput(attrs={'placeholder': 'Your email address'}))
    phone = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Your phone number'}))

    class Meta:
        model = MindfulMoneyHealthcheckSignup
        fields = ('first_name', 'last_name', 'email', 'phone')

    def __init__(self, *args, **kwargs):
        super(MindfulMoneyHealthcheckForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-4'
        self.helper.field_class = 'col-lg-8'
        self.helper.form_method = "POST"
        self.helper.form_action = reverse('mindful_money_healthcheck_signup')
        self.helper.add_input(Submit('submit', 'Get The Health Check', css_class="btn-success pull-right"))


class MoneyToTheMassesForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Your name'}))
    email = forms.CharField(widget=Html5EmailInput(attrs={'placeholder': 'Where should we send your guide?'}))
    phone = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Your phone number'}))

    class Meta:
        model = MoneyToTheMassesSignup
        fields = ('name', 'email', 'phone')

    def __init__(self, *args, **kwargs):
        super(MoneyToTheMassesForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-4'
        self.helper.field_class = 'col-lg-8'
        self.helper.form_method = "POST"
        self.helper.form_action = reverse('money_to_the_masses_signup')
        self.helper.add_input(Submit('submit', 'Download guide', css_class="btn-success"))


class ChallengerBankGuideForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Your name'}))
    email = forms.CharField(widget=Html5EmailInput(attrs={'placeholder': 'Where should we send your guide?'}))

    class Meta:
        model = ChallengerBankGuideSignup
        fields = ('name', 'email')

    def __init__(self, *args, **kwargs):
        super(ChallengerBankGuideForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-4'
        self.helper.field_class = 'col-lg-8'
        self.helper.form_method = "POST"
        self.helper.form_action = reverse('challenger_banks_guide_signup')
        self.helper.add_input(Submit('submit', 'Download guide', css_class="btn-success pull-right"))


class IHTSqueezePageForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput())
    email = forms.CharField(widget=Html5EmailInput())
    phone = forms.CharField(widget=forms.TextInput())

    class Meta:
        model = IHTSqueezePageSignup
        fields = ('name', 'email', 'phone')

    def __init__(self, *args, **kwargs):
        super(IHTSqueezePageForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-4'
        self.helper.field_class = 'col-lg-8'
        self.helper.form_method = "POST"
        self.helper.add_input(Submit('Download Now', 'Download Now', css_class="btn-savchamp"))
        self.helper.attrs = {
            'style': "text-align: center;color: white;background-color: rgba(10,10,10,0.3);border-radius: 3px;padding: 15px; margin-bottom:15px;"
        }

class PSASqueezePageForm(forms.ModelForm):
    email = forms.CharField(widget=Html5EmailInput())

    class Meta:
        model = PSASqueezePageSignup
        fields = ('email',)

    def __init__(self, *args, **kwargs):
        super(PSASqueezePageForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-10'
        self.helper.form_method = "POST"
        self.helper.add_input(Submit('Download Now', 'Download Now', css_class="btn-savchamp"))

class HighWorthSqueezePageForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput())
    email = forms.CharField(widget=Html5EmailInput())
    phone = forms.CharField(widget=forms.TextInput())

    class Meta:
        model = HighWorthSqueezePageSignup
        fields = ('name', 'email', 'phone')

    def __init__(self, *args, **kwargs):
        super(HighWorthSqueezePageForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-4'
        self.helper.field_class = 'col-lg-8'
        self.helper.form_method = "POST"
        self.helper.add_input(Submit('Download Now', 'Download Now', css_class="btn-savchamp"))
        self.helper.attrs = {
            'style': "text-align: center;color: white;background-color: rgba(10,10,10,0.3);border-radius: 3px;padding: 15px; margin-bottom:15px;"
        }
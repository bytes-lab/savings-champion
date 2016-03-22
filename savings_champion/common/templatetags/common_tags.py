from django import template
from common.models import Rates, Tweet, CarouselTab
from common.accounts.forms import SCRegistrationForm

from common.forms import DecisionTreeForm, NewsletterForm, RateAlertForm
from common.forms import AccountPickerForm
from django.contrib.auth.forms import AuthenticationForm
from django.conf import settings
register = template.Library()


class QuerySetNode(template.Node):
    """ Template node to return a queryset in a specified 
        variable in the context
    """

    def __init__(self, context_var, queryset=None):
        self.context_var = context_var
        self.queryset = queryset 

    def render(self, context):
        context[self.context_var] = self.queryset.all()
        return ''
  
RATES = 'rates'

class LatestTweetNode(template.Node):
    """ 
    """
    def __init__(self, context_var = 'tweet'):
        self.context_var = context_var

    def render(self, context):
        try :
            context[self.context_var] = Tweet.objects.latest('last_updated')
        except Tweet.DoesNotExist:
            pass
        return ''

class RatesNode(template.Node):
    """ 
    """
    def __init__(self, context_var = 'rates'):
        self.context_var = context_var

    def render(self, context):
        context[self.context_var] = Rates.objects.latest('last_updated')
        return ''
    

@register.tag(name="get_current_rates")
def get_current_rates(parser, token):
    func_name, _, context_var = token.split_contents()
    return RatesNode(context_var)


class GetFormNode(template.Node):
    """ Template node to return a queryset in a specified 
        variable in the context
    """

    def __init__(self, form_class, context_var, request):
        self.context_var = context_var
        self.request = template.Variable(request)
        self.form_class = form_class
        
    def render(self, context):
        request = self.request.resolve(context)
        
        if request.method == 'POST':
            form = self.form_class(request.POST)
        else:
            form = self.form_class()    
        context[self.context_var] = form
        return ''
     

@register.tag(name="get_registration_form")
def get_registration_form(parser, token):
    func_name, request, _, context_var = token.split_contents()
    return GetFormNode(SCRegistrationForm, context_var, request)


@register.tag(name="get_login_form")
def get_login_form(parser, token):
    func_name, request, _, context_var = token.split_contents()
    return GetFormNode(AuthenticationForm, context_var, request)


@register.tag(name="get_decision_tree_form")
def get_decision_tree_form(parser, token):
    """ We take care of simple formset loading through here, the view will deal with POST validation only """
    func_name, request, _, context_var = token.split_contents()
    return GetFormNode(DecisionTreeForm, context_var, request)


@register.tag(name="get_account_picker_form")
def get_account_picker_form(parser, token):
    """ We take care of simple formset loading through here, the view will deal with POST validation only """
    func_name, request, _, context_var = token.split_contents()
    return GetFormNode(AccountPickerForm, context_var, request)


@register.tag(name="get_newslettter_form")
def get_newslettter_form(parser, token):
    """ We take care of simple formset loading through here, the view will deal with POST validation only """
    func_name, request, _, context_var = token.split_contents()
    return GetFormNode(NewsletterForm, context_var, request)


@register.tag(name="get_rate_alert_form")
def get_rate_alert_form(parser, token):
    """ We take care of simple formset loading through here, the view will deal with POST validation only """
    func_name, request, _, context_var = token.split_contents()
    return GetFormNode(RateAlertForm, context_var, request)


@register.tag(name="get_latest_tweet")
def get_latest_tweet(parser, token):
    """ We take care of simple formset loading through here, the view will deal with POST validation only """
    func_name, _, context_var = token.split_contents()
    return LatestTweetNode(context_var)


@register.tag(name="get_carousel_tabs")
def get_carousel_tabs(parser, token):
    """ We take care of simple formset loading through here, the view will deal with POST validation only """
    func_name, _, context_var = token.split_contents()
    return QuerySetNode(context_var, queryset=CarouselTab.objects.all().order_by('order'))


@register.simple_tag()
def settings_value(name):
    return getattr(settings, name, "")


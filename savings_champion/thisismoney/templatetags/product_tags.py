from django import template
from django.conf import settings
from products.models import Provider, BestBuy, Product, ProviderBestBuy
from common.templatetags import QuerySetNode
from products.forms import PortfolioFormset, ReminderFormset
from products import utils
import json
register = template.Library()
from products.utils import get_maturity_based_bestbuys, get_ISA_bestbuys
import constants

@register.tag(name="get_providers_bestbuy_json")
def get_providers_bestbuy_json(parser, token):
    """
    Simple helper to get a list of product ids and the bestbuy ids that provider has.
    
    This is to simplify the lookup and ajax points by dumping an id list into the template
    """
    
    func_name, _, context_var = token.split_contents()
    return ProviderBestBuyJsonNode(context_var)

@register.tag(name="get_providers_isa_bestbuy_json")
def get_providers_isa_bestbuy_json(parser, token):
    """
    Simple helper to get a list of product ids and the bestbuy ids that provider has.
    
    This is to simplify the lookup and ajax points by dumping an id list into the template
    """
    
    func_name, _, context_var = token.split_contents()
    return ProviderISABestBuyJsonNode(context_var)

@register.tag(name="get_bestbuys_json")
def get_bestbuys_json(parser, token):
    """
    Simple helper to get a list of product ids and the bestbuy ids that provider has.
    
    This is to simplify the lookup and ajax points by dumping an id list into the template
    """
    
    func_name, _, context_var = token.split_contents()
    return BestBuyJsonNode(context_var)
 
@register.tag(name="get_isa_bestbuys_json")
def get_isa_bestbuys_json(parser, token):
    """
    Simple helper to get a list of product ids and the bestbuy ids that provider has.
    
    This is to simplify the lookup and ajax points by dumping an id list into the template
    """
    
    func_name, _, context_var = token.split_contents()
    return BestBuyISAJsonNode(context_var)

@register.tag(name="get_maturity_based_accounts")
def get_maturity_based_accounts(parser, token):
    """
    Simple helper to get a list of product ids and the bestbuy ids that provider has.
    
    This is to simplify the lookup and ajax points by dumping an id list into the template
    """
    
    func_name, _, context_var = token.split_contents()
    return MaturityBaseBestBuysNode(context_var)
 
class MaturityBaseBestBuysNode(template.Node):
    """ Template node to return a queryset in a specified 
        variable in the context
    """

    def __init__(self, context_var = 'json'):
        self.context_var = context_var

    def render(self, context):
        # TODO remove the hardcoding
        values = get_maturity_based_bestbuys()
        ret_val = []
        for value in values :
            ret_val.append({'id' : int(value.id)})
    
        context[self.context_var] = json.dumps(ret_val)
        return ''
     
class BestBuyISAJsonNode(template.Node):
    """ Template node to return a queryset in a specified 
        variable in the context
    """

    def __init__(self, context_var = 'json'):
        self.context_var = context_var

    def render(self, context):
        values = get_ISA_bestbuys()
        ret_val = []
        for value in values :
            ret_val.append({'id' : int(value.id), 'title' : value.title})
    
        context[self.context_var] = json.dumps(ret_val)
        return ''
  
class BestBuyJsonNode(template.Node):
    """ Template node to return a queryset in a specified 
        variable in the context
    """

    def __init__(self, context_var = 'json'):
        self.context_var = context_var

    def render(self, context):
        values = BestBuy.objects.all()
        ret_val = []
        for value in values :
            ret_val.append({'id' : int(value.id), 'title' : value.title})
    
        context[self.context_var] = json.dumps(ret_val)
        return ''
  
class ProviderBestBuyJsonNode(template.Node):
    """ Template node to return a queryset in a specified 
        variable in the context
    """

    def __init__(self, bestbuy, context_var = 'json'):
        self.context_var = context_var

    def render(self, context):
        values = ProviderBestBuy.objects.all()
        retval = []
        for value in values :
            provider = {'id': int(value.provider.id)}
            bestbuys = []
            
            for bestbuy in value.bestbuys.all() :
                bestbuys.append(int(bestbuy.id))
            provider['bestbuys'] = bestbuys
            retval.append(provider)
        context[self.context_var] = json.dumps(retval)
        return ''

class ProviderISABestBuyJsonNode(template.Node):
    """ Template node to return a queryset in a specified 
        variable in the context
    """
    def __init__(self, bestbuy, context_var = 'json'):
        self.context_var = context_var
        
    def render(self, context):
        isa_bestbuys = get_ISA_bestbuys()
        values = ProviderBestBuy.objects.filter(bestbuys__in= isa_bestbuys)

        retval = []
        for value in values :
            provider = {'id': int(value.provider.id)}
            bestbuys = []
            
            for bestbuy in value.bestbuys.filter(id__in = isa_bestbuys) :
                bestbuys.append(int(bestbuy.id))
            provider['bestbuys'] = bestbuys
            retval.append(provider)
        context[self.context_var] = json.dumps(retval)
        return ''
        
@register.tag(name="get_providers")
def get_providers(parser, token):
    """ Return all the featured plans as a context variable 
    TODO put limits on this
    """
  
    func_name, _, context_var = token.split_contents()
    return QuerySetNode(context_var, queryset=Provider.objects.all())

@register.tag(name="get_bestbuy_types")
def get_bestbuy_types(parser, token):
    """ 
    """
  
    func_name, _, context_var = token.split_contents()
    limit = 9
    return QuerySetNode(context_var, queryset=BestBuy.objects.filter(client_type='p')[:limit])

class BestBuyProductNode(template.Node):
    """ Template node to return a queryset in a specified 
        variable in the context
    """

    def __init__(self, bestbuy, context_var = 'portfolio'):
        self.context_var = context_var
        self.bestbuy= template.Variable(bestbuy)

    def render(self, context):
        bestbuy = self.bestbuy.resolve(context)
        context[self.context_var] = bestbuy.get_personal_products()
        return ''
    
@register.tag(name="get_bestbuy_products")
def get_bestbuy_products(parser, token):
    """ 
    """
    func_name, bestbuy, _, context_var = token.split_contents()
    return BestBuyProductNode(bestbuy, context_var)

@register.tag(name="get_product")
def get_product(parser, token):
    """ 
    """

    func_name, sc_code, _, context_var = token.split_contents()
    return QuerySetNode(context_var, queryset=Product.objects.filter(pk = 29))

class UserPortfolioNode(template.Node):
    """ Template node to return a queryset in a specified 
        variable in the context
    """

    def __init__(self, user, context_var = 'portfolio', limit = 5):
        self.context_var = context_var
        self.user= template.Variable(user)
        self.limit = limit

    def render(self, context):
        user = self.user.resolve(context)
        if user.is_authenticated():
            context[self.context_var] = user.portfolio_products.filter(productportfolio__is_deleted = False)[:self.limit]
        return ''
    

@register.tag(name="get_portfolio")
def get_portfolio(parser, token):
    """ 
    """
  
    func_name, user, _, context_var = token.split_contents()
    return UserPortfolioNode(user, context_var)


class InlineFormSetNode(template.Node):
    """ Template node to return a queryset in a specified 
        variable in the context
    """

    def __init__(self, user, context_var, formset):
        self.context_var = context_var
        self.user = template.Variable(user)
        self.formset = formset
        
    def render(self, context):
        user = self.user.resolve(context)
        if user.is_authenticated():
            if context.get(self.context_var, None) is None :
                context[self.context_var] = self.formset(instance = user)
        return ''   

@register.tag(name="get_portfolio_formset")
def get_portfolio_formset(parser, token):
    """ We take care of simple formset loading through here, the view will deal with POST validation only """
    func_name, user, _, context_var = token.split_contents()
    return InlineFormSetNode(user, context_var, formset = PortfolioFormset)

@register.tag(name="get_reminder_formset")
def get_reminder_formset(parser, token):
    """ We take care of simple formset loading through here, the view will deal with POST validation only """
    func_name, user, _, context_var = token.split_contents()
    return InlineFormSetNode(user, context_var, formset = ReminderFormset)


@register.filter
def get_page_view(session):
    """
    If we find the session variable results set, we embed a virtual page view in the calling page.
    
    """
    if session.get(constants.RESULTS, False) != False:
        return session.get(constants.RESULTS)
    return False

@register.filter
def clear_page_view(session):
    """
    If we find the session variable results set, we embed a virtual page view in the calling page.
    
    """
    if session.get(constants.RESULTS, False) != False:
        session[constants.RESULTS] = False
    return ''




from django import template
from products.models import BestBuy
from common.templatetags import QuerySetNode
register = template.Library()

@register.inclusion_tag('products/topaccounts/advantages.html')
def get_bestbuy_pros(bestbuy):
    pros = bestbuy.advantagesblock_set.filter(type='pro')
    return {'pros' : pros}

@register.inclusion_tag('products/topaccounts/disadvantages.html')
def get_bestbuy_cons(bestbuy):
    cons = bestbuy.advantagesblock_set.filter(type='con')
    return {'cons' : cons}

@register.tag(name="get_ratealert_bestbuys")
def get_ratealert_bestbuys(parser, token):
    """ 
    """
  
    func_name, _, context_var = token.split_contents()
    return QuerySetNode(context_var, queryset=BestBuy.objects.filter(has_table=True, client_type='p'))

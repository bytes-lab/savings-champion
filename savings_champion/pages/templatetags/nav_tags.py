from django import template
from common.templatetags import QuerySetNode
from pages.models import ParentPage, ChildPage
from products.models import BestBuy

register = template.Library()

@register.tag(name="get_main_nav")
def get_main_nav(parser, token):
    func_name, _, context_var = token.split_contents()
    return QuerySetNode(context_var, ParentPage.objects.filter(main_nav=True))

@register.tag(name="get_footer_nav")
def get_footer_nav(parser, token):
    func_name, _, context_var = token.split_contents()
    return QuerySetNode(context_var, ChildPage.objects.filter(footer_nav=True).order_by('order'))

@register.tag(name="get_bestbuy_nav")
def get_bestbuy_nav(parser, token):
    func_name, _, context_var = token.split_contents()
    return QuerySetNode(context_var, BestBuy.objects.filter(has_table=True).order_by('-client_type', 'order'))

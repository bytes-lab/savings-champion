from django import template
from common.templatetags import QuerySetNode
from pages.models import FAQ

register = template.Library()

@register.tag(name="get_concierge_faqs")
def get_concierge_faqs(parser, token):
    func_name, _, context_var = token.split_contents()
    faq, _ = FAQ.objects.get_or_create(title="Concierge")
    return QuerySetNode(context_var, faq.faqblock_set.all().order_by('order')[:4])

@register.tag(name="get_healthcheck_faqs")
def get_concierge_faqs(parser, token):
    func_name, _, context_var = token.split_contents()
    faq, _ = FAQ.objects.get_or_create(title="Healthcheck")
    return QuerySetNode(context_var, faq.faqblock_set.all().order_by('order')[:4])
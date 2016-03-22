from django import template

register = template.Library()

@register.filter
def as_percent(gross_rate, max_gross_rate):
    if gross_rate > 0 and max_gross_rate > 0:
        return int((gross_rate / max_gross_rate)*100)
    return 0

@register.filter
def divide_by(gross_rate, value):
    if gross_rate > 0 :
        return gross_rate / 2
    return 0

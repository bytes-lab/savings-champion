from decimal import Decimal
import re
from django import template
from django.conf import settings
from django.utils.encoding import force_text
from django.utils.formats import number_format

register = template.Library()

@register.filter(name='lookup')
def lookup(dictionary, key):
    return dictionary.get(key)


@register.filter(is_safe=True)
def intcomma2dp(value, use_l10n=True):
    """
    Converts an integer to a string containing commas every three digits.
    For example, 3000 becomes '3,000' and 45000 becomes '45,000'.
    """
    if settings.USE_L10N and use_l10n:
        try:
            if not isinstance(value, (float, Decimal)):
                value = int(value)
        except (TypeError, ValueError):
            return intcomma2dp(value, False)
        else:
            return number_format(value, force_grouping=True, decimal_pos=2)
    orig = force_text(value)
    new = re.sub("^(-?\d+)(\d{3})", '\g<1>,\g<2>', orig)
    if orig == new:
        return new
    else:
        return intcomma2dp(new, use_l10n)
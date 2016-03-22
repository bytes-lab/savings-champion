"""
Special field to handle currency
"""
from django import forms
import re
from decimal import *
import string

EMPTY_VALUES = ['', None, ' ']
class CurrencyField(forms.RegexField):
    #currencyRe = re.compile(r'^[0-9]{1,5}(.[0-9][0-9])?$')
    currencyRe = re.compile(r'^(\d{1,3}(\,\d{3})*|(\d+))(\.\d{2})*$')
    
    def __init__(self, *args, **kwargs):
        super(CurrencyField, self).__init__(self.currencyRe, None, None, *args, **kwargs)

    def clean(self, value):
        """
        Although its a RegexField, we need to remove any commas before 
        converting it to a float.
        """
        value = super(CurrencyField, self).clean(value)
        if value not in EMPTY_VALUES:
            value = value.replace(',', '')
        else:
            value = '0'
        value = re.sub("[^0-9.]", "", value)
        return Decimal(value)

class CurrencyInput(forms.TextInput):
    def render(self, name, value, attrs=None):
        if value != '':
            try:
                value = value
            except TypeError:
                pass
        return super(CurrencyInput, self).render(name, value, attrs)
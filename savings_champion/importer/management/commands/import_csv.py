# -*- coding: utf-8 -*-
# this job will can be run manually or by a cron job
import re
import datetime
from decimal import *


DECIMAL_RE = re.compile('[\d][\.\d]*')
INT_RE = re.compile('[\d]+')
BOOLEAN = 'boolean'
STRING = 'string'
DECIMAL = 'decimal'
INTEGER = 'integer'
DATETIME = 'datetime'
DATE = 'date'
PERCENT = 'percent'
DEFAULT = 'default'
ATTRIBUTE = 'attribute'
ROW_TITLE = 'row_title'
REQUIRED = 'required'
VALIDATE = 'validate'
IS_FOREIGNKEY = 'is_foreignkey'
IS_MONTHLY = 'is_monthly'
EMPTY_VALUES = ['', None, ' ', ]


def get_decimal(val, is_required):
    try:
        retval = float(val)
        return "%.4g" % retval
        #match = DECIMAL_RE.search(val)
        #if match:
        #    return match.group()
        # TODO maybe do None
        #return None  
    except ValueError:
        pass

    return None


def get_integer(val, is_required):
    match = INT_RE.search(val)
    if match:
        return match.group()
    if is_required:
        return 0
    return 0


TRUE_TYPES = [1, '1', 'true', 'y']


def get_bool(val, is_required=False):
    if val.lower() in TRUE_TYPES:
        return True
    return False


def get_date(val, is_required=False):
    if val not in EMPTY_VALUES:
        return datetime.datetime.strptime(val, '%Y-%m-%d')

    return None


def get_percent(val, is_required=False):
    """ For some reason some data has come through as percent rather than decimals """
    match = DECIMAL_RE.search(val)
    # i need this to be in exactly the same format as the rest, therefore I need to /100 etc
    if match and match.group() not in EMPTY_VALUES:
        val = Decimal(match.group()) / 100
        return val
    return None


def get_datetime(val, is_required=False):
    if val not in EMPTY_VALUES:
        return datetime.datetime.strptime(val, '%d/%m/%Y %H:%M:%S')
    return None


def get_string(val, is_required=False):
    return val


def get_value(value, validation_type, is_required):
    if validation_type == DECIMAL:
        return get_decimal(value, is_required)
    elif validation_type == INTEGER:
        return get_integer(value, is_required)
    elif validation_type == DATETIME:
        return get_datetime(value, is_required)
    elif validation_type == DATE:
        return get_date(value, is_required)
    elif validation_type == BOOLEAN:
        return get_bool(value, is_required)
    elif validation_type == PERCENT:
        return get_percent(value, is_required)
    return get_string(value, is_required)




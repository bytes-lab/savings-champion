from __future__ import absolute_import
from celery import task
from decimal import Decimal
import datetime
from django.db.models.base import Model
from sortedcontainers import SortedSet
from concierge.engine import compare_existing_portfolio_to_generated

__author__ = 'josh'


def convert_to_json(value):
    if isinstance(value, Decimal):
        value = float(value)
    if isinstance(value, datetime.datetime) or isinstance(value, datetime.date):
        value = value.isoformat()
    if isinstance(value, Model):
        value = {
            'pk': value.pk,
            'provider': value.product.provider.title,
            'title': value.product.title,
            'term': value.product.term,
            'fixed_term_date': value.product.term_fixed_date,
            'notice': value.product.notice,
            'facts': value.product.facts
        }
    if isinstance(value, SortedSet):
        value = list(value)
        value = convert_to_json_safe(value)
    if isinstance(value, dict) or isinstance(value, list) or isinstance(value, tuple) or isinstance(value, frozenset):
        value = convert_to_json_safe(value)
    return value


def convert_to_json_safe(result):
    if isinstance(result, list) or isinstance(result, tuple) or isinstance(result, set) or isinstance(result, frozenset):
        safe_result = []
        for item in result:
            safe_result.append(convert_to_json(item))
    elif isinstance(result, dict):
        safe_result = {}
        for key, value in result.iteritems():
            safe_result[key] = convert_to_json(value)
    else:
        safe_result = convert_to_json(result)

    return safe_result


@task(soft_time_limit=60, time_limit=120)
def async_api_concierge_engine_run(*args, **kwargs):
    result = compare_existing_portfolio_to_generated(*args, **kwargs)
    safe_result = convert_to_json_safe(result)
    return safe_result
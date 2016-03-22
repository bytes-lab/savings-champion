from django.core import management

__author__ = 'josh'

from celery import shared_task


@shared_task(ignore_result=True)
def async_update_products_from_salesforce():
    management.call_command('salesforce_rest_api_mirror')
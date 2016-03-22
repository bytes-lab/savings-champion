# -*- coding: utf-8 -*-
from rest_framework.response import Response
from rest_framework.views import APIView
from products.models import Product
from django.db.models import Q
import datetime
from datetime import timedelta

from products.fields import CurrencyField
from decimal import *
from django.core.exceptions import ValidationError

ACCOUNT_NAME = 'account_name'
PROVIDER = 'provider'
ACCOUNT_TYPE = 'account_type'
BALANCE = 'balance'

EMPTY_VALUES = ['', None, u'', 'unknown']

from rest_framework import serializers


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ('id', 'title')


class ProductList(APIView):
    def get(self, request, format=None):
        results = Product.objects.all()

        if PROVIDER in request.GET.keys() and request.GET[PROVIDER] not in EMPTY_VALUES:
            results = results.filter(provider__pk=request.GET[PROVIDER])

        if ACCOUNT_TYPE in request.GET.keys() and request.GET[ACCOUNT_TYPE] not in EMPTY_VALUES:
            results = results.filter(bestbuy_type__pk=request.GET[ACCOUNT_TYPE])

        if BALANCE in request.GET.keys() and request.GET[BALANCE] not in EMPTY_VALUES:
            balance = request.GET[BALANCE]
            balance = balance.replace(",", "")
            balance = balance.replace(u"£", "")
            fld = CurrencyField()

            try:
                value = fld.clean(balance)
            except (ValidationError, InvalidOperation):
                value = 0

            if value >= 0:
                results = results.filter(minimum__lte=value, maximum__gte=value)
            else:
                # there's something fishy going on
                results = Product.objects.none()

        # Flawed as this will grow and grow
        # FLAWED FLAWED
        results = results.filter(publish_after__lt=datetime.datetime.now() + timedelta(days=1),
                                 is_fixed=False,
                                 master_product__status__in=['Live', 'Closed']
                                 ).order_by('title', '-publish_after', '-maximum')

        # new_results = []
        #
        # tmpval = {}
        # for result in results:
        #     if not tmpval.get(result.sf_product_id, False):
        #         new_results.append(result)
        #         tmpval[result.sf_product_id] = True
        #     else:
        #         continue
        #
        # results = new_results

        data = ProductSerializer(results, many=True).data
        return Response(data)
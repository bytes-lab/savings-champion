from django.http import JsonResponse
from piston.handler import BaseHandler
from django.utils.text import slugify
from rest_framework import serializers
from rest_framework.renderers import JSONRenderer
from products.models import BestBuy
PROVIDER = 'provider'

EMPTY_VALUES = ['', None, u'']
class BestBuysHandler(BaseHandler):
    """
    Return a list of current bestbuys on the system
    """
    
    allowed_methods = ('GET')
    model = BestBuy
    
    fields = ('id', 'title', 'slug')
    
    
    def read(self, request):
        """
        """ 
        results = self.model.objects.all()
        
        if PROVIDER in request.GET.keys() and request.GET[PROVIDER] not in EMPTY_VALUES:
            results = self.model.objects.filter(bestbuy_products__provider__slug =slugify(request.GET[PROVIDER])).distinct()
        return results


class BestbuySerializer(serializers.ModelSerializer):
    class Meta:
        model = BestBuy
        fields = ('id', 'title', 'slug')


def bestbuy(request):
    results = BestBuy.objects.all()

    if PROVIDER in request.GET.keys() and request.GET[PROVIDER] not in EMPTY_VALUES:
        results = BestBuy.objects.filter(bestbuy_products__provider__slug=slugify(request.GET[PROVIDER]), client_type='p').distinct()
    return JsonResponse(BestbuySerializer(results, many=True).data, safe=False)

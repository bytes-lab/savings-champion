from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from products.models import Provider

EMPTY_VALUES = ['', u'', None]
PROVIDER = 'provider'


class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = ('id', 'title', 'slug')

def provider(request):
    results = Provider.objects.all()

    # if PROVIDER in request.GET.keys() and request.GET[PROVIDER] not in EMPTY_VALUES:
    #     results = results.filter(title__istartswith=request.GET[PROVIDER])

class ProviderList(APIView):

    def get(self, request, format=None):
        results = Provider.objects.all()
        if PROVIDER in request.GET.keys() and request.GET[PROVIDER] not in EMPTY_VALUES:
            results = results.filter(title__istartswith=request.GET[PROVIDER])
        data = ProviderSerializer(results, many=True).data
        return Response(data)


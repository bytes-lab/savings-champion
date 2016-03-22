from django.http import JsonResponse
from rest_framework.views import APIView
from products.ajax.product_handler import ProductSerializer
from products.models import Provider, MasterProduct

from django.views.decorators.cache import never_cache

@never_cache
def retrieve_personal_products(request):
    if request.method == 'GET':
        provider_id = request.GET.get('providerid')
        provider = Provider.objects.get(pk=provider_id)
        
        masterproducts = MasterProduct.objects.filter(provider=provider, account_type='P', bestbuy_type__ratetracker_enabled=True) \
                                              .exclude(status="Deleted") \
                                              .exclude(bestbuy_type__is_fixed=True)
        products = []
        for mp in masterproducts:
            mp_result = mp.return_product()
            if mp_result:
                products.append(mp_result)
        return JsonResponse(products, safe=False)


@never_cache
def retrieve_provider_fixed_types(request):
    if request.method == 'GET':
        provider_id = request.GET.get('providerid')
        
        provider = Provider.objects.get(pk=provider_id)
        bestbuys = MasterProduct.objects.filter(provider=provider, account_type='P',
                                                bestbuy_type__ratetracker_enabled=True) \
                                        .exclude(status="Deleted") \
                                        .exclude(bestbuy_type__is_fixed=False).order_by('bestbuy_type__title').values_list('bestbuy_type__pk', 'bestbuy_type__title').distinct()

        return JsonResponse(list(bestbuys), safe=False)
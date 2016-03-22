from django.http import HttpResponse, Http404, JsonResponse
from products.models import Provider, ProviderBestBuy, MasterProduct, BestBuy
import json
from django.shortcuts import redirect


def retrieve_products(request):
    if request.is_ajax() and request.method == 'GET':
        provider_id = request.GET.get('provider')
        balance = request.GET.get('balance')
        account_type = request.GET.get('account_type')     
        provider = Provider.objects.get(pk=provider_id)
        
        masterproducts = MasterProduct.objects.filter(provider=provider, bestbuy_type__pk=account_type, account_type='P', bestbuy_type__ratetracker_enabled=True)
        #gotta filter those fixed rate products out
        products = []
        for mp in masterproducts:
            mp_result = mp.return_product_within_balance(balance)
            if mp_result:
                products.append(mp_result)
        return JsonResponse(list(products), safe=False)
    else:
        return redirect('ajax_required')


def get_bestbuys(request):
    if request.is_ajax() and request.method == 'GET':
        provider_id = request.GET.get('provider')
        provider = Provider.objects.get(pk=provider_id)
        providerbb, _ = ProviderBestBuy.objects.get_or_create(provider=provider)

        bestbuys_list = providerbb.bestbuys.filter(ratetracker_enabled=True).values_list('pk', 'title')
        return JsonResponse(list(bestbuys_list), safe=False)
    return Http404()
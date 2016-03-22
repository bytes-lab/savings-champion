import json
from django.http import HttpResponse
from products.models import Provider, MasterProduct, BestBuy

ACCOUNT_NAME = 'account_name'
PROVIDER = 'provider'
ACCOUNT_TYPE = 'account_type'
BALANCE = 'balance'

EMPTY_VALUES = ['', None, u'', 'unknown']

def retrieveAllProducts(request):
    if request.is_ajax() and request.method == 'GET':
        provider_id = request.GET.get('providerid')
        balance = request.GET.get('balanceval')
        provider = Provider.objects.get(pk=provider_id)
        account_type = request.GET.get('account_type')
        bestbuy = BestBuy.objects.get(id=account_type)
        masterproducts = MasterProduct.objects.filter(provider=provider, bestbuy_type=bestbuy)
        products = []
        for mp in masterproducts:
            mp_result = mp.return_product()
            if mp_result:
                products.append(mp_result)
        return HttpResponse(json.dumps(list(products)), mimetype="application/json")
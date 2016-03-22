"""
This is currently a daily job that associates Providers to specific BestBuys, this is 
used to help the F/E output dropdowns on the Ratetracker pages where a lot of information
is interdependant. Rather than doing a lot of extra crazy processing we minimise by making 
a decent link table to hold all this information.
"""

from django.core.management.base import NoArgsCommand
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.contrib.sites.models import Site

from django.conf import settings


from products.models import Provider, BestBuy, Product, ProviderBestBuy
import datetime
class Command(NoArgsCommand):
    
    def _get_start_date(self, dte, minus_days = 50):
        dte =  dte + datetime.timedelta(days = -minus_days)
        return datetime.datetime.combine(dte.date(), datetime.time.min)
    
    def _get_end_date(self, dte):
        dte =  self._get_query_date(dte)
        return datetime.datetime.combine(dte.date(), datetime.time.max)
    
    def _get_query_date(self, dte, minus_days = 5):
        return dte + datetime.timedelta(days = -minus_days)
    
    def handle_noargs(self, **options):
        """ Get all Providers that have been recently updated """
        dte = self._get_query_date(datetime.datetime.now())

        
        products = Product.objects.filter(
                               last_updated__gte = self._get_start_date(dte),
                               )
        products = Product.objects.all()
        for product in products :
            provider_best_buy, created = ProviderBestBuy.objects.get_or_create(provider = product.provider)
            # now make sure this pbb has m2ms needed
            
            for bestbuy in product.bestbuy_type.all() :
               provider_best_buy.bestbuys.add(bestbuy) 
     
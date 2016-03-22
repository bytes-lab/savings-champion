from django.conf import settings
from django.db.models import Q
BESTBUYS_COUNT = getattr(settings, 'BESTBUYS_COUNT', 5)
from products.models import Product, BestBuy, Ranking
from decimal import *

def calculate(tax_rate, product, lump_sum = 0, monthly_amount = 0, is_monthly = False, months = 12):
    """Assumes no previous calculations have occured
    TODO do we use monthly gross rate?
    """

    lump_sum_interest = 0
    
    if is_monthly and product.monthly_gross :
        aer = product.monthly_gross
    else : 
        aer = product.aer 
    
    # luckily we do not calculate every tax band just on or off
    if tax_rate :
        aer = aer * Decimal('0.8') 
            
    if lump_sum > 0:
        
        lump_sum_interest = (lump_sum * aer)
        #lump_sum += lump_sum_interest
        
    i = 1  
    monthly_interest = 0
    monthly_amounts = 0

    if monthly_amount:
        while i <= months :
            segment_aer = aer/12
            net_aer = segment_aer * i
            monthly_interest += (monthly_amount * net_aer)
            monthly_amounts += monthly_amount
    
            i+=1
    #print monthly_interest
    return (lump_sum + lump_sum_interest) + (monthly_amounts + monthly_interest), lump_sum_interest + monthly_interest                 
    
EMPTY_VALUES= ['', None, ' ']


def cleaned_data_to_params(cleaned_data):
    """
    Because we're potnetially passing through more than one parameter to be handled as one Next, 
    do we need to do something clever
    XXX this contains a fudge to get two fields to marry up - i.e. product and account_name
    """ 
    retval = 'search=True&'
    for key, value in cleaned_data.items():
        if value not in EMPTY_VALUES :
            
            if hasattr(value, 'id'):
                retval +='%s=%s&' %(key, value.id)
            else :
                retval += '%s=%s&' %(key, value)
          
    return retval

def get_products_by_bestbuy(bestbuy):
    return bestbuy.get_personal_products()
    
    #Old method of retrieving the products linked to a best buy. Replaced by a method that links to 
    #the best buy table which has a list of the products currently associated with it.
    
    
    #filters = {}
    #ordering = Product.get_ordering(bestbuy.slug)
    #filters['%s__lte' % ordering] = 5
    #filters['bestbuy_type'] = bestbuy
    #filters['status'] = 'live'

    #return Product.objects.filter(**filters)\
     #                   .order_by(Product.get_ordering(bestbuy.slug))[0:BESTBUYS_COUNT]
                        
                    
def get_maturity_based_bestbuys():
    # TODO remove this hardcode
    return BestBuy.objects.filter(slug__in=['fixed-rate-bond', 'fixed-rate-isa'])

def get_ISA_bestbuys():
    # TODO remove this hardcode
    return BestBuy.objects.filter(title__icontains='isa', client_type='p')

def get_reset_candidates():
    #filter out the product that have any bestbuys of less than 10  
    #XXX CDH would rather do this dynamically       
    products = Product.objects.filter(Q(bbrating_easyaccess__lt=10) | \
                                      Q(bbrating_variable_isa__lt=10) | \
                                      Q(bbrating_easyaccess__lt=10) | \
                                      Q(bbrating_fixedrate_bonds__lt=10) | \
                                      Q(bbrating_fixed_isa__lt=10) | \
                                      Q(bbrating_notice__lt=10) | \
                                      Q(bbrating_over50__lt=10) | \
                                      Q(bbrating_monthly_income__lt=10) | \
                                      Q(bbrating_regularsavings__lt=10) | \
                                      Q(bbrating_childrenssavings__lt=10)| \
                                      Q(bbrating_variable_bond__lt=10))

    products_list = list(products.values_list('id',flat=True))
    return products_list
    
    
def update_reset_candidates(products=Product.objects.all()):
    """Reset update bestbuys on list set of products"""
    bestbuy_fields = Product.get_bestbuy_fields()
    updates = {}
    
    for fld in bestbuy_fields :
        updates['%s' %fld] = 0
        
    #apply the updates
    product_update = products.update(**updates)
    
    print "PRODUCT_COUNT= %s" %product_update

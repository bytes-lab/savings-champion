 # -*- coding: utf-8 -*-
from django.core.management.base import NoArgsCommand

from products.models import Product, MasterProduct

class Command(NoArgsCommand):    
    def handle_noargs(self, **options):
        scList = Product.objects.all()
        
        for sc in scList:
            try:
                masterProduct = MasterProduct.objects.get(sf_product_id=sc.sf_product_id)
            except MasterProduct.DoesNotExist:                
                masterProduct = MasterProduct()
                masterProduct.sf_product_id = sc.sf_product_id
                sc.title = sc.title.replace(u' ֲ£', u' £') #For some reason there seems to be a lot of this about so automated replace yay
                sc.save()
                masterProduct.title = sc.title.encode('UTF-8')
                
                masterProduct.status = sc.status
                masterProduct.provider = sc.provider
            
                masterProduct.account_type = sc.account_type
                
                masterProduct.is_internet_access = sc.is_internet_access
                masterProduct.is_phone_access = sc.is_phone_access
                masterProduct.is_post_access = sc.is_post_access
                masterProduct.is_branch_access = sc.is_branch_access
                masterProduct.is_cc_access = sc.is_cc_access
            
                masterProduct.is_open_internet = sc.is_open_internet
                masterProduct.is_open_telephone = sc.is_open_telephone
                masterProduct.is_open_post = sc.is_open_post
                masterProduct.is_open_branch = sc.is_open_branch
                masterProduct.is_open_cc = sc.is_open_cc
                
                masterProduct.is_isa_transfers_in = sc.is_isa_transfers_in
                
                
                masterProduct.fscs_licence = sc.fscs_licence
                try:
                    masterProduct.save()
                except Exception as e:
                    print e
                    print sc.sc_code

        
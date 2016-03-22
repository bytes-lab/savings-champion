# -*- coding: utf-8 -*-
from django.core.management.base import NoArgsCommand
from products.models import MasterProduct


class Command(NoArgsCommand):    
    def handle_noargs(self, **options):
        masterList = MasterProduct.objects.all()
        
        for mp in masterList:
            latestProduct = mp.get_latest_sc_code()
            
            mp.title = latestProduct.title
            
            mp.provider = latestProduct.provider
            
            mp.status = latestProduct.status
            mp.bestbuy_type = latestProduct.bestbuy_type.all()
            mp.account_type = latestProduct.account_type            
    
            mp.is_internet_access = latestProduct.is_internet_access
            mp.is_phone_access = latestProduct.is_phone_access
            mp.is_post_access = latestProduct.is_post_access
            mp.is_branch_access = latestProduct.is_branch_access
            mp.is_cc_access = latestProduct.is_cc_access
        
            mp.is_open_internet = latestProduct.is_open_internet
            mp.is_open_telephone = latestProduct.is_open_telephone
            mp.is_open_post = latestProduct.is_open_post
            mp.is_open_branch = latestProduct.is_open_branch
            mp.is_open_cc = latestProduct.is_open_cc
            mp.is_isa_transfers_in = latestProduct.is_isa_transfers_in
            
            mp.is_fixed = latestProduct.is_fixed
            
            if latestProduct.facts:
                latestProduct.facts = latestProduct.facts.replace(u' ֲ£', u' £') #For some reason there seems to be a lot of this in the facts section
                latestProduct.save()  # save the £ fix
                mp.facts = latestProduct.facts.encode('utf-8')
            mp.fscs_licence = latestProduct.fscs_licence

            try:
                mp.save()
            except Exception as e:
                print e
                print latestProduct.sc_code
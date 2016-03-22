from django.core.management.base import NoArgsCommand

from products.models import Product, MasterProduct

class Command(NoArgsCommand):    
    def handle_noargs(self, **options):
        scList = Product.objects.all()
        
        for sc in scList:
            try:
                sc.master_product = MasterProduct.objects.get(sf_product_id=sc.sf_product_id)
                sc.save()
            except Exception as e:
                print e
                print sc.sc_code
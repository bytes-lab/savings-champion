"""
Resets bestbuys for products that have a bestby value of five or less 
"""

from django.core.management.base import NoArgsCommand

from products.utils import get_reset_candidates, update_reset_candidates

class Command(NoArgsCommand):
    
    def handle_noargs(self, **options):
        # First of all get all the best buys 
        reset_products = get_reset_candidates()
        
        # Now update them 
        update_reset_candidates(reset_products)
        

        
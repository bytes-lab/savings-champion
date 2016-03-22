from piston.handler import BaseHandler
from products.models import ProductPortfolio
from products.forms import ProductReminderForm
from decimal import *
from piston.utils import validate

ACCOUNT_NAME = 'account_name'
PROVIDER = 'provider'
ACCOUNT_TYPE = 'account_type'
BALANCE = 'balance'

EMPTY_VALUES = ['', None, u'']


class TrackerHandler(BaseHandler):
    model = ProductPortfolio
    
    @validate(ProductReminderForm)
    def create(self, request):
        """
        Creates a new blogpost.
        """
        attrs = self.flatten_dict(request.POST)
        import pdb
        pdb.set_trace()
        if self.exists(**attrs):
            return rc.DUPLICATE_ENTRY
        else:
            post = ProductPortfolio(title=attrs['title'], 
                            content=attrs['content'],
                            author=request.user)
            post.is_synched = False
            post.save()
            
            return post

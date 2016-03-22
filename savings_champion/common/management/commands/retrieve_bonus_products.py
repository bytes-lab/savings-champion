from django.core.management.base import NoArgsCommand
from products.models import Product
from django.conf import settings
import csv
import os
from django.core.mail import EmailMessage

DUPLICATE_EMAILS_PATH = getattr(settings, 'DUPLICATE_EMAILS_PATH')
ALERTS_CSV_EMAIL = getattr(settings, 'CSV_EXPORT_RECIPIENTS')

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        date_format = "bonus"
        
        productList = Product.objects.all()
        bonus_list = []
        
        fn = os.path.join(DUPLICATE_EMAILS_PATH % date_format)
        f1 = open(fn, 'wb')
        fwr = csv.writer(f1, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        fwr.writerow(['SCcode', 'Provider', 'ProductName', 'BonusAmount', 'BonusTerm', 'FixedEndDate', 'UnderlyingGross'])
        
        accounts = 0
        
        for product in productList:
            if product.show_opening_date():
                fwr.writerow([product.sc_code.encode('ascii', 'ignore'), 
                              product.provider, product.title.encode('ascii', 'ignore'),
                              product.bonus_amount, product.bonus_term,
                              product.bonus_end_date,
                              product.underlying_gross_rate])
                accounts += 1
        
        f1.close()
        
        email = EmailMessage('Products with bonuses', 
                             'There are currently %s products with bonuses' % accounts, 
                             settings.DEFAULT_FROM_EMAIL,
                             ALERTS_CSV_EMAIL,)
        
        email.attach_file(fn)
        email.send()

from django.core.management.base import NoArgsCommand
from products.models import ProductPortfolio, RatetrackerReminder, Product
import csv
import os
from django.core.mail import EmailMessage
from django.conf import settings

USER_EXPORT_PATH = getattr(settings, 'USER_EXPORT_PATH')
#have to split portfolio. FRB needs work
class Command(NoArgsCommand):    
    def handle_noargs(self, **options):
        
        #get all the portfolios
        
        portfolioList = ProductPortfolio.objects.all()
        reminderList = RatetrackerReminder.objects.all()
        
        failed_portfolios = []
        
        fn = os.path.join(USER_EXPORT_PATH % 'Portfolios')
            
        f = open(fn, 'wb')                                                     
        fwr = csv.writer(f, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        
        for portfolio in portfolioList:
            try:
                fwr.writerow([portfolio.user.id, portfolio.balance, portfolio.opening_date, "pp%s" % portfolio.id, True, 
                              portfolio.product.sc_code, portfolio.user.id])
            except Exception as ex:
                failed_portfolios.append("Portfolio ID %s failed because of %s \n" % (portfolio.id, ex))
        
        for reminder in reminderList:
            try:
                productCode = 'SCxxxxx'
                #products = Product.objects.filter(provider=reminder.provider_id).filter(publish_after__year=1970)
                #for product in products:
                #    best_buys = product.bestbuy_type.values_list()
                #   for best_buy in best_buys:
                #       if best_buy[0] == reminder.account_type_id:
                #           productCode = product.sc_code
                if reminder.account_type_id == 14:
                    products = Product.objects.filter(provider=reminder.provider_id).filter(title='DJANGO FIXED RATE BOND') 
                else:
                    products = Product.objects.filter(provider=reminder.provider_id).filter(title='DJANGO FIXED RATE ISA')
                    
                if products:
                    productCode = products[0].sc_code
        
                fwr.writerow([reminder.user.id, reminder.balance, reminder.maturity_date, "rr%s" % reminder.id, True, 
                                  productCode, reminder.user.id])
            except Exception as ex:
                failed_portfolios.append("Reminder ID %s failed because of %s \n" % (reminder.id, ex))
        f.close()
        
        email = EmailMessage('Portfolio Salesforce List', 
                                 ('The following users failed: \n %s' % "".join(failed_portfolios)), 
                                 settings.DEFAULT_FROM_EMAIL,
                ['info@savingschampion.co.uk'],)
            
        email.attach_file(fn)
        email.send()


#prt.Balance = reminder.balance
#                prt.OpeningDate = reminder.maturity_date
#                prt.Id = reminder.id
#                prt.RateTrack = True
#    
#                # XXX get a product have to find appropriate product that is published in 1970, this can almost certainly 
#                # be optomised if required. Also relies on their only being 1 product that matches this way.
#                productCode = 'SCxxxxx'
#                products = Product.objects.filter(provider=reminder.provider_id).filter(publish_after__year=1970)
#                for product in products:
#                    best_buys = product.bestbuy_type.values_list()
#                    for best_buy in best_buys:
#                        if best_buy[0] == reminder.account_type_id:
#                            productCode = product.sc_code
#    
#                prt.UserId = reminder.user.id
#                prt.SCCode = productCode
#                try:
#                    if reminder.is_deleted == True:
#                        returncode = django_client.service.deleteRateTracker(reminder.user.id, prt)

#<xsd:element name="newRateTracker">
#    <xsd:complexType>
#     <xsd:sequence>
#      <xsd:element name="pUserId" type="xsd:string" nillable="true"/>
#      <xsd:element name="pProductPortfolio" type="tns:ProductPortfolio" nillable="true"/>
#     </xsd:sequence>
#    </xsd:complexType>
    
#prt = django_client.factory.create('ProductPortfolio')
#            prt.Balance = portfolio.balance
#            prt.OpeningDate = portfolio.opening_date
#            prt.Id = portfolio.id
#            prt.RateTrack = True
#            prt.SCCode = portfolio.product.sc_code
#            prt.UserId = portfolio.user.id
#            try:
#                if portfolio.is_deleted == True:
#                    returncode = django_client.service.deleteRateTracker(portfolio.user.id, prt)
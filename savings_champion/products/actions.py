from products.models import MasterProduct
from django.conf import settings
import csv, os, datetime
from django.core.mail import EmailMessage, send_mail
USER_EXPORT_PATH = getattr(settings, 'USER_EXPORT_PATH')

def ExportMasterProducts(modeladmin, request, queryset):
    
    today = datetime.datetime.now()
    date_format = today.strftime('%Y%m%d')
    failed_products = []
    
    fn = os.path.join(USER_EXPORT_PATH % date_format)
    f1 = open(fn, 'wb')
    fwr = csv.writer(f1, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    fwr.writerow(['Product', 'SFID'])
    
    masterProducts = MasterProduct.objects.all()
    for mp in masterProducts:
        try:                
            fwr.writerow([mp.title, mp.sf_product_id])
        except Exception, ex:
            try:
                failed_products.append(" because %s \n" % ex)
            except:
                failed_products.append(ex)    
    f1.close()
        
    email = EmailMessage('Product Export List', 
                             ('The following products failed: \n %s' % "".join(failed_products)), 
                             settings.DEFAULT_FROM_EMAIL,
            ['admin@savingschampion.co.uk'],)
        
    email.attach_file(fn)
    email.send()
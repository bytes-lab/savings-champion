from django.contrib.auth import get_user_model
from importer.management.commands import readers
from django.conf import settings
import csv, os, datetime
from django.core.mail import EmailMessage
from products.models import ProductPortfolio, RatetrackerReminder, Product
from common.models import NewsletterSignup, Profile

User = get_user_model()

USER_EXPORT_PATH = getattr(settings, 'USER_EXPORT_PATH')


def ExportUsers(modeladmin, request, queryset):
    
    today = datetime.datetime.now()
    date_format = today.strftime('%Y%m%d')
    failed_users = []
    
    fn = os.path.join(USER_EXPORT_PATH % date_format)
    f1 = open(fn, 'wb')
    fwr = csv.writer(f1, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    fwr.writerow(['Email', 'Firstname', 'Surname', 'Telephone', 'Postcode', 'Newsletters', 'RateAlerts'])
        
    for file in queryset:
        csv_file = readers.UnicodeReader(open(file.csv_file.path, 'rb'), encoding='utf-8')
        for row in csv_file:
            try:                
                user = User.objects.get(email__iexact=row[0])
                try:
                    profile = user.profile
                except Profile.DoesNotExist:
                    profile = Profile(user=user)
                    profile.save()
                except Profile.MultipleObjectsReturned:
                    profiles = Profile.objects.filter(user=user)
                    profile = profiles[0]
                fwr.writerow([user.email, user.first_name, user.last_name, profile.telephone, profile.postcode, profile.newsletter, profile.ratealerts])
            except Exception, ex:
                try:
                    if not row[0] == "Email":
                        failed_users.append(row[0])
                        failed_users.append(" because %s \n" % ex)
                except:
                    failed_users.append(ex)
        file.has_been_run = True
        file.save()
        file.csv_file.close()
    
    f1.close()
        
    email = EmailMessage('User Export List', 
                             ('The following users failed: \n %s' % "".join(failed_users)), 
                             settings.DEFAULT_FROM_EMAIL,
            ['info@savingschampion.co.uk'],)
        
    email.attach_file(fn)
    email.send()    

def ExportUserProducts(modeladmin, request, queryset):
    
    today = datetime.datetime.now()
    date_format = today.strftime('%Y%m%d')
    failed_users = []
    
    fn = os.path.join(USER_EXPORT_PATH % date_format)
    f1 = open(fn, 'wb')
    fwr = csv.writer(f1, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    fwr.writerow(['Email', 'Firstname', 'Surname', 'Provider', 'Product', 'Account Type', 'Balance', 'Deleted'])
        
    for file in queryset:
        csv_file = readers.UnicodeReader(open(file.csv_file.path, 'rb'), encoding='utf-8')
        for row in csv_file:
            try:                
                user = User.objects.get(email__iexact=row[0])
                try:
                    profile = user.profile
                except Profile.DoesNotExist:
                    profile = Profile(user=user)
                    profile.save()
                except Profile.MultipleObjectsReturned:
                    profiles = Profile.objects.filter(user=user)
                    profile = profiles[0]
                varproducts = ProductPortfolio.objects.filter(user=user)
                fixedproducts = RatetrackerReminder.objects.filter(user=user)
                for varproduct in varproducts:
                    fwr.writerow([user.email, user.first_name, user.last_name, varproduct.provider, varproduct.account_type, 
                                  varproduct.product, varproduct.balance, varproduct.is_deleted])
                
                for reminder in fixedproducts:
                    fwr.writerow([user.email, user.first_name, user.last_name, reminder.provider, reminder.account_type, 
                                  '', reminder.balance, reminder.is_deleted])
            except Exception, ex:
                try:
                    if not row[0] == "Email":
                        failed_users.append(row[0])
                        failed_users.append(" because %s \n" % ex)
                except:
                    failed_users.append(ex)
        file.has_been_run = True
        file.save()
        file.csv_file.close()
    
    f1.close()
        
    email = EmailMessage('User Export List', 
                             ('The following users failed: \n %s' % "".join(failed_users)), 
                             settings.DEFAULT_FROM_EMAIL,
            ['info@savingschampion.co.uk'],)
        
    email.attach_file(fn)
    email.send()

def AddUsersNewsletter(modeladmin, request, queryset):
    
    today = datetime.datetime.now()
    date_format = today.strftime('%Y%m%d')
    failed_users = []

    for file in queryset:
        csv_file = readers.UnicodeReader(open(file.csv_file.path, 'rb'), encoding='utf-8')
        for row in csv_file:
            try:
                user = NewsletterSignup.objects.get(email=row[0])
            except NewsletterSignup.DoesNotExist:                
                user = NewsletterSignup()
                user.email = row[0]
                user.is_synched = False
                user.save()
            except Exception, ex:
                try:
                    if not row[0] == "Email":
                        failed_users.append(row[0])
                        failed_users.append(" because %s \n" % ex)
                except:
                    failed_users.append(ex)
        file.has_been_run = True
        file.save()
        file.csv_file.close()
    
        
    email = EmailMessage('Added Users to Newsletter Signups', 
                             ('The following users failed: \n %s' % "".join(failed_users)), 
                             settings.DEFAULT_FROM_EMAIL,
            ['info@savingschampion.co.uk'],)
        
    email.send()
    
def AddUsersNewsletterFlag(modeladmin, request, queryset):
    
    today = datetime.datetime.now()
    date_format = today.strftime('%Y%m%d')
    failed_users = []
    
        
    for file in queryset:
        csv_file = readers.UnicodeReader(open(file.csv_file.path, 'rb'), encoding='utf-8')
        for row in csv_file:
            try:
                user = User.objects.get(email__iexact=row[0])
                try:
                    profile = user.profile
                except Profile.DoesNotExist:
                    profile = Profile(user=user)
                    profile.save()
                except Profile.MultipleObjectsReturned:
                    profiles = Profile.objects.filter(user=user)
                    profile = profiles[0]
                profile.newsletter = True
                profile.is_synched = False
                profile.save()
            except Exception, ex:
                try:
                    if not row[0] == "Email":
                        failed_users.append(row[0])
                        failed_users.append(" because %s \n" % ex)
                except:
                    failed_users.append(ex)
        file.has_been_run = True
        file.save()
        file.csv_file.close()
    
        
    email = EmailMessage('Added Users to Newsletter Signups', 
                             ('The following users failed: \n %s' % "".join(failed_users)), 
                             settings.DEFAULT_FROM_EMAIL,
            ['admin@savingschampion.co.uk'],)
        
    email.send()

def RemoveUsersNewsletterFlag(modeladmin, request, queryset):
    
    today = datetime.datetime.now()
    date_format = today.strftime('%Y%m%d')
    failed_users = []
    
        
    for file in queryset:
        csv_file = readers.UnicodeReader(open(file.csv_file.path, 'rb'), encoding='utf-8')
        for row in csv_file:
            try:
                user = User.objects.get(email__iexact=row[0])
                try:
                    profile = user.profile
                except Profile.DoesNotExist:
                    profile = Profile(user=user)
                    profile.save()
                except Profile.MultipleObjectsReturned:
                    profiles = Profile.objects.filter(user=user)
                    profile = profiles[0]
                profile.newsletter = False
                profile.is_synched = False
                profile.save()
            except Exception, ex:
                try:
                    if not row[0] == "Email":
                        failed_users.append(row[0])
                        failed_users.append(" because %s \n" % ex)
                except:
                    failed_users.append(ex)
        file.has_been_run = True
        file.save()
        file.csv_file.close()
    
        
    email = EmailMessage('Removed Users newsletter flag', 
                             ('The following users failed: \n %s' % "".join(failed_users)), 
                             settings.DEFAULT_FROM_EMAIL,
            ['admin@savingschampion.co.uk'],)
        
    email.send()
    
def RemoveUsersRateAlertFlag(modeladmin, request, queryset):
    
    today = datetime.datetime.now()
    date_format = today.strftime('%Y%m%d')
    failed_users = []
    
        
    for file in queryset:
        csv_file = readers.UnicodeReader(open(file.csv_file.path, 'rb'), encoding='utf-8')
        for row in csv_file:
            try:
                user = User.objects.get(email__iexact=row[0])
                try:
                    profile = user.profile
                except Profile.DoesNotExist:
                    profile = Profile(user=user)
                    profile.save()
                except Profile.MultipleObjectsReturned:
                    profiles = Profile.objects.filter(user=user)
                    profile = profiles[0]
                profile.ratealerts = False
                profile.is_synched = False
                profile.save()
            except Exception, ex:
                try:
                    if not row[0] == "Email":
                        failed_users.append(row[0])
                        failed_users.append(" because %s \n" % ex)
                except:
                    failed_users.append(ex)
        file.has_been_run = True
        file.save()
        file.csv_file.close()
    
        
    email = EmailMessage('Removed Users Rate Alert Flag', 
                             ('The following users failed: \n %s' % "".join(failed_users)), 
                             settings.DEFAULT_FROM_EMAIL,
            ['admin@savingschampion.co.uk'],)
        
    email.send()


def DeleteSCCodes(modeladmin, request, queryset):
    
    today = datetime.datetime.now()
    date_format = today.strftime('%Y%m%d')
    errors = []
    
        
    for file in queryset:
        csv_file = readers.UnicodeReader(open(file.csv_file.path, 'rb'), encoding='utf-8')
        for row in csv_file:
            try:
                product = Product.objects.get(sc_code=row[0])
                product.delete()
            except Exception, ex:
                try:
                    errors.append(row[0])
                    errors.append(" because %s \n" % ex)
                except:
                    errors.append(ex)
        file.has_been_run = True
        file.save()
        file.csv_file.close()
    
        
    email = EmailMessage('Deleted Sc Codes', 
                             ('The following rows failed: \n %s' % "".join(errors)), 
                             settings.DEFAULT_FROM_EMAIL,
            ['admin@savingschampion.co.uk'],)
        
    email.send()
    
ExportUsers.short_description = "Export Details about users"
ExportUserProducts.short_description = "Export User Products"        
AddUsersNewsletter.short_description = "Add emails to newsletter signups"
AddUsersNewsletterFlag.short_description = "Add newsletter flag to profiles"
RemoveUsersNewsletterFlag.short_description = "Mark newsletter subs as unsubscribed"
RemoveUsersRateAlertFlag.short_description = "Mark Rate Alert subs as unsubscribed"
DeleteSCCodes.short_description = "Delete Products from database by sc code"
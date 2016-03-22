from django.contrib.auth import get_user_model
from django.core.management.base import NoArgsCommand
from common.models import CampaignsSignup, Profile
import csv
import os
from django.core.mail import EmailMessage
from django.conf import settings

User = get_user_model()

USER_EXPORT_PATH = getattr(settings, 'USER_EXPORT_PATH')

class Command(NoArgsCommand):
    
    def _get_subscription_bitmask(self, profile):
        if not profile.skeleton_user:
            retval = 8
        else:
            retval = 0
        if profile.newsletter :
            retval += 1
        if profile.ratealerts :
            retval += 2
        try:
            signup = CampaignsSignup.objects.get(email=profile.user.email)
            retval += 16
        except:
            pass
        return retval
    
    def handle_noargs(self, **options):
        #get all users and then export them to a csv for syncing with salesforce (for newUser4)
        failed_users=[]
        userList = User.objects.all()
        fn = os.path.join(USER_EXPORT_PATH  % 'all')
            
        f = open(fn, 'wb')                                                     
        fwr = csv.writer(f, delimiter=',', quoting=csv.QUOTE_MINIMAL)

        for user in userList:
            try:
                try:
                    profile = user.profile
                except Profile.DoesNotExist:
                    profile = Profile(user=user)
                    profile.save()
                
                #GET ALT TEL AND BEST TIME TO CALL
                try:
                    signup = CampaignsSignup.objects.get(email=profile.user.email)
                    alt_tel = signup.alt_telephone
                    best_time = signup.best_call_time
                except:
                    alt_tel = ''
                    best_time = ''
                subscriptions = self._get_subscription_bitmask(profile)
                fwr.writerow([user.id, user.username, user.email, user.first_name, user.last_name, 
                              profile.dob, profile.telephone, profile.salutation, profile.postcode, 
                              subscriptions, profile.source, alt_tel, best_time, user.is_active, user.date_joined])
            except Exception as ex:
                try:
                    failed_users.append("%s failed because %s \n" % (user.email, ex))
                except:
                    failed_users.append("%s \n" % ex)
            
        f.close()
        
        email = EmailMessage('User Salesforce List', 
                            ('The following users failed: \n %s' % "".join(failed_users)),
                             settings.DEFAULT_FROM_EMAIL,
                             ['info@savingschampion.co.uk'],)
            
        email.attach_file(fn)
        email.send()
        
    
    
    
    
   
    
        
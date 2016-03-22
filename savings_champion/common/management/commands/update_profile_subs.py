from django.contrib.auth import get_user_model
from django.core.management.base import NoArgsCommand
from django.conf import settings
from common.models import RateAlertsSignup, NewsletterSignup, Profile
from django.core.mail import send_mail

User = get_user_model()

#Use this command sparingly as it will take forever I suspect. (looping through quite a few entries)
class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        newsletterList = NewsletterSignup.objects.all()
        ratealertsList = RateAlertsSignup.objects.all()
        
        failed_users = []
        for newsletter in newsletterList:
            try:
                user = User.objects.get(email__iexact=newsletter.email)

                try:
                    profile = user.profile
                except Profile.DoesNotExist:
                    profile = Profile(user=user)
                    profile.save()
                
                profile.newsletter = True
                profile.save()
            except User.DoesNotExist:
                pass
            except Exception as ex:
                failed_users.append(newsletter.email)
                failed_users.append(" because %s \n" % ex)
            
        for ratealert in ratealertsList:
            try:
                user = User.objects.get(email__iexact=ratealert.email)
                
                profile = user.profile
                
                profile.ratealert = True
                profile.save()
                
            except User.DoesNotExist:
                pass
            except Exception as ex:
                failed_users.append(ratealert.email)
                failed_users.append(" because %s \n" % ex)
                                
        send_mail('Profile Status', "The following signups failed: %s " % "".join(failed_users), 
                  settings.DEFAULT_FROM_EMAIL, ['info@savingschampion.co.uk'], fail_silently=False)
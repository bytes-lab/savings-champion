import string
from random import Random
from django.contrib.sites.models import RequestSite
from django.shortcuts import redirect
from registration import signals
from registration.backends.default.views import RegistrationView
from common.accounts.forms import SCRegistrationForm
from common.accounts.utils import create_stage_one_profile
from common.models import Profile
from registration.models import RegistrationProfile
from django.conf import settings
from django.contrib.auth import login, get_user_model
from common.models import UserNext
from thisismoney.models import TiMSignups
from common.models import RateAlertsSignup, NewsletterSignup, CampaignsSignup
from products.models import ProductPortfolio, Product, BestBuy
import datetime

User = get_user_model()

UUID = 'uuid'


# class SCBackend1(RegistrationView):
#     def _get_subscription_bitmask(self, profile):
#         retval = 8
#         if profile.newsletter:
#             retval += 1
#         if profile.ratealerts:
#             retval += 2
#         try:
#             if CampaignsSignup.objects.filter(email=profile.user.email).exists():
#                 retval += 16
#         except:
#             pass
#         return retval
#
#     def get_form_class(self, request=None):
#         """
#         Return the default form class used for user registration.
#         """
#         return SCRegistrationForm
#
#
#     def register(self, request, **kwargs):
#         email, password, first_name, last_name = kwargs['email'], kwargs['password1'], kwargs['first_name'], kwargs[
#             'surname']
#         site = RequestSite(request)
#         #kwargs['dob'], kwargs['telephone'], kwargs['title'],
#         dob = kwargs.get('dob', None)
#         telephone = kwargs.get('telephone', None)
#         salutation = kwargs.get('salutation', None)
#         postcode = kwargs.get('postcode', None)
#         newsletter = kwargs.get('newsletter', False)
#         ratealerts = kwargs.get('ratealerts', False)
#
#         try:
#             new_user = User.objects.get(email__iexact=email)
#             try:
#                 profile = new_user.profile
#             except Profile.DoesNotExist:
#                 profile = Profile(user=new_user)
#                 profile.save()
#             except Profile.MultipleObjectsReturned:
#                 profiles = Profile.objects.filter(user=new_user)
#                 profile = profiles[0]
#
#             if profile.skeleton_user:
#                 new_user.first_name = first_name
#                 new_user.last_name = last_name
#                 new_user.set_password(password)
#                 new_user.is_active = False
#                 new_user.save()
#
#                 registration_profile = RegistrationProfile.objects.create_profile(new_user)
#
#                 registration_profile.send_activation_email(site)
#         except User.DoesNotExist:
#
#             username = self._make_username()
#
#             new_user = RegistrationProfile.objects.create_inactive_user(username, email,
#                                                                         password, site, send_email=False)
#             new_user.first_name = first_name
#             new_user.last_name = last_name
#             new_user.save()
#
#             signals.user_registered.send(sender=self.__class__,
#                                          user=new_user,
#                                          request=request)
#             # Create a new Member Profile for this user based on all the other fields
#
#             profile = Profile()
#             profile.user = new_user
#
#         profile.dob = dob
#         profile.salutation = salutation
#         profile.postcode = postcode
#         profile.telephone = telephone
#         profile.salutation = salutation
#         profile.newsletter = newsletter
#         profile.ratealerts = ratealerts
#         profile.is_synched = False
#         profile.skeleton_user = False
#
#         try:
#             if RateAlertsSignup.objects.filter(email=email).exists():
#                 profile.ratealerts = True
#         except:
#             pass
#         try:
#             if NewsletterSignup.objects.filter(email=email).exists():
#                 profile.newsletter = True
#         except:
#             pass
#
#         profile.save()
#
#         if UUID in request.POST:
#             UserNext.objects.create(user=new_user, uuid=request.POST[UUID])
#
#         return new_user
#
#     def timregister(self, request, new_uuid, **kwargs):
#         email, password, first_name, last_name = kwargs['email'], kwargs['password1'], kwargs['first_name'], kwargs[
#             'surname']
#         site = RequestSite(request)
#         dob = kwargs.get('dob', None)
#         telephone = kwargs.get('telephone', None)
#         salutation = kwargs.get('salutation', None)
#         postcode = kwargs.get('postcode', None)
#         newsletter = kwargs.get('newsletter', False)
#         ratealerts = kwargs.get('ratealerts', False)
#         source = kwargs.get('source', None)
#
#         new_user, user_created = create_stage_one_profile(request=request, email=email, source='this_is_money')
#         new_user.set_password(password)
#         new_user.first_name = first_name
#         new_user.last_name = last_name
#
#         try:
#             new_user = User.objects.get(email__iexact=email)
#             try:
#                 profile = new_user.profile
#             except Profile.DoesNotExist:
#                 profile = Profile(user=new_user)
#                 profile.save()
#             except Profile.MultipleObjectsReturned:
#                 profiles = Profile.objects.filter(user=new_user)
#                 profile = profiles[0]
#
#             if profile.skeleton_user:
#                 new_user.first_name = first_name
#                 new_user.last_name = last_name
#                 new_user.set_password(password)
#                 new_user.is_active = False
#                 new_user.save()
#
#                 registration_profile = RegistrationProfile.objects.create_profile(new_user)
#
#                 registration_profile.send_activation_email(site)
#         except User.DoesNotExist:
#
#             username = self._make_username()
#
#             new_user = RegistrationProfile.objects.create_inactive_user(username, email,
#                                                                         password, site)
#             new_user.first_name = first_name
#             new_user.last_name = last_name
#             new_user.save()
#
#             signals.user_registered.send(sender=self.__class__,
#                                          user=new_user,
#                                          request=request)
#             # Create a new Member Profile for this user based on all the other fields
#
#             profile = Profile()
#             profile.user = new_user
#
#         UserNext.objects.create(user=new_user, uuid=new_uuid)
#
#         #kwargs['dob'], kwargs['telephone'], kwargs['title'],
#
#         profile.dob = dob
#         profile.salutation = salutation
#         profile.postcode = postcode
#         profile.telephone = telephone
#         profile.salutation = salutation
#         profile.newsletter = newsletter
#         profile.ratealerts = ratealerts
#         profile.source = source
#         profile.is_synched = False
#         profile.skeleton_user = False
#
#         if RateAlertsSignup.objects.filter(email=email).exists():
#             profile.ratealerts = True
#         if NewsletterSignup.objects.filter(email=email).exists():
#             profile.newsletter = True
#
#         profile.save()
#
#         provider = request.POST['provider']
#         id = request.POST['product']
#         balance = request.POST['balance']
#
#         if id > 0 and balance > 0 and provider > 0:
#             product = Product.objects.get(pk=id)
#             portfolio = ProductPortfolio()
#             portfolio.user = new_user
#
#             portfolio.account_type = BestBuy.objects.get(id=product.bestbuy_type.all()[0].id)
#             portfolio.balance = request.POST['balance']
#             portfolio.product = product
#             portfolio.provider = product.provider
#
#             # When making I found some bonus terms can be entered as '' as well as None
#             # hence the ugly if statement to ensure it is an int
#             # as it only gets evaluated on portfolio.save() which by then a typeerror try/except is too late as it
#             # could be any field
#
#             if product.bonus_term:
#                 if product.bonus_term > 0:
#                     portfolio.bonus_term = product.bonus_term
#                 else:
#                     portfolio.bonus_term = None
#             else:
#                 portfolio.bonus_term = None
#             try:
#                 month = int(request.POST['opening_date_month'])
#                 year = int(request.POST['opening_date_year'])
#                 portfolio.opening_date = datetime.datetime(year, month, 01)
#             except:
#                 pass
#             portfolio.notice = product.notice
#             portfolio.save()
#         return new_user
#
#     def activate(self, request, activation_key):
#         """
#         On Activation we send across our details to Campaign Monitor and not before
#         """
#         try:
#             user = RegistrationProfile.objects.get(activation_key=activation_key)
#         except RegistrationProfile.DoesNotExist:
#             user = None
#         if user is not None:
#             user.is_active = True
#             user.backend = 'django.contrib.auth.backends.ModelBackend'
#             login(request, user)
#             if TiMSignups.objects.filter(email=user.email).exists():
#                 timSignup = TiMSignups.objects.get(email=user.email)
#                 timSignup.completed_activation = True
#                 timSignup.save()
#             try:
#                 profile = user.profile
#             except Profile.DoesNotExist:
#                 profile = Profile(user=user)
#                 profile.save()
#             except Profile.MultipleObjectsReturned:
#                 profiles = Profile.objects.filter(user=user)
#                 profile = profiles[0]
#             profile.skeleton_user = False
#             profile.is_synched = False
#             profile.save()
#
#         return redirect('activation_complete')
#
#
#     def _make_username(self):
#         username = '%s%s' % (settings.USERNAME_STEM, self._make_random())
#         try:
#             User.objects.get(username=username)
#         except User.DoesNotExist:
#             return username
#
#     def _make_random(self, length=8, chars=string.letters + string.digits):
#         random_string = ''.join(Random().sample(string.letters + string.digits, 12))
#         return random_string
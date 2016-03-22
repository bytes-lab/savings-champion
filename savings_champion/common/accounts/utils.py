import string
from django.conf import settings
from random import Random
from django.contrib.auth import get_user_model
from django.contrib.sites.models import get_current_site
from django.shortcuts import redirect
from registration.models import RegistrationProfile
from common.models import Profile
from common.utils import record_referral_signup
from stats.client import StatsDClient

User = get_user_model()

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', None)
    if x_forwarded_for is not None:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def _make_random(length=22, chars=string.letters + string.digits):
    random_string = ''.join(Random().sample(string.letters + string.digits, 22))
    return random_string

def MakeUsername():
    username = '%s%s' % (settings.USERNAME_STEM, _make_random())
    
    while User.objects.filter(username=username).exists():
        username = '%s%s' % (settings.USERNAME_STEM, _make_random())
    return username


def Stage1Profile(user, request=None, source=None):
    profile, _ = Profile.objects.get_or_create(user=user)
    profile.is_synched = False
    profile.skeleton_user = False
    profile.filled_in_name = False
    if request is not None:
        profile.ip_address = get_client_ip(request)
    else:
        profile.ip_address = '127.0.0.1'
    profile.source = source
    profile.save()


def Stage2Profile(email, first_name, surname, telephone):
    user = User.objects.get(email__iexact=email)
    user.first_name = first_name
    user.last_name = surname
    user.save()
    try:
        profile = user.profile
    except Profile.DoesNotExist:
        profile = Profile(user=user)
        profile.save()
    except Profile.MultipleObjectsReturned:
        profiles = Profile.objects.filter(user=user)
        profile = profiles[0]
    profile.telephone = telephone
    profile.is_synched = False
    profile.filled_in_name = True
    profile.save()


def BasketInitialProfile(email, first_name=None, surname=None, telephone = None, newsletter=False, ratealert=False):
    user = User.objects.get(email__iexact=email)
    try:
        profile = user.profile
    except Profile.DoesNotExist:
        profile = Profile(user=user)
        profile.save()
    except Profile.MultipleObjectsReturned:
        profiles = Profile.objects.filter(user=user)
        profile = profiles[0]
    if first_name and surname:
        user.first_name = first_name
        user.last_name = surname
        user.save()
        profile.filled_in_name = True
        
    profile.telephone = telephone
    profile.newsletter = newsletter
    profile.ratealerts = ratealert
    profile.is_synched = False
    profile.source = "Basket"
    
    profile.save()


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def create_stage_one_profile(request, email, source, send_activation=True, login_user=True, use_site_framework=True):
    user_created = False
    record_stats = False
    try:
        user = User.objects.get(email__iexact=email)
    except User.MultipleObjectsReturned:
        user = User.objects.filter(email__iexact=email).earliest('date_joined')
        # Found more than one account with this email, use the first one.
    except User.DoesNotExist:
        password = User.objects.make_random_password(50)  # make a 50 char password for temporary use
        site = get_current_site(request)
        username = MakeUsername()
        user = RegistrationProfile.objects.create_inactive_user(site=site,
                                                                send_email=send_activation,
                                                                request=request,
                                                                username=username,
                                                                password=password,
                                                                email=email)
        user_created = True
    try:
        profile = user.profile
    except Profile.DoesNotExist:
        profile = Profile(user=user)
        profile.save()
    except Profile.MultipleObjectsReturned:
        profiles = Profile.objects.filter(user=user)
        profile = profiles.earliest()
    if profile.skeleton_user:
        if request is not None:
            profile.ip_address = get_client_ip(request)
        else:
            profile.ip_address = '127.0.0.1'
        profile.save()
    elif send_activation and not user.is_active and not user_created:
        return redirect('resend_activation')
    elif login_user and user.is_active is True:
        return redirect('auth_login')

    Stage1Profile(user, request, source)
    if not email.endswith('@local'):
        record_referral_signup(request, user, user_created, 'signup')

        statsd_client = StatsDClient().get_counter_client(
            client_name='user.profile.created'
        )
        statsd_client += 1

        statsd_client = StatsDClient().get_counter_client(
            client_name='user.profile.created.{source}'.format(
                source=source
            )
        )
        statsd_client += 1

        statsd_client = StatsDClient().get_counter_client(
            client_name='user.profile.created.{source}.{path}'.format(
                source=source,
                path=request.path
            )
        )
        statsd_client += 1

        record_stats = True

    return user, user_created, record_stats


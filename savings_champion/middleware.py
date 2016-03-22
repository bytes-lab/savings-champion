import datetime
import platform

from django.http import HttpResponseRedirect
from django.conf import settings
from common.models import Referrer

import re
from stats.client import StatsDClient


class SecureRequiredMiddleware(object):
    def __init__(self):
        self.paths = getattr(settings, 'SECURE_REQUIRED_PATHS')
        self.enabled = self.paths and getattr(settings, 'HTTPS_SUPPORT')

    def process_request(self, request):
        if self.enabled and not request.is_secure():
            for path in self.paths:
                if request.get_full_path().startswith(path):
                    request_url = request.build_absolute_uri(request.get_full_path())
                    secure_url = request_url.replace('http://', 'https://')
                    return HttpResponseRedirect(secure_url)


class SubdomainsMiddleware:
    def process_request(self, request):
        try:
            request.domain = request.META['HTTP_HOST']
        except KeyError:
            request.domain = ''
        request.subdomain = ''
        parts = request.domain.split('.')

        # blog.101ideas.cz or blog.localhost:8000 
        if len(parts) >= 3 or (re.match("^localhost", parts[-1]) and len(parts) == 2):
            request.subdomain = parts[0]
            request.domain = '.'.join(parts[1:])

        # set the right urlconf

        if settings.DEBUG:
            request.urlconf = 'thisismoney.urls'
        elif request.subdomain == 'thisismoney':
            request.urlconf = 'thisismoney.urls'
        elif request.subdomain == 'tim':
            request.urlconf = 'thisismoney.urls'
        else:
            request.urlconf = 'urls'


P3P_COMPACT = 'CP="NID DSP ALL COR"'  # I import this from a global constants file


# eg. P3P_COMPACT='CP="CAO DSP CURa ADMa DEVa TAIa CONa OUR DELa BUS IND PHY ONL UNI PUR COM NAV DEM STA"'

class MiddlewareResponseInjectP3P(object):
    def __init__(self):
        self.process_response = self.inject

    def inject(self, request, response):
        response['P3P'] = P3P_COMPACT
        return response


class ReferrerSavingMiddleware(object):
    def process_request(self, request):
        referer = None
        campaign = None
        term = None
        medium = None
        referrer_object = None
        if request.method == 'GET':
            if 'utm_source' in request.GET:
                referer = request.GET['utm_source']
            if 'utm_medium' in request.GET:
                medium = request.GET['utm_medium']
            if 'utm_term' in request.GET:
                term = request.GET['utm_term']
            if 'utm_campaign' in request.GET:
                campaign = request.GET['utm_campaign']

        if referer is not None:
            referrer_object, _ = Referrer.objects.get_or_create(name=referer)
            request.session.save()
            request.session.modified = True
            request.session['referer'] = referrer_object.pk
            request.session['medium'] = medium
            request.session['term'] = term
            request.session['campaign'] = campaign
            request.session.save()
            request.first_session = 'true'
            request.referrer = referrer_object

        if 'first_session' in request.COOKIES:
            request.first_session = 'true'
            referrer_object, _ = Referrer.objects.get_or_create(pk=request.COOKIES['referer'])
            request.referrer = referrer_object

        statsd_client = StatsDClient().get_counter_client(
            client_name='user.hit.{referrer}.{campaign}.{medium}.{term}'.format(
                referrer=referrer_object.name if request.session.get('referer', None) is not None else 'None',
                medium=request.session.get('medium', None),
                term=request.session.get('term', None),
                campaign=request.session.get('campaign', None)
            )
        )
        statsd_client += 1

    def process_response(self, request, response):

        if hasattr(request, 'session') and 'referer' in request.session:
            max_age = 365 / 2  # 6 Months
            expires = datetime.datetime.utcnow() + datetime.timedelta(days=max_age)
            response.set_cookie('referer',
                                request.session['referer'],
                                expires=expires,
                                max_age=datetime.timedelta(days=max_age).seconds
                                )
            response.set_cookie('first_session',
                                'true',
                                expires=expires,
                                max_age=None
                                )
            response.set_cookie('medium',
                                request.session['medium'],
                                expires=expires,
                                max_age=datetime.timedelta(days=max_age).seconds
                                )
            response.set_cookie('term',
                                request.session['term'],
                                expires=expires,
                                max_age=datetime.timedelta(days=max_age).seconds
                                )
            response.set_cookie('campaign',
                                request.session['campaign'],
                                expires=expires,
                                max_age=datetime.timedelta(days=max_age).seconds
                                )
        return response


class ServerIdentification(object):
    def process_response(self, request, response):
        response['x-processed-by'] = platform.node()
        return response

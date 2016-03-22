from django.db import IntegrityError
import urllib
from django.core.urlresolvers import reverse
import csv
import codecs
import cStringIO
from common.models import Referrer, UserReferral, better_slugify

def as_slug(val):
    return better_slugify(val)


class ResponseError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def get_subscription_bitmask(profile):
    retval = 0
    if profile.newsletter:
        retval += 1

    if profile.ratealerts:
        retval += 2
    return retval


def build_url(*args, **kwargs):
    get = kwargs.pop('get', {})
    url = reverse(*args, **kwargs)
    if get:
        url += '?' + urllib.urlencode(get)
    return url


class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")

class UnicodeDictReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)
        self.header = self.reader.next()

    def next(self):
        row = self.reader.next()
        vals = [unicode(s, "utf-8") for s in row]
        return dict((self.header[x], vals[x]) for x in range(len(self.header)))

    def __iter__(self):
        return self

class UnicodeDictWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, fieldnames, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.fieldnames = fieldnames
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writeheader(self):
        self.writer.writerow(self.fieldnames)

    def writerow(self, row):
        self.writer.writerow([row[x].encode("utf-8") for x in self.fieldnames])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


def record_referral_signup(request, user, user_created, action, third_party=False):
    referrer = None
    term = ''
    medium = ''
    campaign = ''
    referrer_from = None

    # -------------------------------------

    if 'referer' in request.COOKIES:
        referrer = request.COOKIES['referer']
    if 'referer' in request.session:
        referrer = request.session['referer']

    # -------------------------------------

    if 'term' in request.COOKIES and \
                    request.COOKIES['term'] is not None and \
                    request.COOKIES['term'] != 'None':

        term = request.COOKIES['term']

    if 'term' in request.session and \
                    request.session['term'] is not None and \
                    request.session['term'] != 'None':

        term = request.session['term']

    # -------------------------------------

    if 'medium' in request.COOKIES and \
                    request.COOKIES['medium'] is not None and \
                    request.COOKIES['medium'] != 'None':

        medium = request.COOKIES['medium']

    if 'medium' in request.session and \
                    request.session['medium'] is not None and \
                    request.session['medium'] != 'None':

        medium = request.session['medium']

    # -------------------------------------

    if 'campaign' in request.COOKIES and \
                    request.COOKIES['campaign'] is not None and \
                    request.COOKIES['campaign'] != 'None':

        campaign = request.COOKIES['campaign']

    if 'campaign' in request.session and \
                    request.session['campaign'] is not None and \
                    request.session['campaign'] != 'None':

        campaign = request.session['campaign']

    # -------------------------------------

    if third_party:
        referrer = None
    else:
        try:
            referrer = Referrer.objects.get(pk=referrer)
        except Referrer.DoesNotExist:
            return False

    # -------------------------------------

    if user_created is False and action == 'signup':
        referrer = None

    # -------------------------------------

    if UserReferral.objects.filter(user=user).exists():
        referrer_from = referrer
        referrer = UserReferral.objects.filter(user=user)[0].referrer  # Use Existing Referrer instead of new one

    # -------------------------------------

    if action in UserReferral.REFERRAL_ACTION_CHOICES_FLAT:
        try:
            user_referral, created = UserReferral.objects.get_or_create(user=user,
                                                                    referrer=referrer,
                                                                    referral_action=action,
                                                                    referrer_from=referrer_from,
                                                                    referral_medium=medium,
                                                                    referral_term=term,
                                                                    referral_campaign=campaign)
        except IntegrityError:
            return False
    else:
        try:
            user_referral, created = UserReferral.objects.get_or_create(user=user,
                                                                        referrer=referrer,
                                                                        referrer_from=referrer_from,
                                                                        referral_medium=medium,
                                                                        referral_term=term,
                                                                        referral_campaign=campaign)
        except IntegrityError:
            return False

    # -------------------------------------

    return created

# Create your views here.
from products.models import BestBuy, Product
from common.models import Rates
from django.http import Http404, HttpResponse
from django.conf import settings
from django.template.response import TemplateResponse
from products.utils import cleaned_data_to_params
from common.models import UUIDNext, NewsletterSignup, RateAlertsSignup
from dateutil.relativedelta import relativedelta
import datetime
from django.shortcuts import redirect

BESTBUYS_COUNT = getattr(settings, 'BESTBUYS_COUNT', 5)

def _make_uid():
    import uuid

    return str(uuid.uuid1())


def create_uid_next(form):
    next = UUIDNext()
    next.uuid = _make_uid()
    next.next = '/rate-tracker/'
    next.params = cleaned_data_to_params(form)
    next.save()
    return next.uuid


def _get_current_bestbuy(queryset, list, bestbuy_slug=None):
    current_bestbuy = None
    if bestbuy_slug:
        try:
            current_bestbuy = queryset.get(slug=bestbuy_slug, client_type='p')
        except BestBuy.DoesNotExist:
            raise Http404()

    elif len(list) > 0:
        current_bestbuy = list[0]

    return current_bestbuy


def _get_current_inflation_rate():
    rate = Rates.objects.latest('last_updated')
    if rate:
        return rate.inflation_rate
    return 0


def _get_overall_max_rate(rates):
    """ """
    retval = 0.0

    for rate in rates:
        aer = rate[0].get('aer', 0.0)
        if aer > retval:
            retval = aer
    return retval


def testview(request, template_file='thisismoney/registration_complete.html'):
    return TemplateResponse(request, template_file, {})


def check_opening_date_expiry(request):
    message = ""
    if request.is_ajax():
        if request.method == 'POST':
            product = Product.objects.get(pk=request.POST["productID"])

            if product.show_opening_date():
                year = int(request.POST["opYear"])

                if product.bonus_term is not None:
                    bonus_term = product.bonus_term
                else:
                    bonus_term = 0
                try:
                    openingDate = datetime.datetime(year, int(request.POST["opMonth"]), 1)
                except ValueError:
                    # Opening date was invalid, so assume it expires today
                    openingDate = datetime.datetime.today() - relativedelta(months=bonus_term)

                expiryDate = openingDate + relativedelta(months=bonus_term)

                if expiryDate < datetime.datetime.now():
                    message = True
                else:
                    message = False
            else:
                message = False

    return HttpResponse(message)


def get_new_gross_rate(request):
    message = ""
    if request.is_ajax():
        if request.method == 'POST':
            if "bonusExpired" in request.POST:
                if request.POST["bonusExpired"]:
                    message = Product.objects.get(pk=request.POST["productID"]).underlying_gross_rate
                else:
                    message = Product.objects.get(pk=request.POST["productID"]).gross_rate
    return HttpResponse(message)


def signup(request, ratealert=None):
    if request.method == "POST":
        email = request.POST['email']
        if ratealert:
            try:
                signup = RateAlertsSignup.objects.get(email=email)
            except RateAlertsSignup.DoesNotExist:
                signup = RateAlertsSignup()
        else:
            try:
                signup = NewsletterSignup.objects.get(email=email)
            except NewsletterSignup.DoesNotExist:
                signup = NewsletterSignup()

        signup.email = request.POST['email']
        signup.source = request.POST['source']

        signup.is_activated = True
        signup.save()
        return redirect('thankyou_newsletter')
    




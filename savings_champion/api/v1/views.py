# coding=utf-8
from __future__ import absolute_import
from celery.result import AsyncResult
import datetime
from django.conf import settings

from django.contrib.auth import get_user_model
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import permission_classes
from rest_framework.generics import GenericAPIView, CreateAPIView, ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser
from api.v1.models import ApiExcludedItem
from api.v1.serializers import ProviderSerializer, ProductSerializer, \
    OldProductTierSerializer, ProductTierSerializer, ProductPortfolioSerializer, \
    RatetrackerReminderSerializer, BestBuySerializer, ConciergeReferrerReportingSerializer, UserSerializer, \
    ReferrerSerializer, ProfileSerializer
from common.accounts.utils import create_stage_one_profile
from common.models import UserReferral, Referrer, Profile
from common.utils import record_referral_signup
from common.tasks import add_to_campaign_monitor, update_subscription_on_email_service
from concierge.models import AdviserQueue
from products.models import MasterProduct, ProductTier, Provider, Product, ProductPortfolio, RatetrackerReminder, \
    BestBuy, THBToolReminder

from .tasks import async_api_concierge_engine_run


def partner_permissions(self, products, request):
    if request.user.email in self.PARTNER_PERMISSIONS:
        filters = self.PARTNER_PERMISSIONS[request.user.email]['filter']
        products = products.filter(**filters)
        exclusions = self.PARTNER_PERMISSIONS[request.user.email]['exclude']
        products = products.exclude(**exclusions)
    return products


def partner_fields(self, request):
    if request.user.email in self.PARTNER_FIELDS:
        return self.PARTNER_FIELDS[request.user.email]
    return None


class ProviderPageNumberPagination(PageNumberPagination):
    page_size_query_param = 'page_size'


class ProviderList(GenericAPIView):
    """
    List of all providers, 20 per page

    Optional queries:
    pk=(int) - Primary Key
    page=(int) - Navigate to specific page

    """

    PARTNER_PERMISSIONS = {
        'api@aldermore.com': {
            'exclude': {},
            'filter': {},
        }
    }

    PARTNER_FIELDS = {
        'api@aldermore.com': (
            'id', 'title')
    }

    def get_queryset(self):
        return Provider.objects.all()

    @never_cache
    def get(self, request, format=None):
        providers = Provider.objects.all()
        if 'pk' in request.GET:
            providers = providers.filter(pk=request.GET['pk'])

        providers = partner_permissions(self, providers, request)
        fields = partner_fields(self, request)

        page_number_pagination = ProviderPageNumberPagination()
        providers = page_number_pagination.paginate_queryset(queryset=providers, request=request)

        serializer = ProviderSerializer(providers, context={'request': request}, fields=fields, many=True)
        serializer_data = serializer.data
        return page_number_pagination.get_paginated_response(serializer_data)


class ProductList(GenericAPIView):
    """
    List of all products, 20 per page

    Optional queries:
    pk=(int) - Primary Key
    account_type=(string) - Account type string (case insensitive)
    page=(int) - Navigate to specific page
    provider=(string) - Provider title string (case insensitive)
    bestbuy_type=(string) - Bestbuy type string (case insensitive)

    """

    PARTNER_PERMISSIONS = {
        'api@aldermore.com': {
            'filter': {
                'account_type__iexact': 'b',
                'status__in': ['Closed', 'Live']
            },
            'exclude': {
                'exclude_from_api_for__in': ApiExcludedItem.objects.filter(email__iexact='api@aldermore.com')
            }
        }
    }

    PARTNER_FIELDS = {
        'api@aldermore.com': (
            'id', 'title', 'last_updated', 'provider', 'status', 'bestbuy_type', 'account_type', 'available_from',
            'available_to', 'term', 'term_fixed', 'term_fixed_date', 'notice')
    }

    def get_queryset(self):
        return MasterProduct.objects.all().order_by('last_updated')

    @never_cache
    def get(self, request, format=None):
        products = MasterProduct.objects.all().order_by('last_updated')
        if 'pk' in request.GET:
            products = products.filter(pk=request.GET['pk'])
        if 'provider' in request.GET:
            provider = get_object_or_404(Provider, title__iexact=request.GET['provider'])
            products = products.filter(provider=provider)
        if 'account_type' in request.GET:
            products = products.filter(account_type__iexact=request.GET['account_type'])
        if 'bestbuy_type' in request.GET:
            products = products.filter(bestbuy_type__title__iexact=request.GET['bestbuy_type'])

        products = partner_permissions(self, products, request)
        fields = partner_fields(self, request)

        page_number_pagination = PageNumberPagination()
        products = page_number_pagination.paginate_queryset(queryset=products, request=request)

        serializer = ProductSerializer(products, context={'request': request}, fields=fields, many=True)
        serializer_data = serializer.data
        return page_number_pagination.get_paginated_response(serializer_data)


class OldProductTierList(GenericAPIView):
    """
    List of all product tiers (old style), 20 per page

    Optional queries:
    pk=(int) - Primary Key
    account_type=(string) - Account type string (case insensitive)
    page=(int) - Navigate to specific page
    provider=(string) - Provider title string (case insensitive)

    """


    PARTNER_PERMISSIONS = {
        'api@aldermore.com': {
            'filter': {
                'master_product__account_type__iexact': 'b',
                'master_product__status__in': ['Closed', 'Live']
            },
            'exclude': {
                'product__exclude_from_api_for': ApiExcludedItem.objects.filter(email__iexact='api@aldermore.com')
            }
        }
    }

    PARTNER_FIELDS = {}


    def get_queryset(self):
        return Product.objects.all().order_by('last_updated')

    @never_cache
    def get(self, request, format=None):
        product_tiers = Product.objects.all()
        if 'pk' in request.GET:
            product_tiers = product_tiers.filter(pk=request.GET['pk'])
        if 'provider' in request.GET:
            provider = get_object_or_404(Provider, title=request.GET['provider'])
            product_tiers = product_tiers.filter(provider=provider)
        if 'account_type' in request.GET:
            product_tiers = product_tiers.filter(account_type__iexact=request.GET['account_type'])

        product_tiers = partner_permissions(self, product_tiers, request)
        fields = partner_fields(self, request)

        page_number_pagination = PageNumberPagination()
        product_tiers = page_number_pagination.paginate_queryset(queryset=product_tiers, request=request)

        serializer = OldProductTierSerializer(product_tiers, context={'request': request}, fields=fields, many=True)
        serializer_data = serializer.data
        return page_number_pagination.get_paginated_response(serializer_data)


class ProductTierList(GenericAPIView):
    """
    List of all products, 20 per page

    Optional queries:
    pk=(uuid) - Primary Key
    account_type=(string) - Account type string (case insensitive)
    page=(int) - Navigate to specific page
    provider=(string) - Provider title string (case insensitive)
    product=(string) - Primary Key of a product
    bestbuy_type=(string) - Bestbuy type string (case insensitive)

    """

    PARTNER_PERMISSIONS = {
        'api@aldermore.com': {
            'filter': {
                'product__account_type__iexact': 'b',
                'product__status__in': ['Closed', 'Live']
            },
            'exclude': {
                'product__exclude_from_api_for': ApiExcludedItem.objects.filter(email__iexact='api@aldermore.com')
            }
        }
    }

    PARTNER_FIELDS = {
        'api@aldermore.com': (
            'id', 'title', 'last_updated', 'sc_code', 'product', 'publish_after', 'account_type', 'provider', 'minimum', 'maximum',
            'aer', 'gross_rate', 'monthly_gross', 'bestbuy_type', 'bonus_amount', 'underlying_gross_rate', 'notice', 'status', 'available_until',
            'bonus_term', 'bonus_end_date')
    }

    def get_queryset(self):
        return ProductTier.objects.all().order_by('last_updated')

    @never_cache
    def get(self, request, format=None):
        product_tiers = ProductTier.objects.all().order_by('last_updated')
        if 'pk' in request.GET:
            product_tiers = product_tiers.filter(pk=request.GET['pk'])
        if 'provider' in request.GET:
            provider = get_object_or_404(Provider, title=request.GET['provider'])
            product_tiers = product_tiers.filter(provider=provider)
        if 'account_type' in request.GET:
            product_tiers = product_tiers.filter(account_type__iexact=request.GET['account_type'])
        if 'product' in request.GET:
            product_tiers = product_tiers.filter(product__pk=request.GET['product'])
        if 'bestbuy_type' in request.GET:
            product_tiers = product_tiers.filter(bestbuy_type__title__iexact=request.GET['bestbuy_type'])

        product_tiers = partner_permissions(self, product_tiers, request)
        fields = partner_fields(self, request)

        page_number_pagination = PageNumberPagination()
        product_tiers = page_number_pagination.paginate_queryset(queryset=product_tiers, request=request)

        serializer = ProductTierSerializer(product_tiers, context={'request': request}, fields=fields, many=True)
        serializer_data = serializer.data
        return page_number_pagination.get_paginated_response(serializer_data)


@permission_classes((IsAdminUser, ))
class ProductPortfolioList(GenericAPIView):
    """
    List of a users reported accounts, 20 per page

    Required queries:
    user_email=(string) - Filter for user with specific email

    Optional queries:
    pk=(int) - Primary Key
    """

    def get_queryset(self):
        return ProductPortfolio.objects.all()

    @never_cache
    def get(self, request, format=None):
        if 'pk' in request.GET or 'user_email' in request.GET:
            product_portfolio = ProductPortfolio.objects.all()
            if 'pk' in request.GET:
                product_portfolio = product_portfolio.filter(pk=request.GET['pk'])
            if 'user_email' in request.GET:
                user = get_object_or_404(get_user_model(), email=request.GET.get('user_email'))
                product_portfolio = product_portfolio.filter(user=user)
        else:
            product_portfolio = ProductPortfolio.objects.none()

        page_number_pagination = PageNumberPagination()
        product_portfolio = page_number_pagination.paginate_queryset(queryset=product_portfolio, request=request)

        serializer = ProductPortfolioSerializer(product_portfolio, context={'request': request}, many=True)
        serializer_data = serializer.data
        return page_number_pagination.get_paginated_response(serializer_data)


@permission_classes((IsAdminUser, ))
class RatetrackerReminderList(GenericAPIView):
    """
    List of a users reported accounts, 20 per page

    Required queries:
    user_email=(string) - Filter for user with specific email

    Optional queries:
    pk=(int) - Primary Key
    """

    def get_queryset(self):
        return RatetrackerReminder.objects.all()

    @never_cache
    def get(self, request, format=None):
        if 'pk' in request.GET or 'user_email' in request.GET:
            ratetracker_reminder = RatetrackerReminder.objects.all()
            if 'pk' in request.GET:
                ratetracker_reminder = ratetracker_reminder.filter(pk=request.GET['pk'])
            if 'user_email' in request.GET:
                user = get_object_or_404(get_user_model(), email=request.GET.get('user_email'))
                ratetracker_reminder = ratetracker_reminder.filter(user=user)
        else:
            ratetracker_reminder = ProductPortfolio.objects.none()

        page_number_pagination = PageNumberPagination()
        ratetracker_reminder = page_number_pagination.paginate_queryset(queryset=ratetracker_reminder, request=request)

        serializer = RatetrackerReminderSerializer(ratetracker_reminder, context={'request': request}, many=True)
        serializer_data = serializer.data
        return page_number_pagination.get_paginated_response(serializer_data)


class BestBuyList(GenericAPIView):

    def get_queryset(self):
        return BestBuy.objects.all()

    @never_cache
    def get(self, request, format=None):
        best_buys = BestBuy.objects.all()

        page_number_pagination = PageNumberPagination()
        best_buys = page_number_pagination.paginate_queryset(queryset=best_buys, request=request)

        serializer = BestBuySerializer(best_buys, context={'request': request}, many=True)
        serializer_data = serializer.data
        return page_number_pagination.get_paginated_response(serializer_data)

class ConciergeEngineRun(GenericAPIView):


    @never_cache
    def get(self, request, format=None):
        client_email = request.GET['client_email']
        async_id = async_api_concierge_engine_run.delay(email=client_email)
        return JsonResponse({'results': {'task_id': async_id.id}})


class ConciergeEngineResult(GenericAPIView):

    @never_cache
    def get(self, request, format=None):
        async_id = request.GET['async_id']
        results = AsyncResult(id=async_id)
        return JsonResponse({
            'task_id': results.id,
            'task_status': results.status,
            'results': results.result
        })


class UserList(ListAPIView):

    User = get_user_model()
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminUser,)

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `email` query parameter in the URL.
        """

        User = get_user_model()
        queryset = User.objects.all()
        email = self.request.query_params.get('email', None)
        if email is not None:
            queryset = queryset.filter(email=email)
        return queryset


class UserCreation(CreateAPIView):
    """
        todo: Hook into user referral system.
    """
    User = get_user_model()
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminUser,)


class ConciergeReferrerReporting(CreateAPIView):

    queryset = UserReferral.objects.all()
    serializer_class = ConciergeReferrerReportingSerializer
    permission_classes = (IsAdminUser, )


class ReferrerList(ListAPIView):

    queryset = Referrer.objects.all()
    serializer_class = ReferrerSerializer
    permission_classes = (IsAdminUser,)

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `email` query parameter in the URL.
        """

        queryset = Referrer.objects.all()
        name = self.request.query_params.get('name', None)
        if name is not None:
            queryset = queryset.filter(name=name)
        return queryset


class ProfileList(ListAPIView):

    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (IsAdminUser,)


class THBToolCallback(GenericAPIView):
    serializer_class = THBToolReminder

    def get_queryset(self):
        return self.serializer_class().objects.none()

    @csrf_exempt
    def post(self, request, format=None):
        data = request.data
        thb_reminder = None

        source = data.get('source', None)

        user, user_created = create_stage_one_profile(request=request, email=data['email'],
                                                      source='thb_tool', send_activation=False,
                                                      login_user=False)

        record_referral_signup(request=request, user=user, user_created=user_created, action='signup')

        if data['remind_me']:
            # Client asked to be reminded of the FSCS change to £75,000
            update_subscription_on_email_service.delay(data['email'], interest_group=u'FSCS Protection Drop Reminder')
            record_referral_signup(request=request, user=user, user_created=user_created, action='thb_remind_me_fscs')

        if data['set_reminder'] == 'true':
            deposit_date = datetime.date(year=int(data['deposit_year']),
                                         month=int(data['deposit_month']),
                                         day=int(data['deposit_day']))
            thb_reminder = THBToolReminder.add_reminder(
                name=data['name'],
                email=data['email'],
                phone_number=data['phone_number'],
                source=source,
                deposit_date=deposit_date,
                callback=(data['book_callback'] == 'true')
            )
            record_referral_signup(request=request, user=user, user_created=user_created, action='thb_alert_me_fscs')

        if data['book_callback'] == 'true':
            AdviserQueue.add_to_queue(email=data['email'],
                                      first_name=data['name'],
                                      last_name='.',
                                      lead_source='THB Tool',
                                      telephone_number=data['phone_number'])
            if thb_reminder is not None:
                thb_reminder.scheduled_callback = True
                thb_reminder.save()
            record_referral_signup(request=request, user=user, user_created=user_created, action='thb_book_callback')

        return JsonResponse({
            'status': 'ok'
        })



from __future__ import absolute_import
__author__ = 'josh'
from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from .views import ProductList, ProductTierList, OldProductTierList, ProviderList, ProductPortfolioList, \
    RatetrackerReminderList, BestBuyList, ConciergeEngineRun, ConciergeEngineResult, UserList, UserCreation, \
    ConciergeReferrerReporting, ReferrerList, ProfileList, THBToolCallback

uuid_re = r'[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}'

urlpatterns = [

    url(r'^providers/$', ProviderList.as_view()),

    url(r'^products/$', ProductList.as_view()),

    url(r'^old_product_tiers/$', OldProductTierList.as_view()),

    url(r'^product_tiers/$', ProductTierList.as_view()),

    url(r'^product_portfolios/$', ProductPortfolioList.as_view()),

    url(r'^ratetracker_reminders/$', RatetrackerReminderList.as_view()),

    url(r'^bestbuy_types/$', BestBuyList.as_view()),

    url(r'^concierge/engine/run/$', ConciergeEngineRun.as_view(), name='api_concierge_engine_run'),

    url(r'^concierge/engine/results/$', ConciergeEngineResult.as_view(), name='api_concierge_engine_result'),


    url(r'^users/$', UserList.as_view(), name='api_user_list'),
    url(r'^users/create/$', UserCreation.as_view(), name='api_user_create'),
    url(r'^users/referral/add/$', ConciergeReferrerReporting.as_view(), name='api_user_referral_create'),

    url(r'^profile/$', ProfileList.as_view(), name='api_profile_list'),

    url(r'^referrers/$', ReferrerList.as_view(), name='api_referrer_list'),

    url(r'^thb_tool_callback/$', THBToolCallback.as_view(), name='api_thb_tool_callback')

]

urlpatterns = format_suffix_patterns(urlpatterns)
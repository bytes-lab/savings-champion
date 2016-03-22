from django.conf.urls import *
from django.conf.urls.static import static
from django.conf import settings

uuid_re = '[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}'

urlpatterns = patterns('administration.views',
# ------
    url(r'^$', 'index', name="admininstrationindex"),
    url(r'changesccode/$', 'change_sccode_initial', name="sccodeinitial"),
    url(r'changesccode/success/$', 'change_sccode_process', name="sccodeprocess"),
    url(r'memcached/status/$', 'memcached_status', name="memcached_status"),
    url(r'cache/clear/$', 'clear_cache', name="clear_cache"),
    url(r'comment/approve/$', 'approve_comment', name="approve_comment"),
    url(r'customer/add/$', 'add_new_product_for_customer', name="add_customer_product"),
    url(r'customer/add/success/$', 'add_product_for_customer_logic', name="add_customer_product_logic"),
    url(r'customer/view/$', 'view_customer_portfolio', name="view_customer_portfolio"),
    url(r'customer/change/$', 'change_user_portfolios', name="change_customer_portfolio"),
    url(r'customer/change/updated/$', 'change_user_portfolios_logic', name="change_customer_portfolio_logic"),
    url(r'user/status/$', 'check_user_status', name="view_user_status"),
    url(r'ip/list/$', 'get_ip_address_count', name="list_ips"),
    url(r'ip/list/emails/$', 'get_ip_address_emails', name="list_ip_emails"),
    url(r'bestbuys/add/$', 'manual_bestbuy_add', name="manual_bestbuy_add"),
    url(r'fscs/test/$', 'fscs_test', name="fscs_test"),
    url(r'activation/resend/$', 'resend_user_activation', name="resend_activation_admin"),
    url(r'user/email/$', 'change_user_email', name="change_user_email"),
    url(r'concierge/create/$', 'create_concierge_client', name="create_concierge_client"),
    url(r'concierge/remove/$', 'remove_concierge_client', name="remove_concierge_client"),
    url(r'user/password/$', 'change_user_password', name="change_user_password"),
    url(r'user/unsubscribe/$', 'unsubscribe_user', name="unsubscribe_user"),
    url(r'user/delete/$', 'remove_user', name="delete_user"),
    url(r'user/sync/$', 'force_sync_user', name="sync_user"),
    url(r'users/breakdown/$', 'user_breakdown', name="user_breakdown"),
    url(r'users/breakdown/ajax/$', 'user_breakdown_ajax', name="user_breakdown_ajax"),
    url(r'users/referrals/$', 'referrer_reporting', name='referral_reporting'),
    url(r'users/referrals/paid/(?P<uuid>' + uuid_re + ')/$', 'referrer_reporting_paid', name='referral_reporting_paid'),
    url(r'providers/logos/$', 'provider_logos', name='provider_logos'),
    url(r'products/update/$', 'update_products_from_salesforce', name='update_products_from_salesforce'),
    url(r'user/portfolio/check/$', 'check_client_portfolios_for_issues_view', name='check_client_portfolios_for_issues'),
    )

from django.conf.urls import *
from products.ajax import product_handler, provider_handler

TABLE_TEMPLATE_FILE = 'table_template_file'
CALCULATIONS_TEMPLATE_FILE = 'calculations_template_file'
urlpatterns = patterns('',
                       # ------
                       url(r'^json/bestbuys/$', 'products.ajax.bestbuys_handler.bestbuy', name='bestbuys_json'),
                       #
                       url(r'^json/providers/$', provider_handler.ProviderList.as_view(), name='providers_json'),
                       url(r'^json/products/$', product_handler.ProductList.as_view(), name='products_json'),
                       url(r'^ajax/checkopening/$', 'products.views.check_opening_date_exists', name="checkOpenDate"),
                       url(r'^ajax/updateportfolio/$', 'products.ajax.portfolio_edit.update_portfolio_balance',
                           name='updatePortfolio'),
                       url(r'^ajax/updatereminder/$', 'products.ajax.portfolio_edit.update_reminder_balance',
                           name='updateReminder'),
                       url(r'^ajax/deleteportfolio/$', 'products.ajax.portfolio_delete.delete_portfolio',
                           name='deletePortfolio'),
                       url(r'^ajax/addopening/$', 'products.ajax.portfolio_edit.add_opening', name='add_opening_date'),
                       url(r'^ajax/retrievepersonalproducts/$', 'products.ajax.healthcheck.retrieve_personal_products',
                           name='retrieve_products'),
                       url(r'^ajax/retrievefixedchoices/$', 'products.ajax.healthcheck.retrieve_provider_fixed_types',
                           name='retrieve_fixed_choices'),
                       url(r'^ajax/loadportfolio/$', 'products.ajax.load_portfolio.load_portfolio',
                           name='load_portfolio'),
                       url(r'^ajax/emailinstructions/$', 'products.ajax.email_instructions.email_instructions',
                           name='email_instructions'),
                       #-------
                       url(r'^compare/$', 'products.views.compare_top_accounts', name="compare_table"),
                       url(r'^compare/(?P<portfolio_id>\d+)/$', 'products.views.compare_top_accounts',
                           name="compare_table_ratetracker"),
                       url(r'^all/$', 'products.views.view_all_bestbuys', name="view_all_bestbuys"),
                       url(r'^free-genuine-best-buy-delivery-service/$', 'products.views.reccuring_bestbuy_emails',
                           name="reccuring_bestbuy_emails"),
                       url(r'^business-best-buy-service/$', 'products.views.reccuring_business_bestbuy_emails',
                           name="reccuring_business_bestbuy_emails"),

                       url(r'^personal/(?P<bestbuy_slug>[\w\-]+)/$', 'products.views.personal_top_accounts',
                           name="personal_table"),

                       url(r'^business/(?P<bestbuy_slug>[\w\-]+)/$', 'products.views.business_top_accounts',
                           name="business_table"),

                       #old urls for redirection
                       url(r'^tables/(?P<bestbuy_slug>[\w\-]+)/$', 'redirect.old_bestbuy_table_redirect',
                           name='view_bestbuy_table_old'),
                       url(r'^tables/$', 'redirect.old_bestbuy_table_index_redirect', name='view_bestbuy_tables_old'),
                       url(r'^(?P<bestbuy_slug>[\w\-]+)/$', 'redirect.old_bestbuy_table_index_redirect',
                           name='view_bestbuy_old'),
                       #endold redirects

                       url(r'^moneytothemasses/personal/(?P<bestbuy_slug>[\w\-]+)/$',
                           'products.external_bestbuys.moneytothemasses_personal_top_accounts',
                           name="moneytothemasses_personal_top_accounts"),

                       url(r'^mymoneydiva/personal/(?P<bestbuy_slug>[\w\-]+)/$',
                           'products.external_bestbuys.mymoneydiva_personal_top_accounts',
                           name="mymoneydiva_personal_top_accounts"),

                       url(r'^mymoneydiva/business/(?P<bestbuy_slug>[\w\-]+)/$',
                           'products.external_bestbuys.mymoneydiva_business_top_accounts',
                           name="mymoneydiva_business_top_accounts"),

                       url(r'^$', 'products.views.top_personal_accounts_index', name="top_accounts"),
                       url(r'^business/$', 'products.views.top_business_accounts_index', name="business_top_accounts"),
                       url(r'^outbound/(?P<product_id>\d+)/$', 'products.views.outbound_clickthrough', name='outbound_clickthrough'),

                       url(r'^ajax/portfolio_threshold/$', 'products.views.ratetracker_threshold_amount', name='ratetracker_threshold'),

                       url(r'^ajax/best_buy_table_callback/$', 'products.views.best_buy_table_callback', name='best_buy_table_callback'),
)

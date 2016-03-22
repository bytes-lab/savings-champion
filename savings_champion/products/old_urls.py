from django.conf.urls import *
from products import forms
from piston.resource import Resource
from products.ajax import ProviderHandler
from products.ajax import ProductHandler
from products.ajax import BestBuysHandler

provider_handler = Resource(ProviderHandler)
product_handler = Resource(ProductHandler)
bestbuys_handler = Resource(BestBuysHandler)


TABLE_TEMPLATE_FILE = 'table_template_file'
CALCULATIONS_TEMPLATE_FILE = 'calculations_template_file'
urlpatterns = patterns('',
# ------
    url(r'^json/bestbuys/$', bestbuys_handler, name = 'bestbuys_json'),
    
    url(r'^json/providers/$', provider_handler, name = 'providers_json'),
    url(r'^json/products/$', product_handler, name = 'products_json'),
    url(r'^check_opening/$','products.views.check_opening_date_exists', name="checkOpenDate"),
    url(r'^ajax/updateportfolio/$', 'products.ajax.portfolio_edit.update_portfolio_balance', name='updatePortfolio'),
    url(r'^ajax/updatereminder/$', 'products.ajax.portfolio_edit.update_reminder_balance', name='updateReminder'),
#-------
    url(r'^tables/(?P<bestbuy_slug>easy-access)/$', 
        'products.views.bestbuys', 
        {
         TABLE_TEMPLATE_FILE :'products/tables/easy_access_table.html',
         'form':forms.GenericBestBuyForm,
         },
        name = 'view_easy_access_table'),
    
    url(r'^tables/(?P<bestbuy_slug>notice-accounts)/$', 
        'products.views.bestbuys', 
        {
         TABLE_TEMPLATE_FILE :'products/tables/notice_accounts_table.html',
         'form':forms.GenericBestBuyForm,
         },
        name = 'view_notice_accounts_table'),
    
    url(r'^tables/(?P<bestbuy_slug>fixed-rate-bond)/$', 
        'products.views.bestbuys', 
        {
         TABLE_TEMPLATE_FILE :'products/tables/fixed_rate_bonds_table.html',
         'form': forms.FixedRateBondsBestBuysForm,
         },
        name = 'view_fixed_bonds_table'),
    
    url(r'^tables/(?P<bestbuy_slug>variable-rate-isa)/$', 
        'products.views.bestbuys', 
        {
         TABLE_TEMPLATE_FILE :'products/tables/variable_cash_isa_table.html',
         'form': forms.VariableCashISABestBuyForm,
         },
        name = 'view_variable_cash_isa_table'),
    
    url(r'^tables/(?P<bestbuy_slug>fixed-rate-isa)/$', 
        'products.views.bestbuys', 
        {
         TABLE_TEMPLATE_FILE :'products/tables/fixed_rate_cash_isas_table.html',
         'form': forms.FixedRateCashISABestBuyForm,
         },
        name = 'view_fixed_rate_cash_isas_table'),

    url(r'^tables/(?P<bestbuy_slug>monthly-income)/$', 
        'products.views.bestbuys', 
        {
         TABLE_TEMPLATE_FILE :'products/tables/monthly_income_accounts_table.html',
         CALCULATIONS_TEMPLATE_FILE :'products/tables/monthly_calculations_table.html',
         'form':forms.MonthlyIncomeAccountForm,
         'is_monthly':True,
         },
        name = 'view_monthly_income_accounts_table'),
    
    url(r'^tables/(?P<bestbuy_slug>childrens-accounts)/$', 
        'products.views.bestbuys', 
        {
         TABLE_TEMPLATE_FILE :'products/tables/childrens_table.html',
         'form':forms.ChildrensAccountForm,
         },
        name = 'view_childrens_savings_table'),
    
    url(r'^tables/(?P<bestbuy_slug>over-50s)/$', 
        'products.views.bestbuys', 
        {
         TABLE_TEMPLATE_FILE :'products/tables/over_50s_table.html',
         'form':forms.GenericBestBuyForm,
         },
        name = 'view_over_50s_table'),
    
    url(r'^tables/(?P<bestbuy_slug>regular-savings)/$', 
        'products.views.bestbuys', 
        {
         TABLE_TEMPLATE_FILE :'products/tables/regular_savings_table.html',
         'form':forms.RegularSavingsAccountForm,
         },
        name = 'view_regular_savings_table'),                 
    url(r'^tables/(?P<bestbuy_slug>childrens)/$', 
        'products.views.bestbuys', 
        {
         TABLE_TEMPLATE_FILE :'products/tables/childrens_table.html',
        'form':forms.ChildrensAccountForm,
         },
        name = 'view_regular_savings_table'), 

    url(r'^tables/(?P<bestbuy_slug>[\w\-]+)/$', 
        'products.views.bestbuys', 
        name = 'view_bestbuy_table'),
    
    url(r'^tables/$', 
        'products.views.bestbuys', 
        name = 'view_bestbuy_tables'),
    url(r'^(?P<bestbuy_slug>[\w\-]+)/$', 
        'products.views.bestbuys_compare', 
        name = 'view_bestbuy'),
                       
    url(r'^$', 'products.views.bestbuys_compare', name="view_bestbuys"),

)

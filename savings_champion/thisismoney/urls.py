from django.conf.urls import *

from products.forms import ProductReminderForm
from django.views.generic import TemplateView

urlpatterns = patterns('',
    url(r'^ajax/products/$', 'thisismoney.ajax.omrcajax.retrieve_products', name = 'tim_products_json'),
    url(r'^ajax/get_bestbuys/$', 'thisismoney.ajax.omrcajax.get_bestbuys', name='tim_get_bestbuys'),
    url(r'^ajax/check_expiry/$','thisismoney.views.check_opening_date_expiry', name="checkOpenExpiry"),
    url(r'^ajax/get_new_rate/$','thisismoney.views.get_new_gross_rate', name="getNewGrossRate"),
    url(r'^ajax/check_email/$','thisismoney.ajax.check_email.check_duplicate_email', name="checkDuplicateEmail"),
    url(r'^ajax/concierge_html/$','thisismoney.ajax.largewidget.concierge', name="ajax_concierge"),
    url(r'^ajax/rate_tracker_html/$','thisismoney.ajax.largewidget.rate_tracker', name="ajax_rate_tracker"),
    url(r'^ajax/rate_alerts_html/$','thisismoney.ajax.largewidget.rate_alerts', name="ajax_rate_alerts"),

    # -----

    url(r'^rate-tracker/1-minute-rate-check/ocomplete/$', 'thisismoney.tracker.views.rate_check_complete', {'form_class' : ProductReminderForm }, name="timopening_date_rate_check_complete"),
    url(r'^rate-tracker/1-minute-rate-check/complete/$', 'thisismoney.tracker.views.rate_check_complete', name="timrate_check_complete"),
    url(r'^rate-tracker/1-minute-rate-check/widget/$', 'thisismoney.tracker.views.tracker', name="timrate_check"),
    url(r'^rate-tracker/1-minute-rate-check/largewidget/$', 'thisismoney.tracker.views.tracker', {'template_file' : 'thisismoney/ratetracker/largewizard.html'}, name="largetimrate_check"),
   
    
    (r'^best-buys/', include('products.urls')),
    url(r'^accounts/logout/$', 'common.views.sc_logout', name="sc_logout"),
    url(r'^widgetsignup/$', 'thisismoney.views.signup', name="timsubssignup"),
    url(r'^widgetsignup/ra/$', 'thisismoney.views.signup', {'ratealert' : True}, name="timsubssignupra"),
    
    url(r'^thisismoney/hosted/timiframeheader/$',  TemplateView.as_view(template_name="thisismoney/timiframeheader.html"), name = 'timiframeheader'),
    url(r'^thisismoney/hosted/timiframefooter/$', TemplateView.as_view(template_name="thisismoney/timiframefooter.html"), name = 'timiframefooter'),
    url(r'^accounts/activate/complete/$', 'common.accounts.views.finish_activation',
       name='activation_complete'),
    url(r'^accounts/activate/resend/$', 'common.accounts.views.resend_activation', name='resend_activation'),
    url(r'^accounts/activate/(?P<activation_key>\w+)/$','common.accounts.views.tim_activate', name='tim_registration_activate'),
    url(r'^accounts/timregister/fixed/$','common.accounts.views.tim_fixed_register', name='tim_fixed_register'),
    url(r'^', include('urls')),
    
    
    
    
)


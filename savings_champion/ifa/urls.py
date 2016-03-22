from django.conf.urls import *


urlpatterns = patterns('',
    url(r'^$', 'ifa.views.ifa_landing', name='ifa_landing'),
    url(r'^tpo/$', 'ifa.views.tpo_signup', name='tpo_signup'),
    url(r'^tpo/(?P<balance>\d+)/$', 'ifa.views.tpo_signup', name='tpo_signup'),
    url(r'^tpo/thankyou/$', 'ifa.views.tpo_thankyou', name='tpo_thankyou'),
    url(r'^tpo/fact-find/$', 'ifa.views.tpo_fact_find', name='tpo_fact_find'),
    url(r'^tpo/fact-find/thank-you/$', 'ifa.views.tpo_fact_find_thankyou', name='tpo_fact_find_thankyou'),


    url(r'^beckford_james/$', 'ifa.views.bj_signup', name='bj_signup'),
    url(r'^beckford_james/thankyou/$', 'ifa.views.bj_thankyou', name='bj_thankyou'),
)

from django.conf.urls import *

urlpatterns = patterns('',
                       url(r'^$', 'rate_tracker.views.rate_tracker_portfolio', name="rate_tracker_portfolio"),
)

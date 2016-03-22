from django.conf.urls import *
from products.ajax import TrackerHandler
from piston.resource import Resource

tracker_handler = Resource(TrackerHandler)

urlpatterns = patterns('',
    url(r'^json/track$', tracker_handler, name = 'track_product'),            
    url(r'^1-minute-rate-check$', 'products.tracker.views.tracker', name="rate_check"),
    url(r'^$', 'products.tracker.views.portfolio', name="rate_tracker"),    
    
)

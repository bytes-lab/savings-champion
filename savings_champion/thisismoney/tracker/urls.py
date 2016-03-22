from django.conf.urls import *
from piston.resource import Resource
from products.ajax import TrackerHandler

tracker_handler = Resource(TrackerHandler)

urlpatterns = patterns('',
    url(r'^json/track$', tracker_handler, name='track_product'),
    url(r'^tim1-minute-rate-check$', 'thisismoney.tracker.views.tracker', name="timrate_check"),
    url(r'^$', 'thisismoney.tracker.views.portfolio', name="timrate_tracker"),    
    
)

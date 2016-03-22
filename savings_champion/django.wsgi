import os, sys

try:
    import newrelic.agent
    newrelic.agent.initialize('/etc/newrelic/newrelic.ini', 'production')
except:
    pass

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
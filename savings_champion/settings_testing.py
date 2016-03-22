import os
from settings_base import *

# Condensed settings

ALLOWED_HOSTS.extend(
    ['127.0.0.1',
     'localhost',
     ]
)

DEBUG = True
TEMPLATE_DEBUG = DEBUG

sentry_dsn = os.environ.get('sentry_dsn',
                            'https://c940db8257224401b0be10c7cacf74e0:3b349d3f248b48fdb23c11c40bc0b6d5@sentry.savingschampion.co.uk/5')
protocol, url_first, url_end = sentry_dsn.rsplit(':')
_, url_last = sentry_dsn.split('@')

WEB_DSN = "{protocol}:{first}@{last}".format(protocol=protocol, first=url_first, last=url_last)

#INSTALLED_APPS += ('debug_toolbar', 'debug_toolbar_line_profiler')

#DEBUG_TOOLBAR_PANELS = (
#    'debug_toolbar.panels.versions.VersionsPanel',
#    'debug_toolbar.panels.timer.TimerPanel',
#    'debug_toolbar.panels.settings.SettingsPanel',
#    'debug_toolbar.panels.headers.HeadersPanel',
#    'debug_toolbar.panels.request.RequestPanel',
#    'debug_toolbar.panels.sql.SQLPanel',
#    'debug_toolbar.panels.templates.TemplatesPanel',
#    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
#    'debug_toolbar.panels.cache.CachePanel',
#    'debug_toolbar.panels.signals.SignalsPanel',
#    'debug_toolbar.panels.logging.LoggingPanel',
#    'debug_toolbar.panels.redirects.RedirectsPanel',
#    'debug_toolbar_line_profiler.panel.ProfilingPanel',
#)



HTTPS_SUPPORT = False

SALESFORCE_ENTERPRISE_WSDL = 'file://%s/common/enterprise_live.wsdl' % PROJECT_DIR

#TEST_RUNNER = 'django_behave.runner.DjangoBehaveTestSuiteRunner'

#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

db_engine = os.environ.get('database_engine', 'django.db.backends.postgresql_psycopg2')
db_name = os.environ.get('database_name', 'savings_champion')
db_user = os.environ.get('database_user', 'savings_champion')
db_password = os.environ.get('database_password', '4gPOAKHyRQsmmqSuW5bf9U0X4gvDkd')
db_host = os.environ.get('database_host', 'savings-champion.ccy1i4hmxgnp.eu-west-1.rds.amazonaws.com')
db_port = os.environ.get('database_port', '')

DATABASES = {
    'default': {
        'ENGINE': db_engine,
        # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': db_name,  # Or path to database file if using sqlite3.
        'USER': db_user,  # Not used with sqlite3.
        'PASSWORD': db_password,  # Not used with sqlite3.
        'HOST': db_host,  # Set to empty string for localhost. Not used with sqlite3.
        'PORT': db_port,  # Set to empty string for default. Not used with sqlite3.
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

CELERY_ALWAYS_EAGER = True

MEDIA_URL = '/media/'
STATIC_URL = '/static/'
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
COLLECTFAST_ENABLED = False

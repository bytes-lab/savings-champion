# Django settings for bob project.
from boto.s3.connection import VHostCallingFormat, OrdinaryCallingFormat, SubdomainCallingFormat
from kombu import Queue, Exchange
import markdown
import platform

DEBUG = False
TEMPLATE_DEBUG = DEBUG

import os

ALLOWED_HOSTS = ['.advicechampion.co.uk',
                 '.advicechampion.com',
                 '.annaandsue.co.uk',
                 '.annaandsue.com',
                 '.businessratetracker.co.uk',
                 '.businessratetracker.com',
                 '.cashgurus.co.uk',
                 '.charityratetracker.com',
                 '.charityratetracker.co.uk',
                 '.depositcheck.co.uk',
                 '.deposittracker.com',
                 '.expatratetracker.co.uk',
                 '.expatratetracker.com',
                 '.investmentchampion.co.uk',
                 '.isaadvice.com',
                 '.isachampion.co.uk',
                 '.isachampion.com',
                 '.isatracker.com',
                 '.isatracker.co.uk',
                 '.investmenttracker.co',
                 '.nobiasadvice.co',
                 '.minutesaving.co.uk',
                 '.minutesaving.com',
                 '.minutesavings.co.uk',
                 '.pensionschampion.co.uk',
                 '.pensionschampion.com',
                 '.pensionsratetracker.co.uk',
                 '.pensionsratetracker.com',
                 '.rateguru.co.uk',
                 '.rate-tracker.co.uk',
                 '.savingscheck.co.uk',
                 '.savingschannel.co.uk',
                 '.savingschampion.co.uk',
                 '.savingschampions.co.uk',
                 '.savingschampions.com',
                 '.savingsgurus.co.uk',
                 '.savingsgurus.com',
                 '.savingssolutions.co.uk',
                 '.savingsportal.co.uk',
                 '.sixtysecondsaving.co.uk',
                 '.sixtysecondsaving.com',
                 '.sixtysecondsavings.co.uk',
                 '5.9.87.167',
                 '.wealthtracker.co',
                 '.savingschampiontv.co.uk',
                 '.pensionfundtracker.co',
                 '.ratechampion.co.uk',
                 '.pensionfundtracker.co.uk',
                 '.nobiasadvice.co',
                 platform.node()
                 ]

os.environ['HTTPS'] = "off"

PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))

ADMINS = (
    ('Josh Harwood', 'josh@savingschampion.co.uk'),
)

DEFAULT_FROM_EMAIL = 'savings.champion@savingschampion.co.uk'

CSV_EXPORT_RECIPIENTS = ['info@savingschampion.co.uk']
SAVINGS_CHAMPION_EMAIL_FILTERS = ['josh@savingschampion.co.uk', 'annette@savingschampion.co.uk',
                                  'annettemercer2@gmail.com', 'annette@footdown.com']


SALESFORCE_CREATE_USERS_PATH = os.path.join(PROJECT_DIR, 'sfusers_%s.txt')
USER_EXPORT_PATH = os.path.join(PROJECT_DIR, 'userdetails_%s.csv')
SALESFORCE_SYNC_ALERTS_PATH = os.path.join(PROJECT_DIR, 'sfalerts_%s.txt')
SALESFORCE_RATETRACKER_ACCOUNTS_PATH = os.path.join(PROJECT_DIR, 'sfaccounts_%s.txt')
DUPLICATE_EMAILS_PATH = os.path.join(PROJECT_DIR, 'duplicate_%s.csv')
REMINDERS_CSV_PATH = os.path.join(PROJECT_DIR, 'reminders_%s.csv')
PORTFOLIOS_CSV_PATH = os.path.join(PROJECT_DIR, 'portfolios_%s.csv')
ALERTS_CSV_PATH = os.path.join(PROJECT_DIR, 'alerts_%s.csv')
CAMPAIGNS_CSV_PATH = os.path.join(PROJECT_DIR, 'rate_concierge_%s.csv')
ACTIVE_USERS_NO_RATES_OR_REMINDERS_CSV_PATH = os.path.join(PROJECT_DIR, 'not_tracking_%s.csv')
NON_ACTIVE_USERS_CSV_PATH = os.path.join(PROJECT_DIR, 'inactive_%s.csv')

MANAGERS = ADMINS

# Campaign Monitor Keys,
# These are the live values, if you wish to test with any other list, please set up a 
# a free test account 
CREATESEND_API_KEY = 'bba2918a03729d7ec7b8c37121200adb'
# For Newsletters
CREATESEND_LIST_ID = '4e9c0b23086f7fde10ca39004aec7df9'
# For Rate Alerts
CREATESEND_RATE_ALERTS_LIST_ID = '99e6a404f3432c72a3491f766f7ed779'

SENDY_API_KEY = ''

SENDY_ALL_USER_LIST = 'FoOEXEdhRivMpagwNOYwEg'
SENDY_PERSONAL_AUTO_RESPONDER = 'tPHb5bqUuVBcdMaKLXpEAA'
SENDY_BUSINESS_AUTO_RESPONDER = 'ndfze8928JPtrgdtE763763YDyKA'
SENDY_CHARITY_AUTO_RESPONDER = '1763PRwdCJgdBZfFm1763kRWmA'
SENDY_NEWSLETTER_ID = 'xR5iT8WpdXA3L2NEJ50vkQ'
SENDY_RATE_ALERT_ID = 'FUgrjN22IZ8olReAHKVuPQ'
SENDY_FIFTY_POUND_CHALLENGE_ID = 'Pqb0AHkJiOW73KBXbnT5fQ'
SENDY_IHT_GUIDE_ID = '9yyEGa6vjFPpYA7m892eZLVA'
SENDY_INVESTEC_PRODUCT_ID = '5c7yKHbkUvWJGnf763Vk0cgQ'
SENDY_NISA_GUIDE_ID = 'nxUiQeTz763imlUDEZ763338923A'
SENDY_PETITION_ID = 'ZlsCqRMZTxyLFDPtF0TMhg'
SENDY_PRODUCT_QUESTIONAIRE_ID = 'A0oWLeRQuzc9DdNrvzMMuA'
SENDY_SAVINGS_PRIORITY_LIST_ID = 'aXXiF6L3XikcF6GoiiRJ4w'
SENDY_SEVEN_PITFALLS_ID = 'BGooGRxiZux8AGiBSXU7vw'
SENDY_BIGGEST_MISTAKE_ID = 'HigxbsZfaH5dpNDPOeZlLA'
SENDY_VANQUIS_PRODUCT_ID = 'Czm8920YpBq5LUtXHONid6xQ'
SENDY_DAILY_BESTBUY_TABLES_ID = 'VXTpQjzdgb892rWTmMA50p6w'
SENDY_WEEKLY_BESTBUY_TABLES_ID = '8892mbG560A0LWviTocMTHjQ'
SENDY_MONTHLY_BESTBUY_TABLES_ID = 'EiqGkhI0mXMHATK6K9Uf763w'
SENDY_DAILY_BUSINESS_BESTBUY_TABLES_ID = 'mxdjBU1hBStbFqdUkz4h8g'
SENDY_WEEKLY_BUSINESS_BESTBUY_TABLES_ID = 'Cgi1FUKtniAZoFfZ2892pJKA'
SENDY_MONTHLY_BUSINESS_BESTBUY_TABLES_ID = '4LHCwTo5xg2KsOAUZRZM763A'
SENDY_BECKFORD_JAMES_REFERRAL_ID = 'ot3KvF3i3RMaS763C3I6AE3A'
SENDY_TPO_REFERRAL_ID = '057kgaDnYUpskKJUG6Df892A'
SENDY_PENSION_OPTIONS_ID = 'b9QXhHgUJmiacI9hmad50A'
SENDY_MINDFUL_MONEY_HEALTHCHECK_ID = '763QNWH763fvUxZxvqxwm75TNA'
SENDY_CHALLENGER_BANK_GUIDE_ID = 'XtxI3763nEJ2hTq2KlTiem4w'
SENDY_FSCS_REMINDER_DROP_TO_75000 = 'KNiCNNNz20jhL46jJkRTUQ'
SENDY_PSA_GUIDE_ID = 'iyPjpsRPdIvnQlxIlnsylA'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/London'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-gb'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True
DATE_FORMAT = 'j N, Y'


# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"


# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = 'https://static.savingschampion.co.uk/'
#STATIC_URL = 'static.savingschampion.co.uk.s3.amazonaws.com/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

LOGIN_REDIRECT_URL = '/'


# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'pipeline.finders.ManifestFinder',
    'pipeline.finders.PipelineFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'c0(f=ej7e(4$f%925o)cw#)gzm!%sfxwb9%dljyt-1for8exnj'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    #     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.cache.UpdateCacheMiddleware',
    'pipeline.middleware.MinifyHTMLMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'corsheaders.middleware.CorsPostCsrfMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'middleware.SubdomainsMiddleware',
    'middleware.MiddlewareResponseInjectP3P',
    'middleware.ReferrerSavingMiddleware',
    'middleware.ServerIdentification',
    'waffle.middleware.WaffleMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
)
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request',
    'context_processors.site_context'
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_DIR, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    # Uncomment the next line to enable the admin:
    'django.contrib.sites',
    'registration',
    'grappelli',
    'filebrowser',
    'django.contrib.admin',
    'collectfast',
    'django.contrib.staticfiles',
    'common',
    'products',
    'importer',
    'pages',
    'thisismoney',
    'administration',
    'ifa',
    'tinymce',
    'django.contrib.humanize',
    'django.contrib.sitemaps',
    'pipeline',
    'raven.contrib.django.raven_compat',
    'django_select2',
    'django_extensions',
    'crispy_forms',
    'icybackup',
    'rest_framework',
    'rest_framework.authtoken',
    'django_behave',
    'concierge',
    'waffle',
    'api.v1',
    'guardian',
    'report_builder',
    'ckeditor',
    'corsheaders',
    'rate_tracker'
)

HAYSTACK_SITECONF = 'search_sites'

SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

ACCOUNT_ACTIVATION_DAYS = 1000

TINYMCE_DEFAULT_CONFIG = {
    'plugins': "table,spellchecker,paste,searchreplace, autoresize, style",
    'theme': "advanced",
    'theme_advanced_buttons1_add': "forecolor, fontsizeselect, fontselect",
    'theme_advanced_buttons3_add': "tablecontrols",
    'cleanup_on_startup': True,
    'custom_undo_redo_levels': 10,
    'width': '100%',
    'autoresize_min_height': '400',
    'content_css': '../../../../static/css/libs/tinymce.css',
}

# TODO 
CAMPAIGNMONITOR_API_KEY = '91f6481eace2b60fe2e0a445bd59fc62'
CAMPAIGN_MONITOR_PRODUCT_ALERTS = '8a304e5c5222a5e962a526d94403513a'
CAMPAIGN_MONITOR_NEWSLETTERS = ''

CAMPAIGNMONITOR_CLIENT_ID = ''

AUTH_PROFILE_MODULE = 'common.Profile'

USERNAME_STEM = 'SCuser_'

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'INFO',
        'handlers': ['sentry'],
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'sentry': {
            'level': 'INFO',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'raven': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        '': {
            'handlers': ['sentry'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# SalesForce Specific Code
SALESFORCE_ENTERPRISE_WSDL = 'file://%s/common/enterprise_live.wsdl' % PROJECT_DIR
SALESFORCE_DJANGO_WSDL = 'file:///%s/common/djangoAdapter.wsdl' % PROJECT_DIR
# For Preview
# SALESFORCE_USER = 'savingschampion.co.uk.sfdc@silverlinedsolutions.com.djangoapi.sls'
# SALESFORCE_PASS = 'DjANGO12345'
# SALESFORCE_TOKEN = 'efUBhUSGOcz8LNkWcy9kbLYi'

# Between Live and Preview, we have different urls the url defined here is for testing
# THIS IS ACTUALLY WRITTEN IN THE WSDL FILES!!!
# SALESFORCE_ENDPOINT = 'https://test.salesforce.com/services/Soap/c/23.0'

AUTHENTICATION_BACKENDS = [
    'common.accounts.backends.email.EmailAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend',
]

ANONYMOUS_USER_ID = -1


PIPELINE_CSS = {
    'main': {
        'source_filenames': (
            'css/main/reset.css',
            'css/main/base.css',
            'css/main/style.css',
            'css/libs/chosen.css',
            'css/colorbox.css',
            '3rd_party/bx-slider.js/jquery.bxslider.css',
            'django_select2/css/all.min.css'
        ),
        'output_filename':
            'css/main.css',
    },
    'administration': {
        'source_filenames': (
            'css/administration/administration.css',
        ),
        'output_filename':
            'css/administration.css',
    }
}

PIPELINE_JS = {
    'global_base': {
        'source_filenames': (
            '3rd_party/gmaps/gmaps.js',
            '3rd_party/jquery-validation/dist/jquery.validate.js',
            '3rd_party/colorbox/jquery.colorbox.js',
            'js/base/base.js',
        ),
        'output_filename':
            'js/global_base.js',
    },
    'healthcheck_signup': {
        'source_filenames': (
            'js/healthcheck/signup.js',
            'js/healthcheck/basket.js',
            '3rd_party/chosen/chosen.jquery.min.js',
            'js/validation/healthcheck-signup-val.js',
        ),
        'output_filename':
            'js/healthcheck_signup.js',
    },
    'healthcheck_portfolio': {
        'source_filenames': (
            'js/libs/chosen.jquery.min.js',
            '3rd_party/isotope/jquery.isotope.min.js',
            '3rd_party/jquery-validation/jquery.validate.js',
            '3rd_party/colorbox/jquery.colorbox.js',
            'js/healthcheck/load_portfolio.js',
            'js/healthcheck/portfolio.js',
            'js/validation/healthcheck-portfolio-val.js',
        ),
        'output_filename':
            'js/healthcheck_portfolio.js',
    },
    'index': {
        'source_filenames': (
            '3rd_party/bx-slider.js/jquery.bxslider.min.js',
            '3rd_party/jquery-validation/jquery.validate.js',
            'js/validation/index-val.js',
            'js/index/index.js',
        ),
        'output_filename':
            'js/index.js',
    },
    'healthcheck_basket_signup': {
        'source_filenames': (
            'js/healthcheck/signup.js',
            'js/libs/chosen.jquery.min.js',
            'js/healthcheck/basket.js',
            'js/validation/healthcheck-signup-val.js',
        ),
        'output_filename': 'js/healthcheck_signup.js',
    },
    'ifa': {
        'source_filenames': (
            'js/ifa/ifa.js',
        ),
        'output_filename': 'js/ifa.min.js',
    },
    'bestbuys': {
        'source_filenames': (
            '3rd_party/jquery-cookie/jquery.cookie.js',
            'js/topaccounts/topaccounts.js'
        ),
        'output_filename': 'js/bestbuy.min.js',
    },
}

REPORT_BUILDER_INCLUDE = []

CRISPY_TEMPLATE_PACK = 'bootstrap3'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'api.v1.permissions.HasToken',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication', 'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.BrowsableAPIRenderer',
        'rest_framework.renderers.JSONRenderer',
        'rest_framework_xml.renderers.XMLRenderer',
    )
}

from django.contrib import messages

MESSAGE_TAGS = {
    messages.ERROR: 'danger'
}

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'http'

STATIC_ROOT = os.path.join(PROJECT_DIR, '..', 'static')

PIPELINE_YUGLIFY_BINARY = 'yuglify'

TEST_RUNNER = 'django_behave.runner.DjangoBehaveTestSuiteRunner'

PIPELINE_CSS_COMPRESSOR = 'pipeline.compressors.NoopCompressor'
PIPELINE_JS_COMPRESSOR = 'pipeline.compressors.NoopCompressor'

REPORT_BUILDER_ASYNC_REPORT = False

CMT_API_TOKEN = 'cc75af8ae822d26d78aaf8efb76c3a1f5ce4b038'

MARKUP_FIELD_TYPES = (
    ('markdown', markdown.markdown),
)

sentry_dsn = os.environ.get('sentry_dsn',
                            'https://7056202eadb94769aefca50e618b5d5f:3b9c48c5301c44ab963098c9a00e2110@sentry.savingschampion.co.uk/2')
protocol, url_first, url_end = sentry_dsn.rsplit(':')
_, url_last = sentry_dsn.split('@')

WEB_DSN = "{protocol}:{first}@{last}".format(protocol=protocol, first=url_first, last=url_last)

RAVEN_CONFIG = {'dsn': sentry_dsn, }

CKEDITOR_IMAGE_BACKEND = 'pillow'

CKEDITOR_CONFIGS = {
    "default": {
        'toolbar': 'full',
        "removePlugins": "stylesheetparser",
        "allowedContent": True,
    },
    "readonly_html_display": {
        "readOnly": True,
        "removePlugins": "stylesheetparser",
        "allowedContent": True,
    }
}

PIPELINE_DISABLE_WRAPPER = True

PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))



STATICFILES_DIRS = (
    os.path.join(PROJECT_DIR, 'resources'),
)


# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(PROJECT_DIR, 'assets')

HAYSTACK_SEARCH_ENGINE = 'simple'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = 'https://media.savingschampion.co.uk/'

GA_ACCOUNT = 'UA-27017192-1'

CKEDITOR_UPLOAD_PATH = os.path.join(MEDIA_ROOT, 'uploads')
CKEDITOR_MEDIA_PREFIX = "/assets/uploads/"
HTTPS_SUPPORT = True

SECURE_REQUIRED_PATHS = (
    '/',
    '/admin/',
    '/accounts/',
)

# Between Live and Preview, we have different urls the url defined here is for live,
SALESFORCE_USER = 'savingschampion.co.uk.sfdc@silverlinedsolutions.com.djangoapi'
SALESFORCE_PASS = 'DjANGO123456'
SALESFORCE_TOKEN = 'MNEeYIkCiryhiy1z2rTshDKR8'
SALESFORCE_ENDPOINT = 'https://eu1-api.salesforce.com/services/Soap/class/dJangoAdapter'

REGISTRATION_AUTO_LOGIN = True  # Automatically log the user in.

CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOW_CREDENTIALS = True

CORS_REPLACE_HTTPS_REFERER = True

import celeryapp

STATSD_HOST = 'stats.savingschampion.co.uk'
STATSD_PORT = 8125
STATSD_SAMPLE_RATE = 1
STATSD_BASE_CLIENT_NAME = 'website'

CONN_MAX_AGE = None

AWS_CREDENTIALS = {

    's3': {
        'bucket': os.environ.get('AWS_S3_BUCKET', 'savings-champion-static-files'),
        'secret_key': os.environ.get('AWS_S3_KEY', 'i11ULCdrZdlhcdml7eudYxrdA6bvi+0h+6sp9D9e'),
        'access_id': os.environ.get('AWS_S3_ID', 'AKIAIA5ACTPBQXBNUVZA'),
    },
    'ses': {
        'host': os.environ.get('AWS_SES_HOST', 'email-smtp.eu-west-1.amazonaws.com'),
        'user': os.environ.get('AWS_SES_USER', 'AKIAIO4YL7SZYD2A3R2Q'),
        'password': os.environ.get('AWS_SES_PASSWORD', 'Als0jjkE1eHhaQwMpDWVKAi77R9ACbqc5WbcXT3/rVvh'),
        'port': int(os.environ.get('AWS_SES_PORT', 587)),
    },
    'elasticache': {
        'host': os.environ.get('AWS_ELASTICACHE_HOST', 'website-cluster.vkylgx.0001.euw1.cache.amazonaws.com'),
        'port': int(os.environ.get('AWS_ELASTICACHE_PORT', 6379))
    },
    'rds': {
        'engine': 'django.db.backends.postgresql_psycopg2',
        'name': os.environ.get('AWS_RDS_DATABASE', 'savings_champion'),
        'user':  os.environ.get('AWS_RDS_USER', 'savings_champion'),
        'password': os.environ.get('AWS_RDS_PASSWORD', '4gPOAKHyRQsmmqSuW5bf9U0X4gvDkd'),
        'host': os.environ.get('AWS_RDS_HOST', 'savings-champion.ccy1i4hmxgnp.eu-west-1.rds.amazonaws.com'),
        'port': os.environ.get('AWS_RDS_PORT', '')
    }

}

MANDRILL_CREDENTIALS = {
    'default': {
        'host': os.environ.get('EMAIL_HOST', 'smtp.mandrillapp.com'),
        'user': os.environ.get('EMAIL_USER', 'josh@savingschampion.co.uk'),
        'password': os.environ.get('EMAIL_PASSWORD', '0Eu1mmSMZBWpdmQMLDa9Rg'),
        'port': int(os.environ.get('EMAIL_PORT', 587)),
    }
}

DATABASES = {
    'default': {
        'ENGINE': AWS_CREDENTIALS['rds']['engine'],
        # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': AWS_CREDENTIALS['rds']['name'],  # Or path to database file if using sqlite3.
        'USER': AWS_CREDENTIALS['rds']['user'],  # Not used with sqlite3.
        'PASSWORD': AWS_CREDENTIALS['rds']['password'],  # Not used with sqlite3.
        'HOST': AWS_CREDENTIALS['rds']['host'],  # Set to empty string for localhost. Not used with sqlite3.
        'PORT': AWS_CREDENTIALS['rds']['port'],  # Set to empty string for default. Not used with sqlite3.
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': "redis://{host}:{port}/0".format(host=AWS_CREDENTIALS['elasticache']['host'], port=AWS_CREDENTIALS['elasticache']['port']),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PARSER_CLASS": "redis.connection.HiredisParser",
        }
    },
    'collectfast': {
        # Your dedicated Collectfast cache - Disabled with superfast timeout while awaiting redis
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': "redis://{host}:{port}/1".format(host=AWS_CREDENTIALS['elasticache']['host'], port=AWS_CREDENTIALS['elasticache']['port']),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PARSER_CLASS": "redis.connection.HiredisParser",
        }
    }
}

DJANGO_REDIS_IGNORE_EXCEPTIONS = True

BROKER_URL = u'redis://{rabbitmq_host}:{rabbitmq_port}/2'.format(
    rabbitmq_host=AWS_CREDENTIALS['elasticache']['host'],
    rabbitmq_port=AWS_CREDENTIALS['elasticache']['port'])

CELERY_RESULT_BACKEND = BROKER_URL
CELERY_TASK_SERIALIZER = 'msgpack'
CELERY_RESULT_SERIALIZER = CELERY_TASK_SERIALIZER
CELERY_ACCEPT_CONTENT = ['msgpack', 'json', 'pickle']

CELERY_DEFAULT_QUEUE = 'celery'
CELERY_QUEUES = (
    Queue('celery', Exchange('celery'), routing_key='celery'),
    Queue('lead', Exchange('lead'), routing_key='lead'),
)

CELERYD_HIJACK_ROOT_LOGGER = False

EMAIL_PORT = MANDRILL_CREDENTIALS['default']['port']
EMAIL_HOST = MANDRILL_CREDENTIALS['default']['host']
EMAIL_HOST_USER = MANDRILL_CREDENTIALS['default']['user']
EMAIL_HOST_PASSWORD = MANDRILL_CREDENTIALS['default']['password']
EMAIL_USE_TLS = True

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
STATICFILES_STORAGE = 'common.storage.S3PipelineManifestStorage'

AWS_ACCESS_KEY_ID = AWS_CREDENTIALS['s3']['access_id']
AWS_SECRET_ACCESS_KEY = AWS_CREDENTIALS['s3']['secret_key']
AWS_STORAGE_BUCKET_NAME = AWS_CREDENTIALS['s3']['bucket']

AWS_PRELOAD_METADATA = True
AWS_S3_CALLING_FORMAT = SubdomainCallingFormat()
AWS_QUERYSTRING_AUTH = False

COLLECTFAST_ENABLED = True

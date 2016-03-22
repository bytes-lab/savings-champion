import os

from settings_base import *

DEBUG = True

# Between Live and Preview, we have different urls the url defined here is for preview,

SALESFORCE_ENTERPRISE_WSDL = 'file://%s/common/enterprise_preview.wsdl' % PROJECT_DIR
SALESFORCE_DJANGO_WSDL = 'file:///%s/common/djangoAdapter.wsdl' % PROJECT_DIR
# For Preview
SALESFORCE_USER = 'savingschampion.co.uk.sfdc@silverlinedsolutions.com.djangoapi.sls'
SALESFORCE_PASS = 'DjANGO12345'
SALESFORCE_TOKEN = 'efUBhUSGOcz8LNkWcy9kbLYi'

# Between Live and Preview, we have different urls the url defined here is for testing
# THIS IS ACTUALLY WRITTEN IN THE WSDL FILES!!!
SALESFORCE_ENDPOINT = 'https://test.salesforce.com/services/Soap/c/23.0'


MEDIA_URL = 'https://media-dev.savingschampion.co.uk/'

AWS_CREDENTIALS = {

    's3': {
        'bucket': os.environ.get('AWS_S3_BUCKET', 'savings-champion-static-files-dev'),
        'secret_key': os.environ.get('AWS_S3_KEY', 'i11ULCdrZdlhcdml7eudYxrdA6bvi+0h+6sp9D9e'),
        'access_id': os.environ.get('AWS_S3_ID', 'AKIAIA5ACTPBQXBNUVZA'),
    },
    'elasticache': {
        'host': os.environ.get('AWS_ELASTICACHE_HOST', 'website-cluster-dev.vkylgx.0001.euw1.cache.amazonaws.com'),
        'port': int(os.environ.get('AWS_ELASTICACHE_PORT', 6379))
    },
    'rds': {
        'engine': 'django.db.backends.postgresql_psycopg2',
        'name': os.environ.get('AWS_RDS_DATABASE', 'savings_champion'),
        'user':  os.environ.get('AWS_RDS_USER', 'savings_champion'),
        'password': os.environ.get('AWS_RDS_PASSWORD', '4gPOAKHyRQsmmqSuW5bf9U0X4gvDkd'),
        'host': os.environ.get('AWS_RDS_HOST', 'savings-champion-dev.ccy1i4hmxgnp.eu-west-1.rds.amazonaws.com'),
        'port': os.environ.get('AWS_RDS_PORT', '')
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

sentry_dsn = os.environ.get('sentry_dsn',
                            'https://c940db8257224401b0be10c7cacf74e0:3b349d3f248b48fdb23c11c40bc0b6d5@sentry.savingschampion.co.uk/5')
protocol, url_first, url_end = sentry_dsn.rsplit(':')
_, url_last = sentry_dsn.split('@')

WEB_DSN = "{protocol}:{first}@{last}".format(protocol=protocol, first=url_first, last=url_last)

RAVEN_CONFIG = {'dsn': sentry_dsn, }
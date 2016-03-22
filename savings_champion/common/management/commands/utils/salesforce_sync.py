"""
Common sync methods
"""

from django.conf import settings
import logging
from suds.sax.element import Element 
from urlparse import urlparse
from suds.client import Client

logging.basicConfig(level=logging.INFO)
logging.getLogger('suds.client').setLevel(logging.DEBUG)

def init_client(faults=True):
    ENTREPRISE_WSDL = getattr(settings,     'SALESFORCE_ENTERPRISE_WSDL')
    DJANGO_WSDL = getattr(settings,         'SALESFORCE_DJANGO_WSDL')
    SALESFORCE_ENDPOINT = getattr(settings, 'SALESFORCE_ENDPOINT')
    
    SALESFORCE_USER = getattr(settings,     'SALESFORCE_USER')
    SALESFORCE_PASS = getattr(settings,     'SALESFORCE_PASS')
    SALESFORCE_TOKEN = getattr(settings,    'SALESFORCE_TOKEN')
    
    # Use the entreprise login to get a session id
    entreprise_client = Client(ENTREPRISE_WSDL)
    #entreprise_client.wsdl.url = SALESFORCE_ENDPOINT
    
    login_result = entreprise_client.service.login(SALESFORCE_USER, 
                                                   SALESFORCE_PASS+SALESFORCE_TOKEN)
    

    # our client specific methods are in this specific       
   
    # NOTE we have to create the endpoint url using values from the serverUrl in the loginResponse plus 
    # the djangoAdapter schema
    
    options = urlparse(login_result.serverUrl)
    
    #DJANGO_SF_ENDPOINT = '%s://%s/services/Soap/class/dJangoAdapter' % (options.scheme, options.netloc)
    
    django_client = Client(DJANGO_WSDL, location = SALESFORCE_ENDPOINT, faults=faults)
         
    session_name_space = ('djan', 'http://soap.sforce.com/schemas/class/dJangoAdapter')
    session = Element('sessionId').setText(login_result.sessionId)
    wrapper = Element('SessionHeader')
    wrapper.append(session)
    
    django_client.set_options(soapheaders=wrapper)
    return django_client
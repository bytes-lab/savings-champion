from datetime import date
import json
from django.conf import settings

__author__ = 'josh'

import requests


class RemoteData(object):
    def __init__(self):
        self.host = getattr(settings, u'CMT_API_HOST', u'https://cmt.savingschampion.co.uk')
        self.api_token = getattr(settings, u'CMT_API_TOKEN')
        self.headers = {u'content-type': u'application/json',
                        u'Authorization': u'Token {api_key}'.format(api_key=self.api_token)}
        self.base_url = u''

    def get_page(self, page_number, params):
        params[u'page'] = page_number
        full_url = u"{host}{base_url}".format(host=self.host, base_url=self.base_url)
        r = requests.get(full_url, params=params, headers=self.headers)
        return r.json()

    def get_pages(self, params):
        response = []
        page = 1
        json_response = self.get_page(page, params)
        if u'results' in json_response:
            response = json_response[u'results']
        while u'next' in json_response and json_response[u'next'] is not None:
            page += 1
            json_response = self.get_page(page, params)
            if u'results' in json_response:
                response.extend(json_response[u'results'])
        return page, response

    def get(self, **kwargs):
        return self.get_pages(kwargs)

    def create_item(self, kwargs):
        if u'item_uuid' in kwargs:
            return self.create_or_update_item_at_id(kwargs)
        response = requests.post(u'{server_url}{api_url}'.format(server_url=self.host,
                                                                 api_url=self.base_url),
                                 data=json.dumps(kwargs), headers=self.headers)
        response.raise_for_status()
        return response

    def create_or_update_item_at_id(self, item_uuid, **kwargs):
        response = requests.put(u'{server_url}{api_url}{item_uuid}/'.format(server_url=self.host,
                                                                            api_url=self.base_url,
                                                                            item_uuid=item_uuid),
                                data=json.dumps(kwargs), headers=self.headers)
        response.raise_for_status()
        return response

    def get_or_create(self, search_params, **kwargs):
        response = requests.get(u'{server_url}{api_url}'.format(server_url=self.host,
                                                                api_url=self.base_url),
                                params=search_params,
                                headers=self.headers)
        response.raise_for_status()
        response_content = json.loads(response.content)
        if response_content[u'count'] == 0:
            response = self.create_item(kwargs)
            response_content = json.loads(response.content)
            return response_content[u'url']
        elif response_content[u'count'] > 1:
            raise AssertionError
        response_content = response_content[u'results'][0]
        return response_content[u'url']


class RemoteConciergeClient(RemoteData):
    def __init__(self, *args, **kwargs):
        super(RemoteConciergeClient, self).__init__()
        self.base_url = u'/api/v1/clients/'

    def enquiry_from_user(self, user, source, referrer):
        dob = user.profile.dob if user.profile.dob is not None else date.today()
        search_params = {
            'email': user.email
        }
        client = self.get_or_create(search_params=search_params,
                                    first_name=user.first_name,
                                    last_name=user.last_name,
                                    email=user.email,
                                    daytime_phone_number=user.profile.telephone,
                                    date_of_birth=dob.strftime(u'%Y-%m-%d'),
                                    active=False,
                                    adviser=None)
        RemoteConciergeClientSource().create_source_for_client(client, source, referrer)

    def enquiry_from_user_dict(self, user, source, referrer):
        if 'dob' in user:
            dob = user['dob'] if user['dob'] is not None else date.today()
        else:
            dob = date.today()

        if 'telephone' in user:
            telephone = user['telephone'] if user['telephone'] is not None else ''
        else:
            telephone = ''
        search_params = {
            'email': user['email']
        }
        client = self.get_or_create(
            search_params=search_params,
            first_name=user['first_name'],
            last_name=user['last_name'],
            email=user['email'],
            daytime_phone_number=telephone,
            telephone=[{'number': telephone}],
            date_of_birth=dob.strftime(u'%Y-%m-%d'),
            active=False,
            adviser=None
        )
        RemoteConciergeClientSource().create_source_for_client(client, source, referrer)


class RemoteConciergeClientSource(RemoteData):
    def __init__(self, *args, **kwargs):
        super(RemoteConciergeClientSource, self).__init__()
        self.base_url = u'/api/v1/client_sources/'

    def create_source_for_client(self, client, source, referrer):
        return self.create_item({
            u'client': client,
            u'source': source,
            u'referrer': referrer
        })

class RemoteConciergeClientNote(RemoteData):
    def __init__(self, *args, **kwargs):
        super(RemoteConciergeClientNote, self).__init__()
        self.base_url = u'/api/v1/client_events/'

    def create_note_for_client(self, email, note):
        results_count, client = RemoteConciergeClient().get(email=email)
        print(client)

        return self.create_item({
            u'client': client[0]['url'],
            u'event': u'notes_for_file',
            u'adviser': u'https://cmt.savingschampion.co.uk/api/v1/advisers/11/',
            u'notes': note
        })

import datetime
import arrow as arrow
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.utils.importlib import import_module
from concierge.cmt_adapter import RemoteConciergeClient, RemoteConciergeClientNote
from concierge.engine import compare_existing_portfolio_to_generated
from celery import shared_task
__author__ = 'josh'


@shared_task(soft_time_limit=60, time_limit=120)
def async_compare_existing_portfolio_to_generated(*args, **kwargs):
    result = compare_existing_portfolio_to_generated(*args, **kwargs)
    result['total_amount'] = float(result['total_amount'])  # forcing to float, because msgpack doesn't support decimal
    result['generated_interest'] = float(result['generated_interest'])
    result['expected_amount'] = float(result['expected_amount'])
    return {
        'total_amount': result['total_amount'],
        'generated_interest': result['generated_interest'],
        'expected_amount': result['expected_amount']
    }


@shared_task(bind=True, ignore_result=True, queue='lead', max_retries=0)
def register_enquiry(self, email, first_name, last_name, lead_source, referrer, telephone_number=None, date_of_birth=None):
    remote_concierge_client = RemoteConciergeClient()
    user = {
        u'email': email,
        u'first_name': first_name,
        u'last_name': last_name,
        u'telephone': telephone_number,
        u'date_of_birth': arrow.get(date_of_birth).naive,
    }

    try:
        remote_concierge_client.enquiry_from_user_dict(user, lead_source, referrer)
    except BaseException as exc:
        raise self.retry(exc=exc, countdown=min(2 ** self.request.retries, 128))


@shared_task(bind=True, ignore_result=True, queue='lead', max_retries=0)
def add_note_to_enquiry(self, email, note):
    remote_concierge_note = RemoteConciergeClientNote()

    try:
        remote_concierge_note.create_note_for_client(email, note)
    except BaseException as exc:
        raise self.retry(exc=exc, countdown=min(2 ** self.request.retries, 128))


@shared_task(bind=True, ignore_result=True)
def deactivate_old_temporary_user(self, email):
    User = get_user_model()
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return
    delete_all_unexpired_sessions_for_user(user)


def delete_all_unexpired_sessions_for_user(user):
    all_sessions = Session.objects.filter(expire_date__gte=datetime.datetime.now())
    SessionStore = import_module(settings.SESSION_ENGINE).SessionStore
    for session in all_sessions:
        session_data = session.get_decoded()
        if user.pk == session_data.get('_auth_user_id'):
            s = SessionStore(session_key=session.session_key)
            s.delete()

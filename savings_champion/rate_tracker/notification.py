from django.conf import settings

from common.models import CampaignsSignup

__author__ = 'josh'

from boto.ses import connection


def notify_rate_tracker_user_variable_rate(user, product):
    pass


    # Discover if user is concierge user

    concierge = CampaignsSignup.objects.filter(email=product_portfolio.user.email, is_client=True).exists()

    # render email from user and product data.

    rendered_email = None

    # Add email to SES queue

    ses_connection = connection.SESConnection(aws_access_key_id=settings.AWS_CREDENTIALS['ses']['access_id'],
                             aws_secret_access_key=settings.AWS_CREDENTIALS['ses']['secret_key'],
                             region='eu-west-1'
                             )


def notify_concierge_user_variable_rate():
    pass

    # Send alert to the CMT


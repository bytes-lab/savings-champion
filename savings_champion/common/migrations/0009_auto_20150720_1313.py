# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0008_auto_20150629_1320'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='profile',
            options={'get_latest_by': 'created_date', 'permissions': (('change_sccode', 'Can update SC codes for multiple accounts'), ('add_product', 'Can add a product to a customers portfolio'), ('change_user_portfolio', 'Can change a users portfolio'), ('change_user_activation', 'Can change a users activation status'), ('change_user_email', 'Can change a users email address'), ('add_concierge_client', 'Can add a new concierge client'), ('change_user_password', 'Can change a users password'), ('change_user_subscriptions', 'Can change a users subscriptions'), ('change_user_sync', 'Can change a users sync status'))},
        ),
    ]

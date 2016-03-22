# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('concierge', '0005_auto_20150518_1118'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adviserqueue',
            name='source',
            field=models.TextField(default=b'', choices=[(b'', b''), (b'7 Pitfalls', b'7 Pitfalls'), (b'Video 0.1%', b'Video 0.1%'), (b'Video', b'Video'), (b'Basket', b'Basket'), (b'Basket (Concierge)', b'Basket (Concierge)'), (b'Basket (Healthcheck)', b'Basket (Healthcheck)'), (b'Basket (Healthcheck and Concierge)', b'Basket (Healthcheck and Concierge)'), (b'Rate Tracker > 100K', b'Rate Tracker > 100K'), (b'Inbound Call', b'Inbound Call'), (b'Referral', b'Referral'), (b'Trust', b'Trust Concierge'), (b'Trust Concierge', b'Trust Concierge'), (b'Charity Concierge', b'Charity Concierge'), (b'Business Concierge', b'Business Concierge'), (b'Intermediary', b'Intermediary'), (b'50 Pound Challenge', b'50 Pound Challenge'), (b'Product Questionnaire', b'Product Questionnaire'), (b'The Biggest Mistake', b'The Biggest Mistake'), (b'The Value Of Advice', b'The Value Of Advice'), (b'THB Tool', b'Temporary High Balance Tool')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='adviserqueuehistory',
            name='source',
            field=models.TextField(default=b'', choices=[(b'', b''), (b'7 Pitfalls', b'7 Pitfalls'), (b'Video 0.1%', b'Video 0.1%'), (b'Video', b'Video'), (b'Basket', b'Basket'), (b'Basket (Concierge)', b'Basket (Concierge)'), (b'Basket (Healthcheck)', b'Basket (Healthcheck)'), (b'Basket (Healthcheck and Concierge)', b'Basket (Healthcheck and Concierge)'), (b'Rate Tracker > 100K', b'Rate Tracker > 100K'), (b'Inbound Call', b'Inbound Call'), (b'Referral', b'Referral'), (b'Trust', b'Trust Concierge'), (b'Trust Concierge', b'Trust Concierge'), (b'Charity Concierge', b'Charity Concierge'), (b'Business Concierge', b'Business Concierge'), (b'Intermediary', b'Intermediary'), (b'50 Pound Challenge', b'50 Pound Challenge'), (b'Product Questionnaire', b'Product Questionnaire'), (b'The Biggest Mistake', b'The Biggest Mistake'), (b'The Value Of Advice', b'The Value Of Advice'), (b'THB Tool', b'Temporary High Balance Tool')]),
            preserve_default=True,
        ),
    ]

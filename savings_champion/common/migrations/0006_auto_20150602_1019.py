# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0005_auto_20150409_1052'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userreferral',
            name='referral_action',
            field=models.CharField(default=b'unknown', max_length=130, choices=[(b'unknown', b'User Performed An Unknown Paid For Action'), (b'signup', b'User Signed Up'), (b'rate_tracker', b'User Subscribed To RateTracker'), (b'rate_tracker_used', b'User has used RateTracker'), (b'rate_alerts', b'User Subscribed To Rate Alerts'), (b'newsletter', b'User Subscribed To Newsletter'), (b'savers_priority_list', b'User Subscribed To The Savers Priority List'), (b'seven_pitfalls', b'User Signed Up Via Seven Pitfalls To Larger Savers'), (b'petition', b'User Subscribed To The Petition'), (b'concierge_enquiry', b'User Enquired About Concierge'), (b'concierge_client', b'User Signed Up To Concierge'), (b'recurring_daily_best_buys', b'User Signed Up For Recurring Best Buys - Daily'), (b'recurring_weekly_best_buys', b'User Signed Up For Recurring Best Buys - Weekly'), (b'recurring_monthly_best_buys', b'User Signed Up For Recurring Best Buys - Monthly'), (b'recurring_business_daily_best_buys', b'User Signed Up For Business Recurring Best Buys - Daily'), (b'recurring_business_weekly_best_buys', b'User Signed Up For Business Recurring Best Buys - Weekly'), (b'recurring_business_monthly_best_buys', b'User Signed Up For Business Recurring Best Buys - Monthly'), (b'fifty_pound_challenge', b'User Signed Up For The \xc2\xa350 Challenge'), (b'the_biggest_mistake', b'User Signed Up For The Biggest Mistake'), (b'the_value_of_advice', b'User Signed Up For The Value Of Advice'), (b'tpo_referral', b'User was referred to TPO'), (b'bj_referral', b'User was referred to Beckford James'), (b'concierge_pages', b'User signed up via concierge pages'), (b'iht_guide', b'User requested teh IHT Guide')]),
            preserve_default=True,
        ),
    ]

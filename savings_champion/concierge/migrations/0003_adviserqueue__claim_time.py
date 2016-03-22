# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('concierge', '0002_auto_20141205_1210'),
    ]

    operations = [
        migrations.AddField(
            model_name='adviserqueue',
            name='_claim_time',
            field=models.DecimalField(null=True, max_digits=14, decimal_places=0, blank=True),
            preserve_default=True,
        ),
    ]

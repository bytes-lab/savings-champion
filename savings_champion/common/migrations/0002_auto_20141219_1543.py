# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='ratetracker_threshold',
            field=models.DecimalField(default=0, max_digits=16, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='profile',
            name='ratetracker_threshold_set',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]

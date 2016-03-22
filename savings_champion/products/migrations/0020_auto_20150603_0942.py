# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0019_bestbuy_is_isa'),
    ]

    operations = [
        migrations.AddField(
            model_name='masterproduct',
            name='maximum_monthly',
            field=models.DecimalField(default=0, max_digits=14, decimal_places=3, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='masterproduct',
            name='minimum_monthly',
            field=models.DecimalField(default=0, max_digits=14, decimal_places=3, blank=True),
            preserve_default=True,
        ),
    ]

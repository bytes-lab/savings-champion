# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0036_auto_20150709_1434'),
    ]

    operations = [
        migrations.AlterField(
            model_name='producttier',
            name='underlying_gross_rate',
            field=models.DecimalField(default=0, max_digits=7, decimal_places=4),
            preserve_default=True,
        ),
    ]

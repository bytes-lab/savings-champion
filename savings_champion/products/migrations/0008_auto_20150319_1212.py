# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0007_weeklybusinessratealert'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='ranking',
            unique_together=set([('product', 'bestbuy', 'date_replaced')]),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0037_auto_20150709_1445'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fscslimittype',
            name='balance_limit',
            field=models.DecimalField(default=0, max_digits=19, decimal_places=3),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='fscslimittype',
            name='currency_code',
            field=models.TextField(default=b'GBP'),
            preserve_default=True,
        ),
    ]

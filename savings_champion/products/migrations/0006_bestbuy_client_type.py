# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0005_auto_20151008_1549'),
    ]

    operations = [
        migrations.AddField(
            model_name='bestbuy',
            name='client_type',
            field=models.CharField(default=b'p', max_length=3, choices=[(b'p', b'Personal'), (b'b', b'Business'), (b'c', b'Charity')]),
            preserve_default=True,
        ),
    ]

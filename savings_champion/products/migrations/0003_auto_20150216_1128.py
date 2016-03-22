# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_auto_20141218_0953'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ranking',
            options={'ordering': ('-date_created', 'bestbuy__title', 'rank')},
        ),
        migrations.AddField(
            model_name='ranking',
            name='date_created',
            field=models.DateTimeField(default=datetime.datetime.now, auto_now_add=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ranking',
            name='date_replaced',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='masterproduct',
            name='other_reason_to_exclude_this_product',
            field=models.TextField(default=b'', blank=True),
            preserve_default=True,
        ),
    ]

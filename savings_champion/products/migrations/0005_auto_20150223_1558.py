# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_auto_20150220_1010'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ranking',
            options={'ordering': ('-date_created', 'bestbuy__title', 'term', 'rank')},
        ),
        migrations.AddField(
            model_name='ranking',
            name='term',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, b'No Term'), (1, b'up to 1 Year'), (2, b'1-2 Years'), (3, b'2-3 Years'), (4, b'3-4 Years'), (5, b'5 Years and over')]),
            preserve_default=True,
        ),
    ]

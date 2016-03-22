# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0018_auto_20150518_1103'),
    ]

    operations = [
        migrations.AddField(
            model_name='bestbuy',
            name='is_isa',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]

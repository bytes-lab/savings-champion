# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0028_auto_20150703_1112'),
    ]

    operations = [
        migrations.AddField(
            model_name='producttier',
            name='split_interest',
            field=models.NullBooleanField(default=False),
            preserve_default=True,
        ),
    ]

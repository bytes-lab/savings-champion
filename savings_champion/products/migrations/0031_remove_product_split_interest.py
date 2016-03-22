# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0030_product_split_interest'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='split_interest',
        ),
    ]

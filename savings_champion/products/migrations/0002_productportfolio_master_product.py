# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_squashed_0042_auto_20150902_1206'),
    ]

    operations = [
        migrations.AddField(
            model_name='productportfolio',
            name='master_product',
            field=models.ForeignKey(to='products.MasterProduct', null=True),
            preserve_default=True,
        ),
    ]

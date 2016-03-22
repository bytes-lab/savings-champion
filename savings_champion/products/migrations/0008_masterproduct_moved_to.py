# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0007_auto_20151109_1007'),
    ]

    operations = [
        migrations.AddField(
            model_name='masterproduct',
            name='moved_to',
            field=models.ForeignKey(blank=True, to='products.MasterProduct', null=True),
            preserve_default=True,
        ),
    ]

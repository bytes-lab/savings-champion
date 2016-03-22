# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0020_auto_20150603_0942'),
    ]

    operations = [
        migrations.AlterField(
            model_name='masterproduct',
            name='maximum_monthly',
            field=models.DecimalField(default=0, max_digits=18, decimal_places=3, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='masterproduct',
            name='minimum_monthly',
            field=models.DecimalField(default=0, max_digits=18, decimal_places=3, blank=True),
            preserve_default=True,
        ),
    ]

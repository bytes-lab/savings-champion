# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_auto_20141218_0953'),
        ('pages', '0004_auto_20150105_1502'),
    ]

    operations = [
        migrations.AddField(
            model_name='factfindaccount',
            name='provider',
            field=models.ForeignKey(to='products.Provider', null=True),
            preserve_default=True,
        ),
    ]

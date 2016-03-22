# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0009_auto_20150720_1313'),
        ('products', '0039_thbtoolreminder'),
    ]

    operations = [
        migrations.AddField(
            model_name='thbtoolreminder',
            name='source',
            field=models.ForeignKey(to='common.Referrer', null=True),
            preserve_default=True,
        ),
    ]

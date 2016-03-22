# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0027_auto_20150702_1200'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='is_paid',
        ),
        migrations.AlterField(
            model_name='masterproduct',
            name='is_paid',
            field=models.NullBooleanField(default=False),
            preserve_default=True,
        ),
    ]

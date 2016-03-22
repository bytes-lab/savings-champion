# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0034_auto_20150709_1219'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='bonus_end_date',
        ),
        migrations.RemoveField(
            model_name='product',
            name='bonus_term',
        ),
    ]

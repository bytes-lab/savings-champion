# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0035_auto_20150709_1258'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='producttier',
            name='bonus_end_date',
        ),
        migrations.RemoveField(
            model_name='producttier',
            name='bonus_term',
        ),
    ]

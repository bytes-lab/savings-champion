# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0024_auto_20150618_1101'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='producttier',
            name='facts',
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_auto_20151008_1534'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productclickthrough',
            name='product',
        ),
        migrations.RemoveField(
            model_name='productclickthrough',
            name='referer',
        ),
        migrations.DeleteModel(
            name='ProductClickthrough',
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0017_product_fscs_licence'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='fscs_licence',
        ),
        migrations.RemoveField(
            model_name='product',
            name='url',
        ),
    ]

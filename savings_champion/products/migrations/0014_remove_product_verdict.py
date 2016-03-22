# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0013_product_verdict'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='verdict',
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0029_producttier_split_interest'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='split_interest',
            field=models.NullBooleanField(default=False),
            preserve_default=True,
        ),
    ]

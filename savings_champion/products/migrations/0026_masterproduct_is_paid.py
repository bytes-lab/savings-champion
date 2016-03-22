# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0025_remove_producttier_facts'),
    ]

    operations = [
        migrations.AddField(
            model_name='masterproduct',
            name='is_paid',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0013_masterproduct_removal_reason'),
    ]

    operations = [
        migrations.AlterField(
            model_name='provider',
            name='website',
            field=models.URLField(default=b'', max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
    ]

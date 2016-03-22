# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0014_remove_product_verdict'),
    ]

    operations = [
        migrations.AddField(
            model_name='masterproduct',
            name='url',
            field=models.URLField(max_length=300, null=True, blank=True),
            preserve_default=True,
        ),
    ]

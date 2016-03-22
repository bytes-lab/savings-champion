# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0012_auto_20150514_0950'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='verdict',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
    ]

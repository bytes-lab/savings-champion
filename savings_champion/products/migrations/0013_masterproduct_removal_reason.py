# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0012_auto_20160125_1650'),
    ]

    operations = [
        migrations.AddField(
            model_name='masterproduct',
            name='removal_reason',
            field=models.TextField(default=b''),
            preserve_default=True,
        ),
    ]

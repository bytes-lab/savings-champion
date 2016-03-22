# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0008_masterproduct_moved_to'),
    ]

    operations = [
        migrations.AddField(
            model_name='masterproduct',
            name='revert_on_bonus_end',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='masterproduct',
            name='revert_on_maturity',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]

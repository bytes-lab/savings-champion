# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0032_auto_20150708_1325'),
    ]

    operations = [
        migrations.AddField(
            model_name='masterproduct',
            name='bonus_end_date',
            field=models.DateField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='masterproduct',
            name='bonus_term',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]

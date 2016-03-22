# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('concierge', '0004_auto_20150518_1103'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conciergeuserpool',
            name='term',
            field=models.IntegerField(default=None, null=True, verbose_name=b'Maximum Term Length'),
            preserve_default=True,
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('rate_tracker', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ratetrackeralert',
            name='last_updated',
            field=models.DateTimeField(default=datetime.datetime(2015, 11, 11, 17, 20, 10, 928302), auto_now=True),
            preserve_default=False,
        ),
    ]

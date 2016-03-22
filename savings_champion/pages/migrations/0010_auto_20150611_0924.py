# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0009_moneytothemassessignup'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='outbrain_content',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='blogitem',
            name='outbrain_content',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]

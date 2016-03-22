# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0010_auto_20150611_0924'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='show_iht_advert',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='blogitem',
            name='show_iht_advert',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]

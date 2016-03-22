# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0002_auto_20141205_1210'),
    ]

    operations = [
        migrations.AddField(
            model_name='productfaq',
            name='logobar',
            field=models.TextField(default=b'logobar.html'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='productfaq',
            name='provider_url',
            field=models.URLField(default=b''),
            preserve_default=True,
        ),
    ]

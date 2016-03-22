# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0016_highworthsqueezepagesignup_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='highworthsqueezepagesignup',
            name='phone',
            field=models.TextField(default=b''),
            preserve_default=True,
        ),
    ]

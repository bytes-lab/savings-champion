# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0015_highworthsqueezepagesignup'),
    ]

    operations = [
        migrations.AddField(
            model_name='highworthsqueezepagesignup',
            name='name',
            field=models.TextField(default=b''),
            preserve_default=True,
        ),
    ]

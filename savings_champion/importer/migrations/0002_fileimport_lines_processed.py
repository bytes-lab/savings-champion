# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('importer', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='fileimport',
            name='lines_processed',
            field=models.PositiveIntegerField(default=0),
            preserve_default=True,
        ),
    ]

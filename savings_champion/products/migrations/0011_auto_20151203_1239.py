# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0010_auto_20151130_1650'),
    ]

    operations = [
        migrations.RenameField(
            model_name='productportfolio',
            old_name='last_checked',
            new_name='last_alerted',
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0011_profile_redd'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='redd',
            new_name='savings_calculator_email',
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0007_mindfulmoneyhealthchecksignup'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mindfulmoneyhealthchecksignup',
            name='postcode',
        ),
    ]

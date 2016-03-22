# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ifa', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bjsignup',
            name='telephone',
            field=models.CharField(max_length=100),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ifasignup',
            name='telephone',
            field=models.CharField(max_length=100),
            preserve_default=True,
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0011_auto_20151203_1239'),
    ]

    operations = [
        migrations.AlterField(
            model_name='provider',
            name='fscs_parent',
            field=models.TextField(help_text=b'Please enter this all as one word, for example: RoyalBankOfScotland', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='provider',
            name='slug',
            field=models.TextField(help_text=b'The slug is a url encoded version of your title and is used to create the web address'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='provider',
            name='title',
            field=models.TextField(unique=True),
            preserve_default=True,
        ),
    ]

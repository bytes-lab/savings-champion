# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0023_auto_20150618_1055'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='_facts_rendered',
        ),
        migrations.RemoveField(
            model_name='product',
            name='facts',
        ),
        migrations.RemoveField(
            model_name='product',
            name='facts_markup_type',
        ),
    ]

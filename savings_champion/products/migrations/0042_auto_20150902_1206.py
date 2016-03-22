# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0041_auto_20150824_1606'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='is_branch_access',
        ),
        migrations.RemoveField(
            model_name='product',
            name='is_cc_access',
        ),
        migrations.RemoveField(
            model_name='product',
            name='is_internet_access',
        ),
        migrations.RemoveField(
            model_name='product',
            name='is_open_branch',
        ),
        migrations.RemoveField(
            model_name='product',
            name='is_open_cc',
        ),
        migrations.RemoveField(
            model_name='product',
            name='is_open_internet',
        ),
        migrations.RemoveField(
            model_name='product',
            name='is_open_post',
        ),
        migrations.RemoveField(
            model_name='product',
            name='is_open_telephone',
        ),
        migrations.RemoveField(
            model_name='product',
            name='is_phone_access',
        ),
        migrations.RemoveField(
            model_name='product',
            name='is_post_access',
        ),
    ]

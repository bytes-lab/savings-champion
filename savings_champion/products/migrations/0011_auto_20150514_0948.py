# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0010_auto_20150424_1002'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='verdict',
        ),
        migrations.AddField(
            model_name='masterproduct',
            name='verdict',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='masterproduct',
            name='exclude_from_api_for',
            field=models.ManyToManyField(to='v1.ApiExcludedItem', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='product',
            name='exclude_from_api_for',
            field=models.ManyToManyField(to='v1.ApiExcludedItem', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='producttier',
            name='exclude_from_api_for',
            field=models.ManyToManyField(to='v1.ApiExcludedItem', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='provider',
            name='exclude_from_api_for',
            field=models.ManyToManyField(to='v1.ApiExcludedItem', null=True, blank=True),
            preserve_default=True,
        ),
    ]

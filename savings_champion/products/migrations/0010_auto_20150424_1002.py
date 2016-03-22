# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('v1', '0002_apiexcludeditem'),
        ('products', '0009_auto_20150409_1052'),
    ]

    operations = [
        migrations.AddField(
            model_name='masterproduct',
            name='exclude_from_api_for',
            field=models.ManyToManyField(to='v1.ApiExcludedItem'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='product',
            name='exclude_from_api_for',
            field=models.ManyToManyField(to='v1.ApiExcludedItem'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='producttier',
            name='exclude_from_api_for',
            field=models.ManyToManyField(to='v1.ApiExcludedItem'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='provider',
            name='exclude_from_api_for',
            field=models.ManyToManyField(to='v1.ApiExcludedItem'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='masterproduct',
            name='status',
            field=models.CharField(default=b'Default', max_length=20),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='ranking',
            unique_together=set([('rank', 'term', 'bestbuy', 'date_replaced'), ('product', 'bestbuy', 'date_replaced')]),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def move_data(apps, schema_editor):
    Product = apps.get_model("products", "Product")
    for product in Product.objects.all():
        product.master_product.url = product.url
        product.master_product.save()
        product.save()


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0015_masterproduct_url'),
    ]

    operations = [
        migrations.RunPython(move_data),
    ]

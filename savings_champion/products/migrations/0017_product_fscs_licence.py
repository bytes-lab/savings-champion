# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def move_data(apps, schema_editor):
    Product = apps.get_model("products", "Product")
    for product in Product.objects.all():
        product.master_product.fscs_licence = product.fscs_licence
        product.master_product.save()
        product.save()


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0016_product_url'),
    ]

    operations = [
        migrations.RunPython(move_data),
    ]

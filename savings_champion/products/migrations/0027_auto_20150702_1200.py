# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.db.migrations import RunPython


def migrate_is_paid_data(apps, schema_editor):
    Product = apps.get_model('products', 'Product')
    for product in Product.objects.all():
        product.master_product.is_paid = product.is_paid
        product.master_product.save()
        product.save()

class Migration(migrations.Migration):

    dependencies = [
        ('products', '0026_masterproduct_is_paid'),
    ]

    operations = [
        RunPython(migrate_is_paid_data),
    ]

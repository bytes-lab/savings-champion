# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def move_data(apps, schema_editor):
    Product = apps.get_model("products", "Product")
    for product in Product.objects.all():
        product.masterproduct.verdict = product.verdict
        product.masterproduct.save()
        product.save()

class Migration(migrations.Migration):

    dependencies = [
        ('products', '0011_auto_20150514_0948'),
    ]

    operations = [
        #migrations.RunPython(move_data),
    ]

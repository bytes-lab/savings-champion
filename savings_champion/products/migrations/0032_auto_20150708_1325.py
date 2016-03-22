# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.db.migrations import RunPython

def migrate_old_products_onto_newer_salesforce_ids(apps, schema_editor):
    Product = apps.get_model("products", "Product")
    ProductTier = apps.get_model("products", "ProductTier")
    for old_product_tier in Product.objects.all().order_by('publish_after'):
        if ProductTier.objects.filter(sf_product_tier_id=old_product_tier.sf_product_id).exists():
            product_tier = ProductTier.objects.filter(sf_product_tier_id=old_product_tier.sf_product_id).first()
            old_product_tier.master_product = product_tier.product
            old_product_tier.save()


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0031_remove_product_split_interest'),
    ]

    operations = [
        RunPython(migrate_old_products_onto_newer_salesforce_ids)
    ]

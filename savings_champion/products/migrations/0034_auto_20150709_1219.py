# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def migrate_old_bonus_info_to_master_product(apps, schema_editor):
    Product = apps.get_model('products', 'Product')
    MasterProduct = apps.get_model('products', 'MasterProduct')

    for product in Product.objects.all().order_by('publish_after'):
        product.master_product.bonus_term = product.bonus_term
        product.master_product.bonus_end_date = product.bonus_end_date
        product.master_product.save()

class Migration(migrations.Migration):

    dependencies = [
        ('products', '0033_auto_20150709_1208'),
    ]

    operations = [
        migrations.RunPython(migrate_old_bonus_info_to_master_product)
    ]

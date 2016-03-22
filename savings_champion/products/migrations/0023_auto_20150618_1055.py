# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def resave_facts(apps, schema_editor):
    MasterProduct = apps.get_model('products', 'MasterProduct')
    for master_product in MasterProduct.objects.exclude(facts=None):
        master_product.save()

class Migration(migrations.Migration):

    dependencies = [
        ('products', '0022_auto_20150618_1055'),
    ]

    operations = [
        migrations.RunPython(resave_facts),
    ]

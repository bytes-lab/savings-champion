# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.db.models import F


def autofill_product_portfolio_master_product(apps, schema_editor):
    ProductPortfolio = apps.get_model("products", "ProductPortfolio")
    product_portfolios = ProductPortfolio.objects.all()
    for x, product_portfolio in enumerate(product_portfolios):
        print("{x} of {y}".format(x=x, y=product_portfolios.count()))
        try:
            product_portfolio.master_product = product_portfolio.product.master_product
        except AttributeError:
            continue
        product_portfolio.save()


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_productportfolio_master_product'),
    ]

    operations = [
        migrations.RunPython(autofill_product_portfolio_master_product)
    ]

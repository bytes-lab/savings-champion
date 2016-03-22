# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_bestbuy_client_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='productportfolio',
            name='last_checked',
            field=models.DateField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='productportfolio',
            name='starting_rate',
            field=models.DecimalField(default=0, max_digits=6, decimal_places=4),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='bestbuy',
            name='title',
            field=models.CharField(max_length=200, choices=[(b'High Interest Current Accounts', b'High Interest Current Accounts'), (b'Current Accounts', b'High Interest Current Accounts'), (b'Easy Access', b'Easy Access'), (b'Fixed Rate Bonds', b'Fixed Rate Bonds'), (b'Variable Rate ISAs', b'Variable Rate ISAs'), (b'Fixed Rate ISAs', b'Fixed Rate ISAs'), (b'Notice Accounts', b'Notice Accounts'), (b'Monthly Income', b'Monthly Income'), (b'Regular Savings', b'Regular Savings'), (b"Children's Accounts", b"Children's Accounts"), (b'Junior ISA', b'Junior ISAs'), (b'Index Linked Certificate', b'Index Linked Certificate'), (b'Variable Rate Bond', b'Variable Rate Bond'), (b'Sharia Accounts', b'Sharia Accounts')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='productportfolio',
            name='master_product',
            field=models.ForeignKey(to='products.MasterProduct'),
            preserve_default=True,
        ),
    ]

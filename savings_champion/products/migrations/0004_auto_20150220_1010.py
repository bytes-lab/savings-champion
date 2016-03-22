# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import markupfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_auto_20150216_1128'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ranking',
            options={'ordering': ('bestbuy__title', 'rank')},
        ),
        migrations.AddField(
            model_name='product',
            name='_facts_rendered',
            field=models.TextField(default='', editable=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='product',
            name='facts_markup_type',
            field=models.CharField(default=b'markdown', max_length=30, editable=False, choices=[(b'', b'--'), (b'markdown', b'markdown')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='bestbuy',
            name='title',
            field=models.CharField(max_length=200, choices=[(b'High Interest Current Accounts', b'High Interest Current Accounts'), (b'Current Accounts', b'High Interest Current Accounts'), (b'Easy Access', b'Easy Access'), (b'Fixed Rate Bonds', b'Fixed Rate Bonds'), (b'Variable Rate ISAs', b'Variable Rate ISAs'), (b'Fixed Rate ISAs', b'Fixed Rate ISAs'), (b'Notice Accounts', b'Notice Accounts'), (b'Monthly Income', b'Monthly Income'), (b'Regular Savings', b'Regular Savings'), (b"Children's Accounts", b"Children's Accounts"), (b'Junior ISA', b'Junior ISA'), (b'Index Linked Certificate', b'Index Linked Certificate'), (b'Variable Rate Bond', b'Variable Rate Bond')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='product',
            name='facts',
            field=markupfield.fields.MarkupField(default=b''),
            preserve_default=True,
        ),
    ]

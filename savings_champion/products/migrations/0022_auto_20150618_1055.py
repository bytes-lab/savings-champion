# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import markupfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0021_auto_20150603_0951'),
    ]

    operations = [
        migrations.AddField(
            model_name='masterproduct',
            name='_facts_rendered',
            field=models.TextField(default=' ', editable=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='masterproduct',
            name='facts_markup_type',
            field=models.CharField(default=b'markdown', max_length=30, editable=False, choices=[(b'', b'--'), (b'markdown', b'markdown')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='masterproduct',
            name='facts',
            field=markupfield.fields.MarkupField(default=b'', rendered_field=True),
            preserve_default=True,
        ),
    ]

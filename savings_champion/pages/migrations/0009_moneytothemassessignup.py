# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0008_remove_mindfulmoneyhealthchecksignup_postcode'),
    ]

    operations = [
        migrations.CreateModel(
            name='MoneyToTheMassesSignup',
            fields=[
                ('uuid', django_extensions.db.fields.UUIDField(serialize=False, editable=False, primary_key=True, blank=True)),
                ('name', models.TextField()),
                ('email', models.EmailField(max_length=75)),
                ('phone', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_auto_20150302_1709'),
    ]

    operations = [
        migrations.CreateModel(
            name='WeeklyBusinessRateAlert',
            fields=[
                ('uuid', django_extensions.db.fields.UUIDField(serialize=False, editable=False, primary_key=True, blank=True)),
                ('email', models.EmailField(max_length=75)),
                ('signup_date', models.DateTimeField(auto_now_add=True)),
                ('frequency', models.IntegerField(default=2, choices=[(2, b'Deliver Weekly'), (3, b'Deliver Monthly')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]

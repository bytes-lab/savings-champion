# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0038_auto_20150728_1412'),
    ]

    operations = [
        migrations.CreateModel(
            name='THBToolReminder',
            fields=[
                ('uuid', django_extensions.db.fields.UUIDField(serialize=False, editable=False, primary_key=True, blank=True)),
                ('name', models.TextField(default=b'')),
                ('email', models.EmailField(max_length=75)),
                ('phone_number', models.TextField(default=b'')),
                ('reminder_date', models.DateField()),
                ('callback', models.BooleanField(default=False)),
                ('scheduled_callback', models.BooleanField(default=False)),
                ('sent', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]

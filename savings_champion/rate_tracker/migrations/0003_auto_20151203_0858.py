# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import ckeditor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('rate_tracker', '0002_ratetrackeralert_last_updated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ratetrackeralert',
            name='alert_email',
            field=ckeditor.fields.RichTextField(default=b''),
            preserve_default=True,
        ),
    ]

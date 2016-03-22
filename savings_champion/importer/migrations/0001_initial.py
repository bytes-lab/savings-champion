# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FileImport',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('csv_file', models.FileField(upload_to=b'imports/')),
                ('is_processed', models.BooleanField(default=False)),
                ('process_date', models.DateTimeField(null=True, blank=True)),
                ('created_date', models.DateTimeField(auto_now=True)),
                ('last_updated', models.DateTimeField(auto_now_add=True)),
                ('has_bestbuys', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserListImport',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('csv_file', models.FileField(upload_to=b'imports/')),
                ('has_been_run', models.BooleanField(default=False)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]

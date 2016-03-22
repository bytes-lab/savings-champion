# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0003_auto_20141205_1536'),
    ]

    operations = [
        migrations.CreateModel(
            name='FactFindAccount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('account_type', models.TextField(choices=[(b'easy_access', b'Easy Access Account'), (b'notice', b'Notice Account'), (b'current', b'High Interest Current Account'), (b'1y_fixed_rate', b'1Yr Fixed Rate Bond'), (b'2y_fixed_rate', b'2Yr Fixed Rate Bond'), (b'3y_fixed_rate', b'3Yr Fixed Rate Bond'), (b'4y_fixed_rate', b'4Yr Fixed Rate Bond'), (b'5y_fixed_rate', b'5Yr Fixed Rate Bond'), (b'6y_fixed_rate', b'6Yr Fixed Rate Bond'), (b'7y_fixed_rate', b'7Yr Fixed Rate Bond'), (b'other_fixed_rate', b'Other Fixed Rate Bond'), (b'variable_rate', b'Variable Rate Bond'), (b'regular_saver', b'Regular Savings Account'), (b'fixed_rate_isa', b'Fixed Rate ISA'), (b'variable_rate_isa', b'Variable Rate ISA')])),
                ('amount', models.TextField()),
                ('rate', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FactFindSignup',
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
        migrations.AddField(
            model_name='factfindaccount',
            name='challenge_signup',
            field=models.ForeignKey(to='pages.FactFindSignup'),
            preserve_default=True,
        ),
    ]

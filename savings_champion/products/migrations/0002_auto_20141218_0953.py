# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='masterproduct',
            name='account_type',
            field=models.CharField(default=b'P', max_length=1, verbose_name=b'Account Type', choices=[(b'P', b'Personal'), (b'p', b'Personal'), (b'B', b'Business'), (b'b', b'Business'), (b'C', b'Charity'), (b'c', b'Charity'), (b'O', b'Unknown')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='product',
            name='account_type',
            field=models.CharField(default=b'P', max_length=1, verbose_name=b'Account Type', choices=[(b'P', b'Personal'), (b'p', b'Personal'), (b'B', b'Business'), (b'b', b'Business'), (b'C', b'Charity'), (b'c', b'Charity'), (b'O', b'Unknown')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='producttier',
            name='account_type',
            field=models.CharField(default=b'P', max_length=1, verbose_name=b'Account Type', choices=[(b'P', b'Personal'), (b'p', b'Personal'), (b'B', b'Business'), (b'b', b'Business'), (b'C', b'Charity'), (b'c', b'Charity'), (b'O', b'Unknown')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='provider',
            name='fitchs_rating',
            field=models.CharField(default=0, max_length=4, null=True, blank=True, choices=[(0, b'None'), (None, b'None'), (b'A+', b'A+'), (b'A', b'A'), (b'B', b'B'), (b'C', b'C')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='provider',
            name='moodys_rating',
            field=models.CharField(blank=True, max_length=4, null=True, choices=[(None, b'None'), (b'0', b'None'), (b'A1', b'Obligations rated A are considered upper-medium grade and are subject to low credit risk'), (b'A2', b'Obligations rated A are considered upper-medium grade and are subject to low credit risk'), (b'A3', b'Obligations rated A are considered upper-medium grade and are subject to low credit risk'), (b'Aa1', b'Obligations rated Aa are judged to be of high quality and are subject to very low credit risk'), (b'Aa2', b'Obligations rated Aa are judged to be of high quality and are subject to very low credit risk'), (b'Aa3', b'Obligations rated Aa are judged to be of high quality and are subject to very low credit risk'), (b'Aaa1', b'Obligations rated Aaa are judged to be of the highest quality, with minimal credit risk.'), (b'Aaa2', b'Obligations rated Aaa are judged to be of the highest quality, with minimal credit risk.'), (b'Aaa3', b'Obligations rated Aaa are judged to be of the highest quality, with minimal credit risk.'), (b'B1', b'Obligations rated B are considered speculative and are subject to high credit risk.'), (b'B2', b'Obligations rated B are considered speculative and are subject to high credit risk.'), (b'B3', b'Obligations rated B are considered speculative and are subject to high credit risk.'), (b'Ba1', b'Obligations rated Ba are judged to have speculative elements and are subject to substantial credit risk.'), (b'Ba2', b'Obligations rated Ba are judged to have speculative elements and are subject to substantial credit risk.'), (b'Ba3', b'Obligations rated Ba are judged to have speculative elements and are subject to substantial credit risk.'), (b'Baa1', b'Obligations rated Baa are subject to moderate credit risk. They are considered medium-grade and as such may possess certain speculative characteristics.'), (b'Baa2', b'Obligations rated Baa are subject to moderate credit risk. They are considered medium-grade and as such may possess certain speculative characteristics.'), (b'Baa3', b'Obligations rated Baa are subject to moderate credit risk. They are considered medium-grade and as such may possess certain speculative characteristics.'), (b'C1', b'Obligations rated C are the lowest rated class of bonds and are typically in default, with little prospect for recovery of principal or interest.'), (b'C2', b'Obligations rated C are the lowest rated class of bonds and are typically in default, with little prospect for recovery of principal or interest.'), (b'C3', b'Obligations rated C are the lowest rated class of bonds and are typically in default, with little prospect for recovery of principal or interest.'), (b'Ca1', b'Obligations rated Ca are highly speculative and are likely in, or very near, default, with some prospect of recovery of principal and interest.'), (b'Ca2', b'Obligations rated Ca are highly speculative and are likely in, or very near, default, with some prospect of recovery of principal and interest.'), (b'Ca3', b'Obligations rated Ca are highly speculative and are likely in, or very near, default, with some prospect of recovery of principal and interest.'), (b'Caa1', b'Obligations rated Caa are judged to be of poor standing and are subject to very high credit risk.'), (b'Caa2', b'Obligations rated Caa are judged to be of poor standing and are subject to very high credit risk.'), (b'Caa3', b'Obligations rated Caa are judged to be of poor standing and are subject to very high credit risk.')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='provider',
            name='provider_maximum',
            field=models.DecimalField(default=0, max_digits=18, decimal_places=2, blank=True),
            preserve_default=True,
        ),
    ]

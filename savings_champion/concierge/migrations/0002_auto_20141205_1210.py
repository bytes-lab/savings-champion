# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('concierge', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='conciergeuserrequiredproduct',
            name='master_product',
            field=models.ForeignKey(to='products.MasterProduct', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='conciergeuserremovedproduct',
            name='concierge_user',
            field=models.ForeignKey(to='concierge.ConciergeUserOption'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='conciergeuserremovedproduct',
            name='master_product',
            field=models.ForeignKey(to='products.MasterProduct', null=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='conciergeuserremovedproduct',
            unique_together=set([('concierge_user', 'master_product')]),
        ),
        migrations.AddField(
            model_name='conciergeuserproviderrisk',
            name='provider',
            field=models.ForeignKey(to='products.Provider'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='conciergeuserproviderrisk',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='conciergeuserproviderrisk',
            unique_together=set([('user', 'provider')]),
        ),
        migrations.AddField(
            model_name='conciergeuserpool',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='conciergeuseroption',
            name='enquiry',
            field=models.ForeignKey(to='concierge.AdviserQueue', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='conciergeuseroption',
            name='user',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='conciergeusernotes',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='conciergeuserlicencerisk',
            name='provider',
            field=models.ForeignKey(help_text=b'Select any member of the banking licence, the licence owner will be discovered automatically', to='products.Provider'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='conciergeuserlicencerisk',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='conciergeuserlicencerisk',
            unique_together=set([('user', 'provider')]),
        ),
        migrations.AddField(
            model_name='conciergeuseracceptedproduct',
            name='concierge_user',
            field=models.ForeignKey(to='concierge.ConciergeUserOption'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='conciergeuseracceptedproduct',
            name='product',
            field=models.ForeignKey(to='products.MasterProduct'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='conciergeuseracceptedproduct',
            unique_together=set([('concierge_user', 'product', 'restriction')]),
        ),
        migrations.AddField(
            model_name='conciergeprovideraccounttypelimitation',
            name='bestbuys',
            field=models.ManyToManyField(to='products.BestBuy'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='conciergeprovideraccounttypelimitation',
            name='provider',
            field=models.ForeignKey(to='products.Provider'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='conciergeleadcapture',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='conciergeleadcapture',
            unique_together=set([('user', 'named_user')]),
        ),
        migrations.AddField(
            model_name='adviserqueuehistory',
            name='adviser_queue',
            field=models.ForeignKey(to='concierge.AdviserQueue'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='adviserqueue',
            name='adviser',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
    ]

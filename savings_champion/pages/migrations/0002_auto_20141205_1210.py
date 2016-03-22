# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pages', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ratealert',
            name='bestbuy',
            field=models.ForeignKey(to='products.BestBuy'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='productfaquestion',
            name='faq',
            field=models.ForeignKey(to='pages.ProductFAQ'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='pressappearance',
            name='publication',
            field=models.ForeignKey(to='pages.PressAppearancePublication'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='pressappearance',
            unique_together=set([('publication_type', 'publication', 'title', 'author', 'link', 'date_featured')]),
        ),
        migrations.AddField(
            model_name='pagebody',
            name='page',
            field=models.OneToOneField(related_name='body', to='pages.Page'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='pageblock',
            name='author',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='formmessage',
            name='author',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='fiftypoundchallengeaccount',
            name='challenge_signup',
            field=models.ForeignKey(to='pages.FiftyPoundChallengeSignup'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='faqblock',
            name='faq',
            field=models.ForeignKey(to='pages.FAQ'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='childpage',
            name='parent',
            field=models.ForeignKey(to='pages.ParentPage', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='blogitem',
            name='author',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='blogcomment',
            name='blog_comment',
            field=models.ForeignKey(to='pages.BlogItem'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='basecomment',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='award',
            name='category',
            field=models.ForeignKey(to='pages.AwardCategory'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='award',
            name='product',
            field=models.ForeignKey(blank=True, to='products.MasterProduct', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='award',
            name='provider',
            field=models.ForeignKey(to='products.Provider'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='articlecomment',
            name='article_comment',
            field=models.ForeignKey(to='pages.Article'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='article',
            name='author',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='article',
            name='document',
            field=models.ManyToManyField(to='pages.Document', null=True, blank=True),
            preserve_default=True,
        ),
    ]

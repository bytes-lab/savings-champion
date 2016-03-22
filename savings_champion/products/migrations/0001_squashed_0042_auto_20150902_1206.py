# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import django_extensions.db.fields
from decimal import Decimal
import markupfield.fields
from django.conf import settings


# Functions from the following migrations need manual copying.
# Move them and any dependencies into this file, then update the
# RunPython operations to refer to the local versions:
# products.migrations.0016_product_url
# products.migrations.0034_auto_20150709_1219
# products.migrations.0023_auto_20150618_1055
# products.migrations.0027_auto_20150702_1200
# products.migrations.0032_auto_20150708_1325
# products.migrations.0017_product_fscs_licence

def migrate_is_paid_data(apps, schema_editor):
    Product = apps.get_model('products', 'Product')
    for product in Product.objects.all():
        product.master_product.is_paid = product.is_paid
        product.master_product.save()
        product.save()

def move_data_16(apps, schema_editor):
    Product = apps.get_model("products", "Product")
    for product in Product.objects.all():
        product.master_product.url = product.url
        product.master_product.save()
        product.save()

def move_data_17(apps, schema_editor):
    Product = apps.get_model("products", "Product")
    for product in Product.objects.all():
        product.master_product.fscs_licence = product.fscs_licence
        product.master_product.save()
        product.save()

def resave_facts(apps, schema_editor):
    MasterProduct = apps.get_model('products', 'MasterProduct')
    for master_product in MasterProduct.objects.exclude(facts=None):
        master_product.save()

def migrate_old_products_onto_newer_salesforce_ids(apps, schema_editor):
    Product = apps.get_model("products", "Product")
    ProductTier = apps.get_model("products", "ProductTier")
    for old_product_tier in Product.objects.all().order_by('publish_after'):
        if ProductTier.objects.filter(sf_product_tier_id=old_product_tier.sf_product_id).exists():
            product_tier = ProductTier.objects.filter(sf_product_tier_id=old_product_tier.sf_product_id).first()
            old_product_tier.master_product = product_tier.product
            old_product_tier.save()

def migrate_old_bonus_info_to_master_product(apps, schema_editor):
    Product = apps.get_model('products', 'Product')
    MasterProduct = apps.get_model('products', 'MasterProduct')

    for product in Product.objects.all().order_by('publish_after'):
        product.master_product.bonus_term = product.bonus_term
        product.master_product.bonus_end_date = product.bonus_end_date
        product.master_product.save()

class Migration(migrations.Migration):

    replaces = [(b'products', '0001_initial'), (b'products', '0002_auto_20141218_0953'), (b'products', '0003_auto_20150216_1128'), (b'products', '0004_auto_20150220_1010'), (b'products', '0005_auto_20150223_1558'), (b'products', '0006_auto_20150302_1709'), (b'products', '0007_weeklybusinessratealert'), (b'products', '0008_auto_20150319_1212'), (b'products', '0009_auto_20150409_1052'), (b'products', '0010_auto_20150424_1002'), (b'products', '0011_auto_20150514_0948'), (b'products', '0012_auto_20150514_0950'), (b'products', '0013_product_verdict'), (b'products', '0014_remove_product_verdict'), (b'products', '0015_masterproduct_url'), (b'products', '0016_product_url'), (b'products', '0017_product_fscs_licence'), (b'products', '0018_auto_20150518_1103'), (b'products', '0019_bestbuy_is_isa'), (b'products', '0020_auto_20150603_0942'), (b'products', '0021_auto_20150603_0951'), (b'products', '0022_auto_20150618_1055'), (b'products', '0023_auto_20150618_1055'), (b'products', '0024_auto_20150618_1101'), (b'products', '0025_remove_producttier_facts'), (b'products', '0026_masterproduct_is_paid'), (b'products', '0027_auto_20150702_1200'), (b'products', '0028_auto_20150703_1112'), (b'products', '0029_producttier_split_interest'), (b'products', '0030_product_split_interest'), (b'products', '0031_remove_product_split_interest'), (b'products', '0032_auto_20150708_1325'), (b'products', '0033_auto_20150709_1208'), (b'products', '0034_auto_20150709_1219'), (b'products', '0035_auto_20150709_1258'), (b'products', '0036_auto_20150709_1434'), (b'products', '0037_auto_20150709_1445'), (b'products', '0038_auto_20150728_1412'), (b'products', '0039_thbtoolreminder'), (b'products', '0040_thbtoolreminder_source'), (b'products', '0041_auto_20150824_1606'), (b'products', '0042_auto_20150902_1206')]

    dependencies = [
        ('common', '0009_auto_20150720_1313'),
        ('common', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('v1', '0002_apiexcludeditem'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdvantagesBlock',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(blank=True, max_length=20, choices=[(b'pro', b'Pro'), (b'con', b'Con')])),
                ('text', models.CharField(max_length=500, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BestBuy',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200)),
                ('slug', models.CharField(help_text=b'The slug is a url encoded version of your title and is used to create the web address', max_length=200)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.BooleanField(default=False)),
                ('meta_description', models.CharField(max_length=200, null=True, verbose_name=b'Tables Meta Description', blank=True)),
                ('comparison_meta_description', models.CharField(max_length=200, null=True, verbose_name=b'Comparison Page Meta Description', blank=True)),
                ('description', models.TextField(help_text=b'Please enter a short description describing the Best Buy type', blank=True)),
                ('landing_page_description', models.TextField(help_text=b'Please enter a short description describing the Best Buy type', blank=True)),
                ('order', models.IntegerField(help_text=b'You can affect the ordering of the Best Buys by adding in a number here, we order from smallest to largest.', null=True, blank=True)),
                ('has_table', models.BooleanField(default=False, verbose_name=b'Show best buy table?')),
                ('tips', models.TextField(blank=True)),
                ('is_fixed', models.NullBooleanField(default=False)),
                ('is_bond', models.BooleanField(default=False)),
                ('ratetracker_enabled', models.NullBooleanField(default=False, verbose_name=b'Show on Rate Tracker')),
                ('author', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, help_text=b"The author's name appears as a citation against the description", null=True)),
            ],
            options={
                'ordering': ('order',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FSCSLimitType',
            fields=[
                ('uuid', django_extensions.db.fields.UUIDField(serialize=False, editable=False, primary_key=True, blank=True)),
                ('name', models.TextField()),
                ('balance_limit', models.DecimalField(max_digits=19, decimal_places=3)),
                ('balance_unlimited', models.BooleanField(default=False)),
                ('currency_code', models.TextField()),
                ('multiplier_if_joint', models.DecimalField(default=Decimal('2'), max_digits=19, decimal_places=3)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='InterestPaidFrequency',
            fields=[
                ('uuid', django_extensions.db.fields.UUIDField(serialize=False, editable=False, primary_key=True, blank=True)),
                ('title', models.TextField(default=b'')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MasterProduct',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200)),
                ('slug', models.CharField(help_text=b'The slug is a url encoded version of your title and is used to create the web address', max_length=200)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.BooleanField(default=False)),
                ('sf_product_id', models.CharField(unique=True, max_length=255)),
                ('status', models.CharField(max_length=20, null=True, blank=True)),
                ('account_type', models.CharField(default=b'P', max_length=1, verbose_name=b'Account Type', choices=[(b'P', b'Personal'), (b'B', b'Business'), (b'C', b'Charity')])),
                ('available_from', models.DateField(null=True, blank=True)),
                ('available_to', models.DateField(null=True, blank=True)),
                ('is_internet_access', models.BooleanField(default=False, verbose_name=b'Internet Access')),
                ('is_phone_access', models.BooleanField(default=False, verbose_name=b'Telephone Access')),
                ('is_post_access', models.BooleanField(default=False, verbose_name=b'Post Access')),
                ('is_branch_access', models.BooleanField(default=False, verbose_name=b'Branch Access')),
                ('is_cc_access', models.BooleanField(default=False, verbose_name=b'Cash Card Access')),
                ('is_open_internet', models.BooleanField(default=False, verbose_name=b'Can it be opened via the internet')),
                ('is_open_telephone', models.BooleanField(default=False, verbose_name=b'Can it be opened via the phone')),
                ('is_open_post', models.BooleanField(default=False, verbose_name=b'Can it be opened through the post')),
                ('is_open_branch', models.BooleanField(default=False, verbose_name=b'Can it be opened through the post')),
                ('is_open_cc', models.BooleanField(default=False, verbose_name=b'Can it be opened via a cash card')),
                ('is_isa_transfers_in', models.BooleanField(default=False, verbose_name=b'Transfer ISAs in')),
                ('is_fixed', models.BooleanField(default=False)),
                ('facts', models.TextField(null=True, blank=True)),
                ('fscs_licence', models.CharField(max_length=200, null=True, blank=True)),
                ('term', models.IntegerField(default=0)),
                ('term_fixed_date', models.DateField(null=True, blank=True)),
                ('notice', models.IntegerField(default=0)),
                ('shariaa', models.BooleanField(default=False)),
                ('existing_only', models.BooleanField(default=False)),
                ('locals_only', models.BooleanField(default=False)),
                ('operating_balance', models.DecimalField(default=0, max_digits=18, decimal_places=10)),
                ('operating_balance_rate', models.DecimalField(default=0, max_digits=18, decimal_places=10)),
                ('other_reason_to_exclude_this_product', models.TextField(default=b'')),
                ('other_reason_compliance_checked', models.BooleanField(default=False)),
                ('trust_funds_accepted', models.BooleanField(default=False)),
                ('minimum_age', models.IntegerField(default=0, null=True, blank=True)),
                ('maximum_age', models.IntegerField(default=0, null=True, blank=True)),
                ('open_limit_total', models.IntegerField(default=-1)),
                ('open_limit_own_name', models.IntegerField(default=-1)),
                ('open_limit_joint_name', models.IntegerField(default=-1)),
                ('bestbuy_type', models.ManyToManyField(to=b'products.BestBuy', null=True, blank=True)),
                ('interest_paid_frequency', models.ManyToManyField(to=b'products.InterestPaidFrequency')),
            ],
            options={
                'ordering': ('title',),
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200)),
                ('slug', models.CharField(help_text=b'The slug is a url encoded version of your title and is used to create the web address', max_length=200)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.BooleanField(default=False)),
                ('sc_code', models.CharField(help_text=b'This is Savings Champion unique identifier for this product', unique=True, max_length=10)),
                ('publish_after', models.DateField(help_text=b'We omit products from searches if there publish date is in the future', null=True, blank=True)),
                ('account_type', models.CharField(default=b'P', max_length=1, verbose_name=b'Account Type', choices=[(b'P', b'Personal'), (b'B', b'Business'), (b'C', b'Charity')])),
                ('minimum', models.IntegerField(default=0, null=True, verbose_name=b'Minimum Deposit', blank=True)),
                ('maximum', models.IntegerField(default=0, null=True, verbose_name=b'Maximum Deposit', blank=True)),
                ('minimum_monthly', models.IntegerField(default=0, null=True, blank=True)),
                ('maximum_monthly', models.IntegerField(default=0, null=True, blank=True)),
                ('aer', models.DecimalField(null=True, max_digits=7, decimal_places=4, blank=True)),
                ('gross_rate', models.DecimalField(null=True, max_digits=7, decimal_places=4, blank=True)),
                ('monthly_gross', models.DecimalField(null=True, max_digits=7, decimal_places=4, blank=True)),
                ('net_20', models.DecimalField(null=True, max_digits=7, decimal_places=4, blank=True)),
                ('net_40', models.DecimalField(null=True, max_digits=7, decimal_places=4, blank=True)),
                ('ratetracker_type', models.CharField(max_length=200, null=True, blank=True)),
                ('is_internet_access', models.BooleanField(default=False, verbose_name=b'Internet Access')),
                ('is_phone_access', models.BooleanField(default=False, verbose_name=b'Telephone Access')),
                ('is_post_access', models.BooleanField(default=False, verbose_name=b'Post Access')),
                ('is_branch_access', models.BooleanField(default=False, verbose_name=b'Branch Access')),
                ('is_cc_access', models.BooleanField(default=False, verbose_name=b'Cash Card Access')),
                ('is_open_internet', models.BooleanField(default=False, verbose_name=b'Can it be opened via the internet')),
                ('is_open_telephone', models.BooleanField(default=False, verbose_name=b'Can it be opened via the phone')),
                ('is_open_post', models.BooleanField(default=False, verbose_name=b'Can it be opened through the post')),
                ('is_open_branch', models.BooleanField(default=False, verbose_name=b'Can it be opened through a branch')),
                ('is_open_cc', models.BooleanField(default=False, verbose_name=b'Cash Card')),
                ('is_isa_transfers_in', models.BooleanField(default=False, verbose_name=b'Transfer ISAs in')),
                ('withdrawals', models.CharField(max_length=1000, null=True, blank=True)),
                ('term', models.IntegerField(default=0)),
                ('facts', models.TextField(default=b'')),
                ('fscs_licence', models.CharField(max_length=1000, null=True, blank=True)),
                ('is_sc_stamp', models.BooleanField(default=False)),
                ('is_paid', models.BooleanField(default=False)),
                ('minimum_age', models.IntegerField(default=0, null=True, blank=True)),
                ('maximum_age', models.IntegerField(default=0, null=True, blank=True)),
                ('bbrating_easyaccess', models.IntegerField(default=0, null=True, verbose_name=b'Easy Access Best Buy Rating', blank=True)),
                ('bbrating_fixedrate_bonds', models.IntegerField(default=0, null=True, verbose_name=b'Fixed Rate Bonds Best Buy Rating', blank=True)),
                ('bbrating_variable_isa', models.IntegerField(default=0, null=True, verbose_name=b'Variable ISA Best Buy Rating', blank=True)),
                ('bbrating_fixed_isa', models.IntegerField(default=0, null=True, verbose_name=b'Fixed ISA Best Buy Rating', blank=True)),
                ('bbrating_notice', models.IntegerField(default=0, null=True, verbose_name=b'Notice Accounts Best Buy Rating', blank=True)),
                ('bbrating_over50', models.IntegerField(default=0, null=True, verbose_name=b'Over 50s Best Buy Rating', blank=True)),
                ('bbrating_monthly_income', models.IntegerField(default=0, null=True, verbose_name=b'Monthly Income Best Buy Rating', blank=True)),
                ('bbrating_regularsavings', models.IntegerField(default=0, null=True, verbose_name=b'Regular Savings Best Buy Rating', blank=True)),
                ('bbrating_childrenssavings', models.IntegerField(default=0, null=True, verbose_name=b'Children Savings Best Buy Rating', blank=True)),
                ('bbrating_variable_bond', models.IntegerField(default=0, null=True, verbose_name=b'Variable Bonds Best Buy Rating', blank=True)),
                ('bbrating_highinterestcurrentaccount', models.IntegerField(default=0, null=True, verbose_name=b'High Interest Current Account Best Buy Rating', blank=True)),
                ('bonus_amount', models.DecimalField(default=0, max_digits=7, decimal_places=4)),
                ('bonus_term', models.IntegerField(default=0)),
                ('bonus_end_date', models.DateField(null=True, blank=True)),
                ('underlying_gross_rate', models.DecimalField(default=0, max_digits=7, decimal_places=4)),
                ('notice', models.IntegerField(default=0, null=True, blank=True)),
                ('url', models.URLField(max_length=300, null=True, blank=True)),
                ('sf_product_id', models.CharField(max_length=255, null=True, blank=True)),
                ('is_fixed', models.BooleanField(default=False)),
                ('verdict', models.TextField(null=True, blank=True)),
                ('bestbuy_type', models.ManyToManyField(related_name='bestbuy_products', null=True, to=b'products.BestBuy', blank=True)),
                ('master_product', models.ForeignKey(related_name='master_product', blank=True, to='products.MasterProduct', null=True)),
            ],
            options={
                'get_latest_by': 'publish_after',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProductClickthrough',
            fields=[
                ('uuid', django_extensions.db.fields.UUIDField(serialize=False, editable=False, primary_key=True, blank=True)),
                ('count', models.IntegerField(default=0)),
                ('product', models.ForeignKey(to='products.Product')),
                ('referer', models.ForeignKey(blank=True, to='common.Referrer', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProductPortfolio',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('balance', models.DecimalField(null=True, max_digits=10, decimal_places=2)),
                ('is_deleted', models.BooleanField(default=False)),
                ('created_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('is_synched', models.NullBooleanField(default=False)),
                ('opening_date', models.DateField(null=True, blank=True)),
                ('bonus_term', models.IntegerField(null=True, blank=True)),
                ('notice', models.IntegerField(null=True, blank=True)),
                ('account_type', models.ForeignKey(to='products.BestBuy')),
                ('product', models.ForeignKey(to='products.Product')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProductTier',
            fields=[
                ('title', models.CharField(max_length=200)),
                ('slug', models.CharField(help_text=b'The slug is a url encoded version of your title and is used to create the web address', max_length=200)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.BooleanField(default=False)),
                ('uuid', django_extensions.db.fields.UUIDField(serialize=False, editable=False, primary_key=True, blank=True)),
                ('sc_code', models.CharField(help_text=b'This is Savings Champion unique identifier for this product', unique=True, max_length=10)),
                ('publish_after', models.DateField(help_text=b'We omit products from searches if their publish date is in the future', null=True, blank=True)),
                ('available_until', models.DateField(help_text=b"This product tier couldn't be opened past this date.", null=True, blank=True)),
                ('account_type', models.CharField(default=b'P', max_length=1, verbose_name=b'Account Type', choices=[(b'P', b'Personal'), (b'B', b'Business'), (b'C', b'Charity')])),
                ('minimum', models.IntegerField(default=0, null=True, verbose_name=b'Minimum Deposit', blank=True)),
                ('maximum', models.IntegerField(default=0, null=True, verbose_name=b'Maximum Deposit', blank=True)),
                ('minimum_monthly', models.IntegerField(default=0, null=True, blank=True)),
                ('maximum_monthly', models.IntegerField(default=0, null=True, blank=True)),
                ('aer', models.DecimalField(default=0, max_digits=7, decimal_places=4, blank=True)),
                ('gross_rate', models.DecimalField(default=0, max_digits=7, decimal_places=4)),
                ('monthly_gross', models.DecimalField(default=0, max_digits=7, decimal_places=4, blank=True)),
                ('net_20', models.DecimalField(default=0, max_digits=7, decimal_places=4, blank=True)),
                ('net_40', models.DecimalField(default=0, max_digits=7, decimal_places=4, blank=True)),
                ('ratetracker_type', models.TextField(null=True, blank=True)),
                ('is_internet_access', models.BooleanField(default=False, verbose_name=b'Internet Access')),
                ('is_phone_access', models.BooleanField(default=False, verbose_name=b'Telephone Access')),
                ('is_post_access', models.BooleanField(default=False, verbose_name=b'Post Access')),
                ('is_branch_access', models.BooleanField(default=False, verbose_name=b'Branch Access')),
                ('is_cc_access', models.BooleanField(default=False, verbose_name=b'Cash Card Access')),
                ('is_open_internet', models.BooleanField(default=False, verbose_name=b'Can it be opened via the internet')),
                ('is_open_telephone', models.BooleanField(default=False, verbose_name=b'Can it be opened via the phone')),
                ('is_open_post', models.BooleanField(default=False, verbose_name=b'Can it be opened through the post')),
                ('is_open_branch', models.BooleanField(default=False, verbose_name=b'Can it be opened through a branch')),
                ('is_open_cc', models.BooleanField(default=False, verbose_name=b'Cash Card')),
                ('is_isa_transfers_in', models.BooleanField(default=False, verbose_name=b'Transfer ISAs in')),
                ('withdrawals', models.TextField(null=True, blank=True)),
                ('facts', models.TextField(null=True, blank=True)),
                ('fscs_licence', models.TextField(null=True, blank=True)),
                ('is_sc_stamp', models.BooleanField(default=False)),
                ('is_paid', models.BooleanField(default=False)),
                ('bbrating_easyaccess', models.IntegerField(default=0, null=True, verbose_name=b'Easy Access Best Buy Rating', blank=True)),
                ('bbrating_fixedrate_bonds', models.IntegerField(default=0, null=True, verbose_name=b'Fixed Rate Bonds Best Buy Rating', blank=True)),
                ('bbrating_variable_isa', models.IntegerField(default=0, null=True, verbose_name=b'Variable ISA Best Buy Rating', blank=True)),
                ('bbrating_fixed_isa', models.IntegerField(default=0, null=True, verbose_name=b'Fixed ISA Best Buy Rating', blank=True)),
                ('bbrating_notice', models.IntegerField(default=0, null=True, verbose_name=b'Notice Accounts Best Buy Rating', blank=True)),
                ('bbrating_over50', models.IntegerField(default=0, null=True, verbose_name=b'Over 50s Best Buy Rating', blank=True)),
                ('bbrating_monthly_income', models.IntegerField(default=0, null=True, verbose_name=b'Monthly Income Best Buy Rating', blank=True)),
                ('bbrating_regularsavings', models.IntegerField(default=0, null=True, verbose_name=b'Regular Savings Best Buy Rating', blank=True)),
                ('bbrating_childrenssavings', models.IntegerField(default=0, null=True, verbose_name=b'Children Savings Best Buy Rating', blank=True)),
                ('bbrating_variable_bond', models.IntegerField(default=0, null=True, verbose_name=b'Variable Bonds Best Buy Rating', blank=True)),
                ('bbrating_highinterestcurrentaccount', models.IntegerField(default=0, null=True, verbose_name=b'High Interest Current Account Best Buy Rating', blank=True)),
                ('status', models.CharField(max_length=20, null=True, blank=True)),
                ('bonus_amount', models.DecimalField(null=True, max_digits=7, decimal_places=4, blank=True)),
                ('bonus_term', models.IntegerField(null=True, blank=True)),
                ('bonus_end_date', models.DateField(null=True, blank=True)),
                ('underlying_gross_rate', models.DecimalField(null=True, max_digits=7, decimal_places=4, blank=True)),
                ('url', models.URLField(max_length=300, null=True, blank=True)),
                ('sf_product_tier_id', models.CharField(unique=True, max_length=255)),
                ('is_fixed', models.BooleanField(default=False)),
                ('verdict', models.TextField(null=True, blank=True)),
                ('joint_account_only', models.BooleanField(default=False)),
                ('tier_type', models.TextField(default=b'', blank=True)),
                ('product', models.ForeignKey(blank=True, to='products.MasterProduct', null=True)),
            ],
            options={
                'get_latest_by': 'publish_after',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Provider',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(unique=True, max_length=200)),
                ('slug', models.CharField(help_text=b'The slug is a url encoded version of your title and is used to create the web address', max_length=200)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.BooleanField(default=False)),
                ('logo', models.ImageField(help_text=b'The logo will appear alongside the product information on the best buy tables', upload_to=b'logos')),
                ('fscs_parent', models.CharField(help_text=b'Please enter this all as one word, for example: RoyalBankOfScotland', max_length=255, null=True, blank=True)),
                ('fscs_licence_holder', models.TextField(null=True)),
                ('ethical', models.BooleanField(default=False)),
                ('ethical_rating', models.TextField(default=b'', null=True, blank=True)),
                ('moodys_rating', models.CharField(blank=True, max_length=4, null=True, choices=[(None, b'None'), (b'A1', b'Obligations rated A are considered upper-medium grade and are subject to low credit risk'), (b'A2', b'Obligations rated A are considered upper-medium grade and are subject to low credit risk'), (b'A3', b'Obligations rated A are considered upper-medium grade and are subject to low credit risk'), (b'Aa1', b'Obligations rated Aa are judged to be of high quality and are subject to very low credit risk'), (b'Aa2', b'Obligations rated Aa are judged to be of high quality and are subject to very low credit risk'), (b'Aa3', b'Obligations rated Aa are judged to be of high quality and are subject to very low credit risk'), (b'Aaa1', b'Obligations rated Aaa are judged to be of the highest quality, with minimal credit risk.'), (b'Aaa2', b'Obligations rated Aaa are judged to be of the highest quality, with minimal credit risk.'), (b'Aaa3', b'Obligations rated Aaa are judged to be of the highest quality, with minimal credit risk.'), (b'B1', b'Obligations rated B are considered speculative and are subject to high credit risk.'), (b'B2', b'Obligations rated B are considered speculative and are subject to high credit risk.'), (b'B3', b'Obligations rated B are considered speculative and are subject to high credit risk.'), (b'Ba1', b'Obligations rated Ba are judged to have speculative elements and are subject to substantial credit risk.'), (b'Ba2', b'Obligations rated Ba are judged to have speculative elements and are subject to substantial credit risk.'), (b'Ba3', b'Obligations rated Ba are judged to have speculative elements and are subject to substantial credit risk.'), (b'Baa1', b'Obligations rated Baa are subject to moderate credit risk. They are considered medium-grade and as such may possess certain speculative characteristics.'), (b'Baa2', b'Obligations rated Baa are subject to moderate credit risk. They are considered medium-grade and as such may possess certain speculative characteristics.'), (b'Baa3', b'Obligations rated Baa are subject to moderate credit risk. They are considered medium-grade and as such may possess certain speculative characteristics.'), (b'C1', b'Obligations rated C are the lowest rated class of bonds and are typically in default, with little prospect for recovery of principal or interest.'), (b'C2', b'Obligations rated C are the lowest rated class of bonds and are typically in default, with little prospect for recovery of principal or interest.'), (b'C3', b'Obligations rated C are the lowest rated class of bonds and are typically in default, with little prospect for recovery of principal or interest.'), (b'Ca1', b'Obligations rated Ca are highly speculative and are likely in, or very near, default, with some prospect of recovery of principal and interest.'), (b'Ca2', b'Obligations rated Ca are highly speculative and are likely in, or very near, default, with some prospect of recovery of principal and interest.'), (b'Ca3', b'Obligations rated Ca are highly speculative and are likely in, or very near, default, with some prospect of recovery of principal and interest.'), (b'Caa1', b'Obligations rated Caa are judged to be of poor standing and are subject to very high credit risk.'), (b'Caa2', b'Obligations rated Caa are judged to be of poor standing and are subject to very high credit risk.'), (b'Caa3', b'Obligations rated Caa are judged to be of poor standing and are subject to very high credit risk.')])),
                ('fitchs_rating', models.CharField(default=0, max_length=4, null=True, blank=True, choices=[(0, b'None'), (b'A+', b'A+'), (b'A', b'A'), (b'B', b'B'), (b'C', b'C')])),
                ('building_society', models.BooleanField(default=False)),
                ('mutual', models.BooleanField(default=False)),
                ('bank', models.BooleanField(default=False)),
                ('high_street', models.BooleanField(default=False)),
                ('phone', models.TextField(default=b'', null=True, blank=True)),
                ('website', models.URLField(default=b'', null=True, blank=True)),
                ('meets_service_standard', models.BooleanField(default=True)),
                ('reason_to_exclude', models.TextField(default=b'', null=True, blank=True)),
                ('compliance_checked', models.BooleanField(default=False)),
                ('sf_provider_id', models.TextField(unique=True, null=True)),
                ('isa_topup_2014', models.BooleanField(default=False)),
                ('isa_topup_2014_conditions', models.TextField(default=b'', blank=True)),
                ('isa_topup_2014_email_list', models.TextField(default=b'', blank=True)),
                ('provider_maximum', models.DecimalField(default=0, max_digits=18, decimal_places=2)),
                ('fscs_limit_type', models.ForeignKey(to='products.FSCSLimitType', null=True)),
            ],
            options={
                'ordering': ('title',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProviderBestBuy',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('bestbuys', models.ManyToManyField(to=b'products.BestBuy')),
                ('provider', models.ForeignKey(to='products.Provider')),
            ],
            options={
                'ordering': ('provider__title',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProviderContacts',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', models.TextField(default=b'')),
                ('last_name', models.TextField(default=b'')),
                ('title', models.TextField(default=b'')),
                ('email', models.EmailField(default=b'', max_length=75)),
                ('office_phone', models.TextField(default=b'')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProviderSpecificFields',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('field_name', models.TextField(default=b'')),
                ('provider', models.ForeignKey(to='products.Provider')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Ranking',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('rank', models.IntegerField(null=True, blank=True)),
                ('hidden', models.BooleanField(default=False)),
                ('bestbuy', models.ForeignKey(to='products.BestBuy')),
                ('product', models.ForeignKey(related_name='link_to_products', to='products.Product')),
            ],
            options={
                'ordering': ('bestbuy__title', 'rank'),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RatetrackerReminder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('balance', models.DecimalField(null=True, max_digits=10, decimal_places=2)),
                ('is_deleted', models.BooleanField(default=False)),
                ('created_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('is_synched', models.NullBooleanField(default=False)),
                ('maturity_date', models.DateField()),
                ('rate', models.DecimalField(default=0, max_digits=18, decimal_places=4)),
                ('fee_exempt', models.BooleanField(default=True)),
                ('term', models.IntegerField(default=0)),
                ('pool_altered', models.BooleanField(default=False)),
                ('account_type', models.ForeignKey(to='products.BestBuy')),
                ('provider', models.ForeignKey(to='products.Provider')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TrustTypes',
            fields=[
                ('uuid', django_extensions.db.fields.UUIDField(serialize=False, editable=False, primary_key=True, blank=True)),
                ('title', models.TextField(default=b'')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='WeeklyRateAlert',
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
        migrations.AddField(
            model_name='producttier',
            name='provider',
            field=models.ForeignKey(related_name='product_tiers', to='products.Provider'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='productportfolio',
            name='provider',
            field=models.ForeignKey(to='products.Provider'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='productportfolio',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='product',
            name='provider',
            field=models.ForeignKey(related_name='products', to='products.Provider'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='product',
            name='user',
            field=models.ManyToManyField(related_name='portfolio_products', through='products.ProductPortfolio', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='masterproduct',
            name='provider',
            field=models.ForeignKey(related_name='master_products', blank=True, to='products.Provider', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='masterproduct',
            name='trust_types_excluded',
            field=models.ManyToManyField(to=b'products.TrustTypes'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bestbuy',
            name='products',
            field=models.ManyToManyField(to=b'products.Product', through='products.Ranking'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='advantagesblock',
            name='bestbuy',
            field=models.ForeignKey(to='products.BestBuy'),
            preserve_default=True,
        ),
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
        migrations.RemoveField(
            model_name='producttier',
            name='account_type',
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
        migrations.AlterModelOptions(
            name='ranking',
            options={'ordering': ('-date_created', 'bestbuy__title', 'rank')},
        ),
        migrations.AddField(
            model_name='ranking',
            name='date_created',
            field=models.DateTimeField(default=datetime.datetime.now, auto_now_add=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ranking',
            name='date_replaced',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='masterproduct',
            name='other_reason_to_exclude_this_product',
            field=models.TextField(default=b'', blank=True),
            preserve_default=True,
        ),
        migrations.AlterModelOptions(
            name='ranking',
            options={'ordering': ('bestbuy__title', 'rank')},
        ),
        migrations.AddField(
            model_name='product',
            name='_facts_rendered',
            field=models.TextField(default='', editable=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='product',
            name='facts_markup_type',
            field=models.CharField(default=b'markdown', max_length=30, editable=False, choices=[(b'', b'--'), (b'markdown', b'markdown')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='bestbuy',
            name='title',
            field=models.CharField(max_length=200, choices=[(b'High Interest Current Accounts', b'High Interest Current Accounts'), (b'Current Accounts', b'High Interest Current Accounts'), (b'Easy Access', b'Easy Access'), (b'Fixed Rate Bonds', b'Fixed Rate Bonds'), (b'Variable Rate ISAs', b'Variable Rate ISAs'), (b'Fixed Rate ISAs', b'Fixed Rate ISAs'), (b'Notice Accounts', b'Notice Accounts'), (b'Monthly Income', b'Monthly Income'), (b'Regular Savings', b'Regular Savings'), (b"Children's Accounts", b"Children's Accounts"), (b'Junior ISA', b'Junior ISA'), (b'Index Linked Certificate', b'Index Linked Certificate'), (b'Variable Rate Bond', b'Variable Rate Bond')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='product',
            name='facts',
            field=markupfield.fields.MarkupField(default=b'', rendered_field=True),
            preserve_default=True,
        ),
        migrations.AlterModelOptions(
            name='ranking',
            options={'ordering': ('-date_created', 'bestbuy__title', 'term', 'rank')},
        ),
        migrations.AddField(
            model_name='ranking',
            name='term',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, b'No Term'), (1, b'up to 1 Year'), (2, b'1-2 Years'), (3, b'2-3 Years'), (4, b'3-4 Years'), (5, b'5 Years and over')]),
            preserve_default=True,
        ),
        migrations.AlterModelOptions(
            name='ranking',
            options={'ordering': ('bestbuy__title', 'term', 'rank', '-date_replaced')},
        ),
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
        migrations.AlterUniqueTogether(
            name='ranking',
            unique_together=set([('product', 'bestbuy', 'date_replaced')]),
        ),
        migrations.RemoveField(
            model_name='producttier',
            name='status',
        ),
        migrations.AddField(
            model_name='masterproduct',
            name='exclude_from_api_for',
            field=models.ManyToManyField(to=b'v1.ApiExcludedItem', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='product',
            name='exclude_from_api_for',
            field=models.ManyToManyField(to=b'v1.ApiExcludedItem', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='producttier',
            name='exclude_from_api_for',
            field=models.ManyToManyField(to=b'v1.ApiExcludedItem', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='provider',
            name='exclude_from_api_for',
            field=models.ManyToManyField(to=b'v1.ApiExcludedItem', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='masterproduct',
            name='status',
            field=models.CharField(default=b'Default', max_length=20),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='ranking',
            unique_together=set([('rank', 'term', 'bestbuy', 'date_replaced'), ('product', 'bestbuy', 'date_replaced')]),
        ),
        migrations.RemoveField(
            model_name='product',
            name='verdict',
        ),
        migrations.AddField(
            model_name='masterproduct',
            name='verdict',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='masterproduct',
            name='url',
            field=models.URLField(max_length=300, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.RunPython(
            code=move_data_16,
            reverse_code=None,
            atomic=True,
        ),
        migrations.RunPython(
            code=move_data_17,
            reverse_code=None,
            atomic=True,
        ),
        migrations.RemoveField(
            model_name='product',
            name='fscs_licence',
        ),
        migrations.RemoveField(
            model_name='product',
            name='url',
        ),
        migrations.AddField(
            model_name='bestbuy',
            name='is_isa',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='masterproduct',
            name='maximum_monthly',
            field=models.DecimalField(default=0, max_digits=18, decimal_places=3, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='masterproduct',
            name='minimum_monthly',
            field=models.DecimalField(default=0, max_digits=18, decimal_places=3, blank=True),
            preserve_default=True,
        ),
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
        migrations.RunPython(
            code=resave_facts,
            reverse_code=None,
            atomic=True,
        ),
        migrations.RemoveField(
            model_name='product',
            name='_facts_rendered',
        ),
        migrations.RemoveField(
            model_name='product',
            name='facts',
        ),
        migrations.RemoveField(
            model_name='product',
            name='facts_markup_type',
        ),
        migrations.RemoveField(
            model_name='producttier',
            name='facts',
        ),
        migrations.AddField(
            model_name='masterproduct',
            name='is_paid',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.RunPython(
            code=migrate_is_paid_data,
            reverse_code=None,
            atomic=True,
        ),
        migrations.RemoveField(
            model_name='product',
            name='is_paid',
        ),
        migrations.AlterField(
            model_name='masterproduct',
            name='is_paid',
            field=models.NullBooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='producttier',
            name='split_interest',
            field=models.NullBooleanField(default=False),
            preserve_default=True,
        ),
        migrations.RunPython(
            code=migrate_old_products_onto_newer_salesforce_ids,
            reverse_code=None,
            atomic=True,
        ),
        migrations.AddField(
            model_name='masterproduct',
            name='bonus_end_date',
            field=models.DateField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='masterproduct',
            name='bonus_term',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.RunPython(
            code=migrate_old_bonus_info_to_master_product,
            reverse_code=None,
            atomic=True,
        ),
        migrations.RemoveField(
            model_name='product',
            name='bonus_end_date',
        ),
        migrations.RemoveField(
            model_name='product',
            name='bonus_term',
        ),
        migrations.RemoveField(
            model_name='producttier',
            name='bonus_end_date',
        ),
        migrations.RemoveField(
            model_name='producttier',
            name='bonus_term',
        ),
        migrations.AlterField(
            model_name='producttier',
            name='underlying_gross_rate',
            field=models.DecimalField(default=0, max_digits=7, decimal_places=4),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='fscslimittype',
            name='balance_limit',
            field=models.DecimalField(default=0, max_digits=19, decimal_places=3),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='fscslimittype',
            name='currency_code',
            field=models.TextField(default=b'GBP'),
            preserve_default=True,
        ),
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
                ('source', models.ForeignKey(to='common.Referrer', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='bestbuy',
            name='title',
            field=models.CharField(max_length=200, choices=[(b'High Interest Current Accounts', b'High Interest Current Accounts'), (b'Current Accounts', b'High Interest Current Accounts'), (b'Easy Access', b'Easy Access'), (b'Fixed Rate Bonds', b'Fixed Rate Bonds'), (b'Variable Rate ISAs', b'Variable Rate ISAs'), (b'Fixed Rate ISAs', b'Fixed Rate ISAs'), (b'Notice Accounts', b'Notice Accounts'), (b'Monthly Income', b'Monthly Income'), (b'Regular Savings', b'Regular Savings'), (b"Children's Accounts", b"Children's Accounts"), (b'Junior ISA', b'Junior ISA'), (b'Index Linked Certificate', b'Index Linked Certificate'), (b'Variable Rate Bond', b'Variable Rate Bond'), (b'Sharia Accounts', b'Sharia Accounts')]),
            preserve_default=True,
        ),
        migrations.RemoveField(
            model_name='product',
            name='is_branch_access',
        ),
        migrations.RemoveField(
            model_name='product',
            name='is_cc_access',
        ),
        migrations.RemoveField(
            model_name='product',
            name='is_internet_access',
        ),
        migrations.RemoveField(
            model_name='product',
            name='is_open_branch',
        ),
        migrations.RemoveField(
            model_name='product',
            name='is_open_cc',
        ),
        migrations.RemoveField(
            model_name='product',
            name='is_open_internet',
        ),
        migrations.RemoveField(
            model_name='product',
            name='is_open_post',
        ),
        migrations.RemoveField(
            model_name='product',
            name='is_open_telephone',
        ),
        migrations.RemoveField(
            model_name='product',
            name='is_phone_access',
        ),
        migrations.RemoveField(
            model_name='product',
            name='is_post_access',
        ),
    ]

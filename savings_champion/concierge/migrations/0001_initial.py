# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AdviserQueue',
            fields=[
                ('uuid', django_extensions.db.fields.UUIDField(serialize=False, editable=False, primary_key=True, blank=True)),
                ('name', models.TextField(default=b'')),
                ('email', models.EmailField(unique=True, max_length=75)),
                ('telephone', models.TextField(default=b'')),
                ('preferred_contact_time', models.TextField(default=b'Anytime', choices=[(b'Anytime', b'Anytime (9-5 weekdays)'), (b'Morning', b'Morning (9-12 weekdays)'), (b'Afternoon', b'Afternoon (12-5 weekdays)')])),
                ('source', models.TextField(default=b'', choices=[(b'', b''), (b'7 Pitfalls', b'7 Pitfalls'), (b'Video 0.1%', b'Video 0.1%'), (b'Video', b'Video'), (b'Basket', b'Basket'), (b'Basket (Concierge)', b'Basket (Concierge)'), (b'Basket (Healthcheck)', b'Basket (Healthcheck)'), (b'Basket (Healthcheck and Concierge)', b'Basket (Healthcheck and Concierge)'), (b'Rate Tracker > 100K', b'Rate Tracker > 100K'), (b'Inbound Call', b'Inbound Call'), (b'Referral', b'Referral'), (b'Trust', b'Trust Concierge'), (b'Trust Concierge', b'Trust Concierge'), (b'Charity Concierge', b'Charity Concierge'), (b'Business Concierge', b'Business Concierge'), (b'Intermediary', b'Intermediary'), (b'50 Pound Challenge', b'50 Pound Challenge'), (b'Product Questionnaire', b'Product Questionnaire'), (b'The Biggest Mistake', b'The Biggest Mistake'), (b'The Value Of Advice', b'The Value Of Advice')])),
                ('status', models.PositiveSmallIntegerField(default=0, choices=[(0, b'Pending Contact'), (1, b'Contacted'), (2, b'Fake details'), (3, b'Fact Find 1'), (4, b'Illustration'), (5, b'No Contact'), (6, b'No Contact 2'), (7, b'No Contact 3'), (8, b'Unsuitable'), (9, b'Signed Up'), (10, b'Emailed'), (11, b'Recommendation')])),
                ('interaction_started', models.DateTimeField(auto_now_add=True)),
                ('interaction_ended', models.DateTimeField(auto_now=True)),
                ('fee', models.DecimalField(default=0, max_digits=14, decimal_places=3)),
                ('portfolio_value', models.DecimalField(default=0, max_digits=14, decimal_places=3)),
                ('unsuitable_reason', models.TextField(default=b'')),
            ],
            options={
                'ordering': ['status'],
                'permissions': (('adviser', 'Is a savings adviser'), ('manage_advisers', 'Can manage savings advisers')),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AdviserQueueHistory',
            fields=[
                ('uuid', django_extensions.db.fields.UUIDField(serialize=False, editable=False, primary_key=True, blank=True)),
                ('status', models.PositiveSmallIntegerField(default=0, choices=[(0, b'Pending Contact'), (1, b'Contacted'), (2, b'Fake details'), (3, b'Fact Find 1'), (4, b'Illustration'), (5, b'No Contact'), (6, b'No Contact 2'), (7, b'No Contact 3'), (8, b'Unsuitable'), (9, b'Signed Up'), (10, b'Emailed'), (11, b'Recommendation')])),
                ('source', models.TextField(default=b'', choices=[(b'', b''), (b'7 Pitfalls', b'7 Pitfalls'), (b'Video 0.1%', b'Video 0.1%'), (b'Video', b'Video'), (b'Basket', b'Basket'), (b'Basket (Concierge)', b'Basket (Concierge)'), (b'Basket (Healthcheck)', b'Basket (Healthcheck)'), (b'Basket (Healthcheck and Concierge)', b'Basket (Healthcheck and Concierge)'), (b'Rate Tracker > 100K', b'Rate Tracker > 100K'), (b'Inbound Call', b'Inbound Call'), (b'Referral', b'Referral'), (b'Trust', b'Trust Concierge'), (b'Trust Concierge', b'Trust Concierge'), (b'Charity Concierge', b'Charity Concierge'), (b'Business Concierge', b'Business Concierge'), (b'Intermediary', b'Intermediary'), (b'50 Pound Challenge', b'50 Pound Challenge'), (b'Product Questionnaire', b'Product Questionnaire'), (b'The Biggest Mistake', b'The Biggest Mistake'), (b'The Value Of Advice', b'The Value Of Advice')])),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('fee', models.DecimalField(default=0, max_digits=5, decimal_places=4)),
                ('portfolio_value', models.DecimalField(default=0, max_digits=14, decimal_places=3)),
                ('unsuitable_reason', models.TextField(default=b'')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ConciergeLeadCapture',
            fields=[
                ('uuid', django_extensions.db.fields.UUIDField(serialize=False, editable=False, primary_key=True, blank=True)),
                ('title', models.CharField(max_length=10)),
                ('first_name', models.TextField()),
                ('middle_names', models.TextField(null=True, blank=True)),
                ('last_name', models.TextField()),
                ('maiden_name', models.TextField(default=b'', null=True, blank=True)),
                ('mothers_maiden_name', models.TextField()),
                ('date_of_birth', models.DateField(default=datetime.datetime.today)),
                ('place_of_birth', models.TextField()),
                ('address', models.TextField()),
                ('postcode', models.TextField()),
                ('date_moved_in', models.DateField(default=datetime.datetime.today)),
                ('country_of_residence', models.TextField()),
                ('uk_resident', models.BooleanField(default=False)),
                ('tax_band', models.CharField(default=b'b', max_length=2, choices=[(b'n', b'Non Taxpayer'), (b'b', b'Basic Rate'), (b'h', b'Higher Rate'), (b'a', b'Additional Rate')])),
                ('required_gross_interest', models.IntegerField(default=0)),
                ('previous_address', models.TextField()),
                ('months_at_previous_address', models.IntegerField(default=0)),
                ('national_insurance_number', models.CharField(max_length=255)),
                ('passport_number', models.CharField(max_length=255)),
                ('passport_expiry_date', models.DateField(default=datetime.datetime.today)),
                ('passport_issue_date', models.DateField(default=datetime.datetime.today)),
                ('home_tel_number', models.CharField(max_length=255)),
                ('daytime_tel_number', models.CharField(max_length=255, null=True, blank=True)),
                ('mobile', models.CharField(max_length=255, null=True, blank=True)),
                ('email', models.EmailField(max_length=75)),
                ('ratetracker_email', models.EmailField(max_length=75)),
                ('occupation', models.CharField(max_length=255)),
                ('employment_status', models.CharField(max_length=255)),
                ('type_of_employment', models.CharField(max_length=10, choices=[(b'full_time', b'Full Time'), (b'part_time', b'Part Time')])),
                ('marital_status', models.CharField(max_length=255)),
                ('account_holders_name', models.CharField(max_length=255)),
                ('bank_name', models.CharField(max_length=255)),
                ('bank_sort_code', models.CharField(max_length=255)),
                ('bank_account_number', models.CharField(max_length=255)),
                ('bank_address', models.TextField()),
                ('source_of_assets', models.TextField()),
                ('interest_payment_options', models.CharField(max_length=4, choices=[(b'add', b'Add to accounts'), (b'move', b'Moved to another account')])),
                ('interest_payment_frequency', models.CharField(max_length=10, choices=[(b'monthly', b'Monthly'), (b'annually', b'Annually')])),
                ('joint_account_authority', models.CharField(max_length=10, choices=[(b'client1', b'Client1 Only'), (b'client2', b'Client2 Only'), (b'either', b'Either Client'), (b'both', b'Both Clients')])),
                ('contact_providers_allowed', models.BooleanField(default=False)),
                ('temporary_credentials_allowed', models.BooleanField(default=False)),
                ('agree_terms_allowed', models.BooleanField(default=False)),
                ('large_print', models.BooleanField(default=False)),
                ('marketing_allowed', models.BooleanField(default=False)),
                ('notes', models.TextField(null=True, blank=True)),
                ('named_user', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ConciergeProviderAccountTypeLimitation',
            fields=[
                ('uuid', django_extensions.db.fields.UUIDField(serialize=False, editable=False, primary_key=True, blank=True)),
                ('maximum_balance', models.DecimalField(default=0, max_digits=18, decimal_places=3)),
            ],
            options={
                'verbose_name': 'ConciergeProviderAccountTypeLimit',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ConciergeUserAcceptedProduct',
            fields=[
                ('uuid', django_extensions.db.fields.UUIDField(serialize=False, editable=False, primary_key=True, blank=True)),
                ('restriction', models.TextField(choices=[(b'open_branch', b'Allowed opening this product in branch'), (b'open_telephone', b'Allowed opening this product via telephone'), (b'open_internet', b'Allowed opening this product in internet'), (b'open_branch', b'Allowed opening this product in post'), (b'access_post', b'Allowed opening this product in branch'), (b'access_telephone', b'Allowed opening this product via telephone'), (b'access_internet', b'Allowed opening this product in internet'), (b'access_post', b'Allowed opening this product in post'), (b'existing', b'Allowed opening this product as user is an existing member'), (b'locals', b'Allowed opening this product as user is a local'), (b'sharia', b"Allowed opening this Sharia'a product"), (b'joint_account', b'Allowed opening this product as a joint account'), (b'current_account', b'Allowed opening this product as a current account'), (b'provider_maximum', b'Allowed to open more of this product by provider'), (b'opening_threshold', b'Allowed opening this product under the users minimum threshold'), (b'other_reason', b'Allowed opening this product despite other reasons to exclude')])),
                ('accepted', models.BooleanField(default=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ConciergeUserLicenceRisk',
            fields=[
                ('uuid', django_extensions.db.fields.UUIDField(serialize=False, editable=False, primary_key=True, blank=True)),
                ('maximum_balance', models.DecimalField(default=0, max_digits=19, decimal_places=3)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ConciergeUserNotes',
            fields=[
                ('uuid', django_extensions.db.fields.UUIDField(serialize=False, editable=False, primary_key=True, blank=True)),
                ('note', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ConciergeUserOption',
            fields=[
                ('uuid', django_extensions.db.fields.UUIDField(serialize=False, editable=False, primary_key=True, blank=True)),
                ('birth_date', models.DateField(default=datetime.datetime(1900, 1, 1, 0, 0), null=True, verbose_name=b'To take advantage of age related accounts', blank=True)),
                ('business', models.BooleanField(default=False, verbose_name=b'I represent a business')),
                ('charity', models.BooleanField(default=False, verbose_name=b'I represent a charity')),
                ('child', models.BooleanField(default=False, verbose_name=b'I represent a child')),
                ('current_accounts', models.BooleanField(default=True, verbose_name=b'I am open to using current accounts')),
                ('ignore_fscs', models.BooleanField(default=False, verbose_name=b'I want to ignore FSCS Protection')),
                ('minimum_opening_balance', models.DecimalField(default=0, help_text=b"I will not automatically open an account under this balance (Doesn't affect pinned accounts)", max_digits=19, decimal_places=3)),
                ('maximum_opening_balance', models.DecimalField(default=0, help_text=b"I will not automatically open an account over this balance unless it's protected (Doesn't affect pinned accounts, overridden by provider risks)", max_digits=19, decimal_places=3)),
                ('no_lowest_rate', models.BooleanField(default=False, help_text=b'Debug option, Service will not give up once reaching the bottom lowest rate in their existing portfolio.')),
                ('existing_customer', models.BooleanField(default=True, verbose_name=b'I am an existing customer of a bank')),
                ('local_customer', models.BooleanField(default=True, verbose_name=b'I am interested in local members accounts')),
                ('shariaa', models.BooleanField(default=False, verbose_name=b'I am interested in products where the rate and capital is not guaranteed due to shariaa law')),
                ('open_post', models.BooleanField(default=True, verbose_name=b'Post')),
                ('open_internet', models.BooleanField(default=False, verbose_name=b'The Internet')),
                ('open_telephone', models.BooleanField(default=False, verbose_name=b'Telephone')),
                ('open_branch', models.BooleanField(default=False, verbose_name=b'Branch')),
                ('access_post', models.BooleanField(default=True, verbose_name=b'Post')),
                ('access_internet', models.BooleanField(default=False, verbose_name=b'The Internet')),
                ('access_telephone', models.BooleanField(default=False, verbose_name=b'Telephone')),
                ('access_branch', models.BooleanField(default=False, verbose_name=b'Branch')),
                ('use_existing_accounts', models.BooleanField(default=True, verbose_name=b'I would like to reuse my existing accounts')),
                ('monthly_interest', models.BooleanField(default=False, verbose_name=b'Monthly interest')),
                ('joint_name', models.BooleanField(default=False, verbose_name=b'To take advantage of joint accounts')),
                ('dual_portfolio', models.BooleanField(default=False, verbose_name=b'I represent two people')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ConciergeUserPool',
            fields=[
                ('uuid', django_extensions.db.fields.UUIDField(serialize=False, editable=False, primary_key=True, blank=True)),
                ('term', models.IntegerField(default=0, verbose_name=b'Maximum Term Length')),
                ('balance', models.DecimalField(default=0, verbose_name=b'Required Balance', max_digits=19, decimal_places=2)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ConciergeUserProviderRisk',
            fields=[
                ('uuid', django_extensions.db.fields.UUIDField(serialize=False, editable=False, primary_key=True, blank=True)),
                ('maximum_balance', models.DecimalField(default=0, max_digits=19, decimal_places=3)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ConciergeUserRemovedProduct',
            fields=[
                ('uuid', django_extensions.db.fields.UUIDField(serialize=False, editable=False, primary_key=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ConciergeUserRequiredProduct',
            fields=[
                ('uuid', django_extensions.db.fields.UUIDField(serialize=False, editable=False, primary_key=True, blank=True)),
                ('balance', models.DecimalField(default=0, max_digits=19, decimal_places=3)),
                ('concierge_user', models.ForeignKey(to='concierge.ConciergeUserOption')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EmailTemplate',
            fields=[
                ('uuid', django_extensions.db.fields.UUIDField(serialize=False, editable=False, primary_key=True, blank=True)),
                ('title', models.TextField(default=b'', unique=True)),
                ('body', models.TextField(default=b'')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]

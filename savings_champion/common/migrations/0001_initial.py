# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AuthorProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField(blank=True)),
                ('linked_in_url', models.URLField(null=True, blank=True)),
                ('twitter_url', models.URLField(null=True, blank=True)),
                ('watercolor_image', models.ImageField(null=True, upload_to=b'biographies/', blank=True)),
                ('small_image', models.ImageField(null=True, upload_to=b'biographies/', blank=True)),
                ('biography', models.TextField(help_text=b'The description will be added to the Biography page', null=True, verbose_name=b'Biography Content', blank=True)),
                ('user', models.OneToOneField(related_name='author_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CampaignsSignup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(unique=True, max_length=75)),
                ('telephone', models.CharField(max_length=100, null=True, blank=True)),
                ('alt_telephone', models.CharField(max_length=100, null=True, blank=True)),
                ('name', models.CharField(max_length=100, null=True, blank=True)),
                ('newsletter', models.NullBooleanField(default=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('is_synched', models.NullBooleanField(default=True)),
                ('best_call_time', models.CharField(max_length=10, null=True, blank=True)),
                ('is_client', models.NullBooleanField(default=False)),
                ('is_fake', models.BooleanField(default=False)),
                ('source', models.CharField(max_length=100, null=True, blank=True)),
            ],
            options={
                'ordering': ['created_date'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CarouselTab',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=500)),
                ('description', models.CharField(max_length=500)),
                ('order', models.IntegerField()),
                ('media', models.ImageField(null=True, upload_to=b'carousel/', blank=True)),
                ('cta_link_title', models.CharField(max_length=100, null=True, blank=True)),
                ('cta_link', models.URLField(null=True, blank=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='HealthcheckSignup',
            fields=[
                ('uuid', django_extensions.db.fields.UUIDField(primary_key=True, serialize=False, editable=False, blank=True, name=b'uuid')),
                ('first_name', models.CharField(max_length=20)),
                ('last_name', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=75)),
                ('telephone', models.CharField(unique=True, max_length=20, error_messages={b'unique': b'A healthcheck request with this telephone number already exists.'})),
                ('date_requested', models.DateTimeField(auto_now_add=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NewsletterSignup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(max_length=75)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('is_synched', models.NullBooleanField(default=False)),
                ('activation_key', models.CharField(max_length=40, null=True)),
                ('is_activated', models.BooleanField(default=True)),
                ('source', models.CharField(max_length=100, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('dob', models.DateField(null=True, blank=True)),
                ('telephone', models.CharField(max_length=250, null=True, blank=True)),
                ('salutation', models.CharField(max_length=10)),
                ('postcode', models.CharField(max_length=10, null=True, blank=True)),
                ('newsletter', models.NullBooleanField(default=False)),
                ('ratealerts', models.NullBooleanField(default=False)),
                ('created_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('is_synched', models.NullBooleanField(default=False, help_text=b'Signifies if the user details have been synced with the SalesForce system')),
                ('ip_address', models.CharField(max_length=100, null=True, blank=True)),
                ('source', models.CharField(max_length=100, null=True, blank=True)),
                ('skeleton_user', models.NullBooleanField(default=False, help_text=b'Whether they have been created from the sync or not')),
                ('filled_in_name', models.BooleanField(default=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': (('change_sccode', 'Can update SC codes for multiple accounts'), ('add_product', 'Can add a product to a customers portfolio'), ('change_user_portfolio', 'Can change a users portfolio'), ('change_user_activation', 'Can change a users activation status'), ('change_user_email', 'Can change a users email address'), ('add_concierge_client', 'Can add a new concierge client'), ('change_user_password', 'Can change a users password'), ('change_user_subscriptions', 'Can change a users subscriptions'), ('change_user_sync', 'Can change a users sync status')),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RateAlertsSignup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(max_length=75)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('is_synched', models.NullBooleanField(default=False)),
                ('activation_key', models.CharField(max_length=40, null=True)),
                ('is_activated', models.BooleanField(default=True)),
                ('source', models.CharField(max_length=100, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Rates',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('boe_rate', models.DecimalField(max_digits=4, decimal_places=2)),
                ('inflation_rate', models.DecimalField(max_digits=4, decimal_places=2)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'Rates',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Referrer',
            fields=[
                ('uuid', django_extensions.db.fields.UUIDField(primary_key=True, serialize=False, editable=False, blank=True, name=b'uuid')),
                ('name', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ReminderSignup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(max_length=75)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('is_synched', models.NullBooleanField(default=False)),
                ('healthcheck', models.NullBooleanField(default=False)),
                ('bestbuys', models.NullBooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Tweet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('summary', models.CharField(max_length=255)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'get_latest_by': 'last_updated',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserNext',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uuid', models.CharField(max_length=255, null=True, blank=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserReferral',
            fields=[
                ('uuid', django_extensions.db.fields.UUIDField(primary_key=True, serialize=False, editable=False, blank=True, name=b'uuid')),
                ('referral_action', models.CharField(default=b'unknown', max_length=30, choices=[(b'unknown', b'User Performed An Unknown Paid For Action'), (b'signup', b'User Signed Up'), (b'rate_tracker', b'User Subscribed To RateTracker'), (b'rate_tracker_used', b'User has used RateTracker'), (b'rate_alerts', b'User Subscribed To Rate Alerts'), (b'newsletter', b'User Subscribed To Newsletter'), (b'savers_priority_list', b'User Subscribed To The Savers Priority List'), (b'seven_pitfalls', b'User Signed Up Via Seven Pitfalls To Larger Savers'), (b'petition', b'User Subscribed To The Petition'), (b'concierge_enquiry', b'User Enquired About Concierge'), (b'concierge_client', b'User Signed Up To Concierge'), (b'recurring_weekly_best_buys', b'User Signed Up For Recurring Best Buys - Weekly'), (b'recurring_monthly_best_buys', b'User Signed Up For Recurring Best Buys - Monthly'), (b'fifty_pound_challenge', b'User Signed Up For The \xc2\xa350 Challenge'), (b'the_biggest_mistake', b'User Signed Up For The Biggest Mistake'), (b'the_value_of_advice', b'User Signed Up For The Value Of Advice'), (b'tpo_referral', b'User was referred to TPO'), (b'bj_referral', b'User was referred to Beckford James')])),
                ('referral_date', models.DateTimeField(auto_now_add=True)),
                ('referral_paid', models.BooleanField(default=False)),
                ('referral_paid_date', models.DateTimeField(null=True)),
                ('referrer', models.ForeignKey(to='common.Referrer', null=True)),
                ('referrer_from', models.ForeignKey(related_name='referrerfrom', to='common.Referrer', null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('referral_date',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UUIDNext',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uuid', models.CharField(unique=True, max_length=255)),
                ('params', models.CharField(max_length=500, null=True, blank=True)),
                ('next', models.CharField(max_length=50)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='userreferral',
            unique_together=set([('user', 'referral_action')]),
        ),
    ]

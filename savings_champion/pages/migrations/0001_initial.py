# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(unique=True, max_length=200)),
                ('slug', models.SlugField(help_text=b'The slug is a url encoded version of your title and is used to create the web address', unique=True, max_length=200)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.BooleanField(default=False)),
                ('publish_date', models.DateField(null=True)),
                ('meta_description', models.CharField(max_length=200, null=True, blank=True)),
                ('body', models.TextField(verbose_name=b'Page Content', blank=True)),
                ('teaser', models.CharField(help_text=b'A teaser is normally a truncated sample of the Article Content,\n    if left blank, the CMS will create it from the first 250 characters of the Page Content.', max_length=1000, blank=True)),
                ('show_ratetracker_form', models.BooleanField(default=False)),
                ('show_newsletter_form', models.BooleanField(default=False)),
                ('show_ratealert_form', models.BooleanField(default=False)),
                ('show_joint_form', models.BooleanField(default=False)),
                ('show_concierge_form', models.BooleanField(default=False)),
                ('show_isa_tool', models.BooleanField(default=False)),
                ('image', models.ImageField(null=True, upload_to=b'guide_cover_images', blank=True)),
                ('guide_section', models.CharField(max_length=50, null=True, blank=True)),
                ('type', models.TextField()),
                ('genre', models.CharField(default=b'OpEd', max_length=500)),
                ('tags', models.CharField(default=b'savings account, interest rate, banking, finance, investment,', max_length=500)),
                ('url_reverse', models.TextField(null=True, blank=True)),
            ],
            options={
                'ordering': ('-publish_date',),
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Award',
            fields=[
                ('uuid', django_extensions.db.fields.UUIDField(serialize=False, editable=False, primary_key=True, blank=True)),
                ('ranking', models.IntegerField(choices=[(0, b'Winner'), (98, b'Highly Commended'), (99, b'Highly Commended')])),
                ('awarded_date', models.DateField(default=datetime.datetime.today)),
            ],
            options={
                'ordering': ['ranking'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AwardCategory',
            fields=[
                ('uuid', django_extensions.db.fields.UUIDField(serialize=False, editable=False, primary_key=True, blank=True)),
                ('title', models.TextField()),
                ('order', models.IntegerField(unique=True, null=True)),
            ],
            options={
                'ordering': ['order'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BaseComment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('comment_date', models.DateTimeField(auto_now_add=True)),
                ('comment', models.TextField(blank=True)),
                ('approved', models.BooleanField(default=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ArticleComment',
            fields=[
                ('basecomment_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='pages.BaseComment')),
            ],
            options={
            },
            bases=('pages.basecomment',),
        ),
        migrations.CreateModel(
            name='BlogComment',
            fields=[
                ('basecomment_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='pages.BaseComment')),
            ],
            options={
            },
            bases=('pages.basecomment',),
        ),
        migrations.CreateModel(
            name='BlogItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(unique=True, max_length=200)),
                ('slug', models.SlugField(help_text=b'The slug is a url encoded version of your title and is used to create the web address', unique=True, max_length=200)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.BooleanField(default=False)),
                ('publish_date', models.DateField(null=True)),
                ('meta_description', models.CharField(max_length=200, null=True, blank=True)),
                ('body', models.TextField(verbose_name=b'Page Content', blank=True)),
                ('teaser', models.CharField(help_text=b'A teaser is normally a truncated sample of the Article Content,\n    if left blank, the CMS will create it from the first 250 characters of the Page Content.', max_length=1000, blank=True)),
                ('show_ratetracker_form', models.BooleanField(default=False)),
                ('show_newsletter_form', models.BooleanField(default=False)),
                ('show_ratealert_form', models.BooleanField(default=False)),
                ('show_joint_form', models.BooleanField(default=False)),
                ('show_concierge_form', models.BooleanField(default=False)),
                ('show_isa_tool', models.BooleanField(default=False)),
                ('genre', models.CharField(default=b'Blog', max_length=500, choices=[(b'Blog', b'Blog'), (b'Ask the experts', b'Ask the experts')])),
                ('tags', models.CharField(default=b'savings account, interest rate, banking, finance, investment,', max_length=500)),
            ],
            options={
                'ordering': ('-publish_date',),
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ChildPage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200)),
                ('slug', models.CharField(help_text=b'The slug is a url encoded version of your title and is used to create the web address', max_length=200)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.BooleanField(default=False)),
                ('meta', models.TextField(blank=True)),
                ('body', models.TextField(blank=True)),
                ('footer_nav', models.BooleanField(default=False)),
                ('order', models.IntegerField(default=1, blank=True)),
            ],
            options={
                'ordering': ('title',),
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200)),
                ('slug', models.CharField(help_text=b'The slug is a url encoded version of your title and is used to create the web address', max_length=200)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.BooleanField(default=False)),
                ('document', models.FileField(null=True, upload_to=b'documents/', blank=True)),
            ],
            options={
                'ordering': ('title',),
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FAQ',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200)),
                ('slug', models.CharField(help_text=b'The slug is a url encoded version of your title and is used to create the web address', max_length=200)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ('title',),
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FAQBlock',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('question', models.TextField(blank=True)),
                ('answer', models.TextField(blank=True)),
                ('order', models.IntegerField(default=1)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FiftyPoundChallengeAccount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.TextField()),
                ('rate', models.TextField()),
                ('account_type', models.TextField(choices=[(b'easy_access', b'Easy Access Account'), (b'notice', b'Notice Account'), (b'current', b'High Interest Current Account'), (b'1y_fixed_rate', b'1Yr Fixed Rate Bond'), (b'2y_fixed_rate', b'2Yr Fixed Rate Bond'), (b'3y_fixed_rate', b'3Yr Fixed Rate Bond'), (b'4y_fixed_rate', b'4Yr Fixed Rate Bond'), (b'5y_fixed_rate', b'5Yr Fixed Rate Bond'), (b'6y_fixed_rate', b'6Yr Fixed Rate Bond'), (b'7y_fixed_rate', b'7Yr Fixed Rate Bond'), (b'other_fixed_rate', b'Other Fixed Rate Bond'), (b'variable_rate', b'Variable Rate Bond'), (b'regular_saver', b'Regular Savings Account'), (b'fixed_rate_isa', b'Fixed Rate ISA'), (b'variable_rate_isa', b'Variable Rate ISA')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FiftyPoundChallengeSignup',
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
        migrations.CreateModel(
            name='FormMessage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message_key', models.CharField(max_length=30)),
                ('text', models.TextField(verbose_name=b'Form Message', blank=True)),
            ],
            options={
                'verbose_name': 'Form Message',
                'verbose_name_plural': 'Form Messages',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='IHTGuideSignup',
            fields=[
                ('uuid', django_extensions.db.fields.UUIDField(serialize=False, editable=False, primary_key=True, blank=True)),
                ('name', models.TextField()),
                ('email', models.EmailField(max_length=75)),
                ('phone', models.TextField()),
                ('date_created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Jargon',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200)),
                ('slug', models.CharField(help_text=b'The slug is a url encoded version of your title and is used to create the web address', max_length=200)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.BooleanField(default=False)),
                ('first_char', models.CharField(max_length=1, blank=True)),
                ('description', models.TextField(verbose_name=b'Page Content', blank=True)),
            ],
            options={
                'ordering': ('title',),
                'verbose_name': 'Jargon',
                'verbose_name_plural': 'Jargon',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NISAGuideSignup',
            fields=[
                ('uuid', django_extensions.db.fields.UUIDField(serialize=False, editable=False, primary_key=True, blank=True)),
                ('name', models.TextField()),
                ('email', models.EmailField(max_length=75)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200)),
                ('slug', models.CharField(help_text=b'The slug is a url encoded version of your title and is used to create the web address', max_length=200)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.BooleanField(default=False)),
                ('lft', models.IntegerField()),
                ('rgt', models.IntegerField()),
                ('is_section', models.BooleanField(default=False, help_text=b'Selecting this checkbox will attempt to add this page to the top navigation', verbose_name=b'Add to the top navigation')),
                ('is_footer', models.BooleanField(default=False, help_text=b'These pages will appear along the footer and are generally for site T&Cs and site statements.', verbose_name=b'Add to the footer navigation')),
                ('meta_description', models.CharField(max_length=200, null=True, blank=True)),
            ],
            options={
                'ordering': ('lft',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PageBlock',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('block_key', models.CharField(max_length=40)),
                ('block_title', models.CharField(max_length=150)),
                ('block_description', models.CharField(max_length=255, null=True, blank=True)),
                ('text', models.TextField(verbose_name=b'Content', blank=True)),
                ('max_length', models.IntegerField()),
                ('cta_link', models.URLField(null=True, blank=True)),
                ('created_date', models.DateTimeField(auto_now=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now_add=True, null=True)),
            ],
            options={
                'verbose_name': 'Page Block',
                'verbose_name_plural': 'Page Blocks',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PageBody',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField(verbose_name=b'Page Content', blank=True)),
            ],
            options={
                'verbose_name': 'Page Content',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ParentPage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200)),
                ('slug', models.CharField(help_text=b'The slug is a url encoded version of your title and is used to create the web address', max_length=200)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.BooleanField(default=False)),
                ('main_nav', models.BooleanField(default=False)),
                ('body', models.TextField(help_text=b'Used if no child pages are available', blank=True)),
                ('meta', models.TextField(help_text=b'Overridden by child pages', blank=True)),
            ],
            options={
                'ordering': ('title',),
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Petition',
            fields=[
                ('uuid', django_extensions.db.fields.UUIDField(serialize=False, editable=False, primary_key=True, blank=True)),
                ('first_name', models.TextField()),
                ('last_name', models.TextField()),
                ('email', models.TextField(null=True)),
                ('postcode', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PressAppearance',
            fields=[
                ('uuid', django_extensions.db.fields.UUIDField(serialize=False, editable=False, primary_key=True, blank=True)),
                ('publication_type', models.IntegerField(default=1, choices=[(1, b'Newspaper'), (2, b'Radio'), (3, b'TV/Video')])),
                ('title', models.TextField()),
                ('author', models.TextField()),
                ('link', models.URLField(null=True, blank=True)),
                ('date_featured', models.DateTimeField()),
            ],
            options={
                'ordering': ['-date_featured'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PressAppearancePublication',
            fields=[
                ('uuid', django_extensions.db.fields.UUIDField(serialize=False, editable=False, primary_key=True, blank=True)),
                ('name', models.TextField(verbose_name=b'Publication')),
                ('ranking', models.IntegerField(default=3, choices=[(1, b'National'), (2, b'Local'), (3, b'Other')])),
            ],
            options={
                'ordering': ['ranking', 'name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProductFAQ',
            fields=[
                ('uuid', django_extensions.db.fields.UUIDField(serialize=False, editable=False, primary_key=True, blank=True)),
                ('name', models.TextField()),
                ('slug', models.SlugField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProductFAQuestion',
            fields=[
                ('uuid', django_extensions.db.fields.UUIDField(serialize=False, editable=False, primary_key=True, blank=True)),
                ('question', models.TextField()),
                ('answer', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProductQuestionaireSignup',
            fields=[
                ('uuid', django_extensions.db.fields.UUIDField(serialize=False, editable=False, primary_key=True, blank=True)),
                ('first_name', models.TextField()),
                ('last_name', models.TextField()),
                ('email', models.EmailField(max_length=75)),
                ('phone', models.TextField()),
                ('easy_access', models.BooleanField(default=False)),
                ('notice_1_3', models.BooleanField(default=False)),
                ('notice_3_6', models.BooleanField(default=False)),
                ('fixed_rate_1', models.BooleanField(default=False)),
                ('fixed_rate_2', models.BooleanField(default=False)),
                ('funds', models.TextField(default=b'0-50k', choices=[(b'0-50k', b'\xc2\xa30 - \xc2\xa350,000'), (b'50k-100k', b'\xc2\xa350,000 - \xc2\xa3100,000'), (b'100k-250k', b'\xc2\xa3100,000 - \xc2\xa3250,000'), (b'250k-1M', b'\xc2\xa3250,000 - \xc2\xa31,000,000'), (b'1M-plus', b'\xc2\xa31,000,000 plus')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RateAlert',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200)),
                ('slug', models.SlugField(max_length=200)),
                ('body', models.TextField(blank=True)),
                ('publish_date', models.DateField(null=True, blank=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ('title',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SavingsPriorityListOptionSignup',
            fields=[
                ('uuid', django_extensions.db.fields.UUIDField(serialize=False, editable=False, primary_key=True, blank=True)),
                ('easy_access', models.BooleanField(default=True)),
                ('notice', models.BooleanField(default=True)),
                ('one_year', models.BooleanField(default=True)),
                ('two_to_three_year', models.BooleanField(default=True)),
                ('four_to_five_year', models.BooleanField(default=True)),
                ('over_five_years', models.BooleanField(default=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SavingsPriorityListSignup',
            fields=[
                ('uuid', django_extensions.db.fields.UUIDField(serialize=False, editable=False, primary_key=True, blank=True)),
                ('name', models.TextField(default=b'')),
                ('email', models.EmailField(max_length=75)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SevenPitfallsSignup',
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
        migrations.CreateModel(
            name='StaticPage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200)),
                ('slug', models.CharField(help_text=b'The slug is a url encoded version of your title and is used to create the web address', max_length=200)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ('title',),
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StaticPageBlock',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('block_id', models.CharField(max_length=1000, blank=True)),
                ('block', models.TextField(blank=True)),
                ('staticpage', models.ForeignKey(to='pages.StaticPage')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TheBiggestMistakeSignup',
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
    ]

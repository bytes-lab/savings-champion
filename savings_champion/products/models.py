from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models, IntegrityError
from django.db.transaction import atomic
from django.utils.functional import cached_property
from django.utils.text import slugify
from django_extensions.db.fields import UUIDField
from markupfield.fields import MarkupField
from api.v1.models import ApiExcludedItem
from common.models import BaseModel, Referrer, better_slugify
from django.db.models import Q
import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from pages.models import StaticPage
from decimal import *
from common.utils import build_url
import logging

logger = logging.getLogger(__name__)

TODO_LENGTH = 200

MOODYS_RATING = (
    (None, 'None'),
    ('0', 'None'),
    ('A1', 'Obligations rated A are considered upper-medium grade and are subject to low credit risk'),
    ('A2', 'Obligations rated A are considered upper-medium grade and are subject to low credit risk'),
    ('A3', 'Obligations rated A are considered upper-medium grade and are subject to low credit risk'),
    ('Aa1', 'Obligations rated Aa are judged to be of high quality and are subject to very low credit risk'),
    ('Aa2', 'Obligations rated Aa are judged to be of high quality and are subject to very low credit risk'),
    ('Aa3', 'Obligations rated Aa are judged to be of high quality and are subject to very low credit risk'),
    ('Aaa1', 'Obligations rated Aaa are judged to be of the highest quality, with minimal credit risk.'),
    ('Aaa2', 'Obligations rated Aaa are judged to be of the highest quality, with minimal credit risk.'),
    ('Aaa3', 'Obligations rated Aaa are judged to be of the highest quality, with minimal credit risk.'),
    ('B1', 'Obligations rated B are considered speculative and are subject to high credit risk.'),
    ('B2', 'Obligations rated B are considered speculative and are subject to high credit risk.'),
    ('B3', 'Obligations rated B are considered speculative and are subject to high credit risk.'),
    ('Ba1', 'Obligations rated Ba are judged to have speculative elements and are subject to substantial credit risk.'),
    ('Ba2', 'Obligations rated Ba are judged to have speculative elements and are subject to substantial credit risk.'),
    ('Ba3', 'Obligations rated Ba are judged to have speculative elements and are subject to substantial credit risk.'),
    ('Baa1', 'Obligations rated Baa are subject to moderate credit risk. They are considered medium-grade and as such '
             'may possess certain speculative characteristics.'),
    ('Baa2', 'Obligations rated Baa are subject to moderate credit risk. They are considered medium-grade and as such '
             'may possess certain speculative characteristics.'),
    ('Baa3', 'Obligations rated Baa are subject to moderate credit risk. They are considered medium-grade and as such '
             'may possess certain speculative characteristics.'),
    ('C1', 'Obligations rated C are the lowest rated class of bonds and are typically in default, with little prospect '
           'for recovery of principal or interest.'),
    ('C2', 'Obligations rated C are the lowest rated class of bonds and are typically in default, with little prospect '
           'for recovery of principal or interest.'),
    ('C3', 'Obligations rated C are the lowest rated class of bonds and are typically in default, with little prospect '
           'for recovery of principal or interest.'),
    ('Ca1', 'Obligations rated Ca are highly speculative and are likely in, or very near, default, with some prospect '
            'of recovery of principal and interest.'),
    ('Ca2', 'Obligations rated Ca are highly speculative and are likely in, or very near, default, with some prospect '
            'of recovery of principal and interest.'),
    ('Ca3', 'Obligations rated Ca are highly speculative and are likely in, or very near, default, with some prospect '
            'of recovery of principal and interest.'),
    ('Caa1', 'Obligations rated Caa are judged to be of poor standing and are subject to very high credit risk.'),
    ('Caa2', 'Obligations rated Caa are judged to be of poor standing and are subject to very high credit risk.'),
    ('Caa3', 'Obligations rated Caa are judged to be of poor standing and are subject to very high credit risk.'),
)

FITCHS_RATING = (
    (0, 'None'),
    (None, 'None'),
    ('A+', 'A+'),
    ('A', 'A'),
    ('B', 'B'),
    ('C', 'C'),
)


class Provider(models.Model):
    title = models.TextField(unique=True)
    slug = models.TextField(help_text="""The slug is a url encoded version of your title and is used to create the web address""")

    created_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)
    logo = models.ImageField(upload_to='logos',
                             help_text="""The logo will appear alongside the product information on the best buy tables""")
    fscs_parent = models.TextField(blank=True, null=True,
                                   help_text="""Please enter this all as one word, for example: RoyalBankOfScotland""")
    fscs_licence_holder = models.TextField(null=True)
    fscs_limit_type = models.ForeignKey('FSCSLimitType', null=True)
    ethical = models.BooleanField(default=False)
    ethical_rating = models.TextField(default='', blank=True, null=True)
    moodys_rating = models.CharField(choices=MOODYS_RATING, null=True, blank=True, max_length=4)
    fitchs_rating = models.CharField(choices=FITCHS_RATING, default=0, blank=True, null=True, max_length=4)
    building_society = models.BooleanField(default=False)
    mutual = models.BooleanField(default=False)
    bank = models.BooleanField(default=False)
    high_street = models.BooleanField(default=False)
    phone = models.TextField(default='', blank=True, null=True)
    website = models.URLField(max_length=255, default='', blank=True, null=True)
    meets_service_standard = models.BooleanField(default=True)
    reason_to_exclude = models.TextField(default='', blank=True, null=True)
    compliance_checked = models.BooleanField(default=False)
    sf_provider_id = models.TextField(unique=True, null=True)
    isa_topup_2014 = models.BooleanField(default=False)
    isa_topup_2014_conditions = models.TextField(default='', blank=True)
    isa_topup_2014_email_list = models.TextField(default='', blank=True)
    provider_maximum = models.DecimalField(max_digits=18, decimal_places=2, default=0, blank=True)

    exclude_from_api_for = models.ManyToManyField(ApiExcludedItem, blank=True, null=True)

    class Meta:
        ordering = ('title',)

    def __unicode__(self):
        return u'%s' % self.title

    def save(self, *args, **kwargs):
        if self.slug in EMPTY_VALUES:
            self.slug = better_slugify(self.title)
        super(Provider, self).save(*args, **kwargs)

    @property
    def fscs_licence(self):
        """
        Allows code to access the fscs_licence via the Provider

        :return: string
        """
        return self.fscs_limit_type.name

    @property
    def get_shared_licence_providers(self):

        """
        Gets all provider ids that share a licence with this provider, and will always include this provider at least
        """

        if self.fscs_parent is None and not Provider.objects.filter(fscs_parent=self.sf_provider_id).exists():
            return {self.pk}
        elif self.fscs_parent is None:
            provider_group = [self.pk]
            provider_group.extend(Provider.objects.filter(fscs_parent=self.sf_provider_id).values_list('pk', flat=True))
            return set(provider_group)

        parent_provider = Provider.objects.filter(sf_provider_id=self.fscs_parent)
        if parent_provider.exists():
            provider_group = [self.pk]
            provider_group.extend(Provider.objects.filter(fscs_parent=self.fscs_parent).values_list('pk', flat=True))
            provider_group.extend(Provider.objects.filter(sf_provider_id=self.fscs_parent).values_list('pk', flat=True))
            return set(provider_group)
        else:
            return {self.pk}


class ProviderContacts(models.Model):
    first_name = models.TextField(default='')
    last_name = models.TextField(default='')
    title = models.TextField(default='')
    email = models.EmailField(default='')
    office_phone = models.TextField(default='')


class ProviderSpecificFields(models.Model):
    field_name = models.TextField(default='')
    provider = models.ForeignKey(Provider)


class ProviderBestBuy(models.Model):
    provider = models.ForeignKey('Provider')
    bestbuys = models.ManyToManyField('BestBuy')

    class Meta:
        ordering = ('provider__title',)


EMPTY_VALUES = ['', None, '']


class BasePortfolio(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    account_type = models.ForeignKey('BestBuy')
    balance = models.DecimalField(decimal_places=2, max_digits=10, null=True)
    is_deleted = models.BooleanField(blank=True, default=False)

    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True, blank=True, null=True)
    is_synched = models.NullBooleanField(blank=True, null=True, default=False)

    class Meta:
        abstract = True

    def product_account_type(self):
        return self.account_type

    def build_compare_url(self):
        return reverse('compare_table_ratetracker', kwargs={'portfolio_id': self.id})

    def build_delete_url(self):
        return build_url('deletePortfolio', get={'id': self.id})

    def show_comparison(self):
        bestbuy = BestBuy.objects.get(title=self.account_type, client_type='p')
        assert self.account_type != 'Variable Rate Bond', bestbuy.has_table
        if bestbuy.has_table:
            return True

        return False

    def outside_lifecycle(self):
        pass


class ProductPortfolio(BasePortfolio):
    master_product = models.ForeignKey('MasterProduct')
    opening_date = models.DateField(blank=True, null=True)
    provider = models.ForeignKey('Provider')
    bonus_term = models.IntegerField(null=True, blank=True)
    notice = models.IntegerField(null=True, blank=True)
    last_alerted = models.DateField(null=True, blank=True)
    starting_rate = models.DecimalField(default=0, decimal_places=4, max_digits=6)

    def __unicode__(self):
        return u" ".join([str(self.pk), self.master_product.title, str(self.balance)])

    def __str__(self):
        return " ".join([str(self.pk), self.master_product.title, str(self.balance)])

    @cached_property
    def expire_date(self):
        try:
            return self.opening_date + relativedelta(months=self.master_product.bonus_term)
        except:
            return False

    @cached_property
    def get_latest_rate(self):
        if self.opening_date is not None:
            return self.master_product.get_latest_rate(self.balance, self.opening_date)
        else:
            return self.master_product.get_latest_rate(self.balance)


    @cached_property
    def get_latest_monthly_rate(self):
        try:
            if self.opening_date:
                return self.master_product.get_latest_monthly_rate(self.balance, self.opening_date)
            else:
                return self.master_product.get_latest_monthly_rate(self.balance)
        except:
            return False

    @cached_property
    def check_bonus_expiry(self):
        """
        Check to see if current bonus has expired
        :return: bool
        """
        if self.master_product.bonus_end_date:
            if self.master_product.bonus_end_date < datetime.datetime.now().date():
                return True
        if self.opening_date and self.master_product.bonus_term > 0:
            if self.expire_date < datetime.datetime.now().date():
                return True
        return False

    @cached_property
    def has_bonus(self):
        """
        Check for the existence of a bonus on this product
        :return: bool
        """
        if self.master_product.bonus_end_date:
            return True
        elif self.opening_date and self.master_product.bonus_term > 0:
            return True
        return False

    @cached_property
    def get_bonus_expiry(self):
        if self.master_product.bonus_end_date:
            return self.master_product.bonus_end_date
        if self.opening_date:
            return self.expire_date

    @cached_property
    def get_personal_rating(self):

        rating = 6
        if self.account_type.is_bond:
            if self.expired:
                rating = 8
            else:
                rating = 7
        if self.account_type.has_table:
            bestbuys = self.product_account_type.get_personal_products(ratetracker=True, balance=self.balance)
            bestbuys_no_current = bestbuys.exclude(master_product=self.master_product)
            try:
                top_bestbuy = bestbuys_no_current[0]
            except IndexError:
                # No suitable Best buys
                if bestbuys.exists():
                    # The current account is the best one in the list and it's applicable
                    rating = 6
                else:
                    # This account isn't in the list and none are applicable.
                    rating = 10
                return rating

            bestbuys_no_current = bestbuys_no_current.order_by('-link_to_products')
            lowest_bestbuy = bestbuys_no_current[0]

            rate = self.get_latest_rate

            if rate >= top_bestbuy.master_product.get_latest_rate(self.balance):
                rating = 6
            elif rate >= lowest_bestbuy.master_product.get_latest_rate(self.balance):
                # leave a number for fixed rate accounts that are maturing
                rating = 5
            elif rate < Decimal('0.1'):
                rating = 1
            else:
                rating = 3
        return rating

    @cached_property
    def get_personal_rating_readable(self):
        rating = self.get_personal_rating
        # rating 2 used to be expired
        if rating == 1:
            rating_text = 'Critical'
        elif rating == 3:
            rating_text = 'Attention Needed'
        elif rating == 4:
            rating_text = 'Changing'
        elif rating == 6:
            rating_text = 'Excellent'
        elif rating == 7:
            rating_text = 'Within Term'
        elif rating == 8:
            rating_text = 'Matured'
        else:
            rating_text = 'Good'

        return rating_text

    @cached_property
    def get_personal_rating_bootstrap_class(self):
        rating = self.get_personal_rating
        # rating 2 used to be expired
        if rating in [1, 3, 8]:
            rating_text = 'panel-danger'
        elif rating == 4:
            rating_text = 'panel-warning'
        elif rating in [6, 7]:
            rating_text = 'panel-success'
        else:
            rating_text = 'panel-default'

        return rating_text

    @cached_property
    def get_rate_text(self):
        rating = self.get_personal_rating
        staticpage = StaticPage.objects.get(slug='healthcheck-portfolio')

        if rating == 0:
            rating_text = staticpage.staticpageblock_set.get(block_id='unavailable-pp').block
        elif rating == 1:
            rating_text = staticpage.staticpageblock_set.get(block_id='critical-pp').block
        elif rating == 3:
            rating_text = staticpage.staticpageblock_set.get(block_id='attention-pp').block
        elif rating == 5:
            rating_text = staticpage.staticpageblock_set.get(block_id='ok-pp').block
        elif rating == 6:
            rating_text = staticpage.staticpageblock_set.get(block_id='excellent-pp').block

        else:
            rating_text = 'This product is outside the minimum/maximum opening balance of any of our Best Buy\'s for ' \
                          'this category, as such it cannot be advised upon by Rate Tracker.'

        return rating_text

    @cached_property
    def get_extra_personal_earnings(self):
        extra_earnings = ''
        if self.account_type.has_table:
            bestbuys = self.product_account_type.get_personal_products(ratetracker=True,
                                                                                                 balance=self.balance).exclude(
                master_product=self.master_product)
            if bestbuys.exists():
                best_bestbuy_rate = 0
                for bestbuy in bestbuys:
                    bestbuy_rate = bestbuy.master_product.get_latest_rate(self.balance)
                    if bestbuy_rate > best_bestbuy_rate:
                        best_bestbuy_rate = bestbuy_rate

                bestbuy_interest = self.balance * (best_bestbuy_rate / 100)
                portfolio_interest = self.balance * (self.get_latest_rate / 100)

                extra_earnings = bestbuy_interest - portfolio_interest

        return extra_earnings

    @cached_property
    def get_top_personal_bestbuy(self):
        bestbuy = ''
        if self.account_type.has_table:
            bestbuys = self.product_account_type.get_personal_products(ratetracker=True,
                                                                                                 balance=self.balance).exclude(
                master_product=self.master_product)
            if bestbuys.exists():
                bestbuy_provider = bestbuys[0].provider.title
                bestbuy_title = bestbuys[0].title
                bestbuy = bestbuy_provider + ' ' + bestbuy_title

        return bestbuy

    @cached_property
    def get_top_personal_bestbuy_url(self):
        bestbuy = '.'
        if self.account_type.has_table:
            bestbuys = self.product_account_type.get_personal_products(ratetracker=True,
                                                                                                 balance=self.balance).exclude(
                master_product=self.master_product)
            if bestbuys.exists():
                bestbuy = bestbuys[0].url
        return bestbuy

    @cached_property
    def get_top_personal_bestbuy_rate(self):
        bestbuy = '.'
        if self.account_type.has_table:
            bestbuys = self.product_account_type.get_personal_products(ratetracker=True,
                                                                                                 balance=self.balance).exclude(
                master_product=self.master_product)
            bestbuy = bestbuys[0].master_product.get_latest_rate(self.balance)

        return bestbuy

    @cached_property
    def outside_balance(self):
        return self.master_product.get_outside_balance(self.balance)

    @cached_property
    def expiring_next_month(self):
        if self.has_bonus:
            if datetime.datetime.now().date() < self.get_bonus_expiry < datetime.datetime.now().date() + relativedelta(
                    months=1):
                return True
        return False

    @cached_property
    def expired(self):
        if self.has_bonus:
            if self.get_bonus_expiry < datetime.datetime.now().date() + relativedelta(
                    months=1):
                return True
        return False

    @cached_property
    def get_bonus_amount(self):
        return self.master_product.return_product_from_balance(self.balance).bonus_amount

    @cached_property
    def get_is_changing(self):
        if self.has_bonus:
            expiry = self.get_bonus_expiry
            first_of_month = datetime.date.today().replace(day=1)
            end_of_month = datetime.date.today().replace(day=28) + datetime.timedelta(days=4)
            end_of_month = end_of_month - datetime.timedelta(days=end_of_month.day)
            if first_of_month <= expiry <= end_of_month:
                return True
        return False

    def save(self, *args, **kwargs):
        super(ProductPortfolio, self).save(*args, **kwargs)
        from products.tasks import sync_ratetracker_portfolio
        if not self.is_synched:
            sync_ratetracker_portfolio.apply_async([self.pk], countdown=1)

    @cached_property
    def product_account_type(self):
        return self.master_product.get_bestbuy_type


class RatetrackerReminder(BasePortfolio):
    provider = models.ForeignKey('products.Provider')
    maturity_date = models.DateField()
    rate = models.DecimalField(default=0, decimal_places=4, max_digits=18)
    fee_exempt = models.BooleanField(default=True)
    term = models.IntegerField(default=0)
    pool_altered = models.BooleanField(default=False)

    @cached_property
    def get_personal_rating(self):

        if self.maturity_date > datetime.datetime.now().date():
            rating = 6
        else:
            rating = 2

        return rating

    @property
    def get_latest_rate(self):
        return self.rate

    @cached_property
    def get_personal_rating_readable(self):
        rating = self.get_personal_rating

        if rating == 2:
            rating_text = 'Matured'
        elif rating == 6:
            rating_text = 'Within Term'
        else:
            rating_text = 'OK'

        return rating_text

    @cached_property
    def get_personal_rating_bootstrap_class(self):
        rating = self.get_personal_rating
        # rating 2 used to be expired
        if rating in [1, 3, 8]:
            rating_text = 'panel-danger'
        elif rating == 4:
            rating_text = 'panel-warning'
        elif rating in [6, 7]:
            rating_text = 'panel-success'
        else:
            rating_text = 'panel-default'

        return rating_text

    def get_rate_text(self):
        rating_text = 'OK'
        rating = self.get_personal_rating
        staticpage = StaticPage.objects.get(slug='healthcheck-portfolio')
        if rating == 2:
            if 'Linked' in self.account_type.get_title_display():
                rating_text = staticpage.staticpageblock_set.get(block_id='expired-ilc-rr').block
            else:
                rating_text = staticpage.staticpageblock_set.get(block_id='expired-rr').block
        elif rating == 6:
            rating_text = staticpage.staticpageblock_set.get(block_id='excellent-rr').block

        return rating_text

    def get_extra_personal_earnings(self):
        extra_earnings = ''
        if self.account_type.has_table:
            bestbuys = self.account_type.get_personal_products(ratetracker=True, balance=self.balance)

            try:
                bestbuy_interest = self.balance * (bestbuys[0].gross_rate / 100)
            except IndexError:
                bestbuy_interest = 0
            extra_earnings = "{0:.2f}".format(Decimal(bestbuy_interest))

        return extra_earnings

    def get_top_personal_bestbuy(self):
        bestbuy = ''
        if self.account_type.has_table:
            bestbuys = self.account_type.get_personal_products(ratetracker=True, balance=self.balance)
            try:
                bestbuy_provider = bestbuys[0].provider.title
                bestbuy_title = bestbuys[0].title
                bestbuy = bestbuy_provider + ' ' + bestbuy_title
            except IndexError:
                bestbuy = ""
        return bestbuy

    def get_top_personal_bestbuy_url(self):
        bestbuy = '.'
        if self.account_type.has_table:
            bestbuys = self.account_type.get_personal_products(ratetracker=True, balance=self.balance)
            if bestbuys.exists():
                bestbuy = bestbuys[0].url
        return bestbuy

    def build_compare_url(self):
        return build_url('compare_table', get={'id': self.id, 'fixed': True})

    def get_matured_status(self):
        if self.maturity_date > datetime.datetime.now().date():
            return False
        return True

    def expiring_next_month(self):
        if datetime.datetime.now().date() < self.maturity_date < datetime.datetime.now().date() + relativedelta(
                months=1):
            return True
        return False

    def is_index_linked_certificate(self):
        if 'Linked' in self.account_type.get_title_display():
            return True
        return False

    def is_isa(self):
        if self.account_type.all().exists():
            for bestbuy in self.account_type.all():
                if 'isa' in str(bestbuy.title).lower():
                    return True
        return False

    def save(self, *args, **kwargs):
        super(RatetrackerReminder, self).save(*args, **kwargs)
        from products.tasks import sync_ratetracker_reminder
        sync_ratetracker_reminder.apply_async([self.pk], countdown=1)


class ProductManager(models.Manager):
    def refine_by_balance(self, balance):
        return super(ProductManager, self).get_query_set().filter(Q(minimum__lte=balance) & Q(maximum__gte=balance))


class Product(BaseModel):
    """This is the documentation for a product."""

    product_manager = ProductManager()
    objects = models.Manager()

    sc_code = models.CharField(max_length=10, help_text="This is Savings Champion unique identifier for this product",
                               unique=True)
    publish_after = models.DateField(blank=True, null=True,
                                     help_text="We omit products from searches if there publish date is in the future")

    ACCOUNT_TYPE_OPTIONS = (
        ('P', 'Personal'),
        ('p', 'Personal'),
        ('B', 'Business'),
        ('b', 'Business'),
        ('C', 'Charity'),
        ('c', 'Charity'),
        ('O', 'Unknown')
    )

    account_type = models.CharField(choices=ACCOUNT_TYPE_OPTIONS, verbose_name='Account Type', max_length=1,
                                    default='P')
    provider = models.ForeignKey('Provider', related_name='products')
    minimum = models.IntegerField(verbose_name="Minimum Deposit", blank=True, null=True, default=0)
    maximum = models.IntegerField(verbose_name="Maximum Deposit", blank=True, null=True, default=0)
    minimum_monthly = models.IntegerField(blank=True, null=True, default=0)  #
    maximum_monthly = models.IntegerField(blank=True, null=True, default=0)
    aer = models.DecimalField(decimal_places=4, max_digits=7, blank=True, null=True)
    gross_rate = models.DecimalField(decimal_places=4, max_digits=7, blank=True, null=True)
    monthly_gross = models.DecimalField(decimal_places=4, max_digits=7, blank=True, null=True)
    # TODO this will not be right
    net_20 = models.DecimalField(decimal_places=4, max_digits=7, blank=True, null=True)
    net_40 = models.DecimalField(decimal_places=4, max_digits=7, blank=True, null=True)
    # TODO bestbuy type
    bestbuy_type = models.ManyToManyField('BestBuy', related_name='bestbuy_products', null=True, blank=True)
    ratetracker_type = models.CharField(max_length=TODO_LENGTH, null=True, blank=True)

    is_isa_transfers_in = models.BooleanField(default=False, verbose_name="Transfer ISAs in")

    withdrawals = models.CharField(max_length=1000, blank=True, null=True)
    term = models.IntegerField(default=0)
    is_sc_stamp = models.BooleanField(default=False)

    minimum_age = models.IntegerField(null=True, blank=True, default=0)
    maximum_age = models.IntegerField(null=True, blank=True, default=0)

    bbrating_easyaccess = models.IntegerField(null=True, blank=True, verbose_name="Easy Access Best Buy Rating",
                                              default=0)
    bbrating_fixedrate_bonds = models.IntegerField(null=True, blank=True,
                                                   verbose_name="Fixed Rate Bonds Best Buy Rating", default=0)
    bbrating_variable_isa = models.IntegerField(null=True, blank=True, verbose_name="Variable ISA Best Buy Rating",
                                                default=0)
    bbrating_fixed_isa = models.IntegerField(null=True, blank=True, verbose_name="Fixed ISA Best Buy Rating", default=0)
    bbrating_notice = models.IntegerField(null=True, blank=True, verbose_name="Notice Accounts Best Buy Rating",
                                          default=0)
    bbrating_over50 = models.IntegerField(null=True, blank=True, verbose_name="Over 50s Best Buy Rating", default=0)
    bbrating_monthly_income = models.IntegerField(null=True, blank=True, verbose_name="Monthly Income Best Buy Rating",
                                                  default=0)
    bbrating_regularsavings = models.IntegerField(null=True, blank=True, verbose_name="Regular Savings Best Buy Rating",
                                                  default=0)
    bbrating_childrenssavings = models.IntegerField(null=True, blank=True,
                                                    verbose_name="Children Savings Best Buy Rating", default=0)
    bbrating_variable_bond = models.IntegerField(null=True, blank=True, verbose_name="Variable Bonds Best Buy Rating",
                                                 default=0)
    bbrating_highinterestcurrentaccount = models.IntegerField(null=True, blank=True,
                                                              verbose_name="High Interest Current Account Best Buy Rating",
                                                              default=0)

    bonus_amount = models.DecimalField(decimal_places=4, max_digits=7, default=0)
    underlying_gross_rate = models.DecimalField(decimal_places=4, max_digits=7, default=0)

    notice = models.IntegerField(null=True, blank=True, default=0)

    # for syncing with sales force, we will start to group together tiers by a Salesforce id
    # TODO index on this
    sf_product_id = models.CharField(max_length=255, blank=True, null=True)
    is_fixed = models.BooleanField(default=False, blank=True)

    master_product = models.ForeignKey('MasterProduct', related_name="master_product", blank=True, null=True)

    exclude_from_api_for = models.ManyToManyField(ApiExcludedItem, blank=True, null=True)


    @property
    def status(self):
        """
        Allows old code to access status via the product tier

        :return: string
        """
        if settings.DEBUG:
            logger.warning('a Product object handled a read for status', extra={
                'stack': True,
            })
        return self.master_product.status

    @property
    def verdict(self):
        """
        Allows old code to access verdict via the product tier

        :return: string
        """
        if settings.DEBUG:
            logger.warning('a Product object handled a read for verdict', extra={
                'stack': True,
            })
        return self.master_product.verdict

    @property
    def url(self):
        """
        Allows old code to access url via the product tier

        :return: string
        """
        if settings.DEBUG:
            logger.warning('a Product object handled a read for url', extra={
                'stack': True,
            })
        return self.master_product.url

    @property
    def facts(self):
        if settings.DEBUG:
            logger.warning('a Product object handled a read for facts', extra={
                'stack': True,
            })
        return self.master_product.facts

    @facts.setter
    def facts(self, value):
        if settings.DEBUG:
            logger.warning('a Product object handled a write for facts', extra={
                'stack': True,
            })
        self.master_product.facts = value
        self.master_product.save()

    @property
    def fscs_licence(self):
        """
        Allows old code to access fscs_licence via the product tier

        :return: string
        """
        if settings.DEBUG:
            logger.warning('a Product object handled a read for fscs_licence', extra={
                'stack': True,
            })
        return self.provider.fscs_limit_type.name

    @property
    def is_paid(self):
        if settings.DEBUG:
            logger.warning('a Product object handled a read for is_paid', extra={
                'stack': True,
            })
        return self.master_product.is_paid

    @is_paid.setter
    def is_paid(self, value):
        # Coerced to a boolean value due to salesforce import returning None for their tickboxes if not set manually
        if settings.DEBUG:
            logger.warning('a Product object handled a write for is_paid', extra={
                'stack': True,
            })
        self.master_product.is_paid = bool(value)
        self.master_product.save()

    @property
    def bonus_term(self):
        if settings.DEBUG:
            logger.warning('a Product object handled a read for bonus_term', extra={
                'stack': True,
            })
        return self.master_product.bonus_term

    @bonus_term.setter
    def bonus_term(self, value):
        if settings.DEBUG:
            logger.warning('a Product object handled a write for bonus_term', extra={
                'stack': True,
            })
        self.master_product.bonus_term = value
        self.master_product.save()

    @property
    def bonus_end_date(self):
        if settings.DEBUG:
            logger.warning('a Product object handled a read for bonus_end_date', extra={
                'stack': True,
            })
        return self.master_product.bonus_end_date

    @bonus_end_date.setter
    def bonus_end_date(self, value):
        if settings.DEBUG:
            logger.warning('a Product object handled a write for bonus_end_date', extra={
                'stack': True,
            })
        self.master_product.bonus_end_date = value
        self.master_product.save()

    def __unicode__(self):
        return u'Provider: %s | Product: %s' % (self.provider.title, self.title)

    class Meta:
        get_latest_by = 'publish_after'

    def get_gross_rate(self):
        if self.gross_rate:
            return self.gross_rate
        return 0

    def get_account_type(self):
        if self.account_type is not None:
            try:
                for option in self.ACCOUNT_TYPE_OPTIONS:
                    if option[0] == self.account_type:
                        return option[1]
            except ValueError:
                pass

        return ''

    def get_term(self):
        if self.term:
            try:
                term = int(self.term)
                if term % 12 == 0:
                    if (term / 12) >= 2:
                        return '%s years' % (term / 12)
                    return '%s year' % (term / 12)
                return '%s months' % term
            except ValueError:
                pass

        return ''

    def get_gross_rate_percent(self):
        if self.gross_rate:
            return self.gross_rate
        return 0

    def get_aer_percent(self):
        if self.aer:
            return self.aer
        return 0

    def show_opening_date(self):
        """
        Not totally the right place for it
        """
        if self.bonus_end_date in EMPTY_VALUES or self.bonus_term > 0:
            return True
        return False

    def fixed_bonus_not_expired(self):
        if self.bonus_end_date not in EMPTY_VALUES:
            if self.bonus_end_date > datetime.datetime.now().date():
                return True
        return False

    def fixed_bonus_has_expired(self):
        if self.bonus_end_date not in EMPTY_VALUES:
            if self.bonus_end_date < datetime.datetime.now().date():
                return True
        return False

    def get_rate(self, opening_date=None):
        """
        Returns the rate of the product based on whether it has expired or not"
        """

        if self.bonus_end_date:
            if self.bonus_end_date < datetime.datetime.now().date():
                return self.underlying_gross_rate
            else:
                return self.gross_rate

        if self.bonus_term > 0:
            if opening_date is not None:
                bonus_term_plus_one = self.bonus_term + 1
                expiry_date = opening_date + relativedelta(months=bonus_term_plus_one)
            else:
                return self.underlying_gross_rate
            if expiry_date < datetime.datetime.now().date():
                return self.underlying_gross_rate
            else:
                return self.gross_rate
        return self.gross_rate

    @staticmethod
    def get_bestbuy_fields():
        """ return a list of bestby bestbuy_fields (without the prefix) as strings """
        bestbuy_fields = ['bbrating_easyaccess',
                          'bbrating_variable_isa',
                          'bbrating_easyaccess',
                          'bbrating_fixedrate_bonds',
                          'bbrating_variable_isa',
                          'bbrating_fixed_isa',
                          'bbrating_notice',
                          'bbrating_over50',
                          'bbrating_monthly_income',
                          'bbrating_regularsavings',
                          'bbrating_childrenssavings',
                          'bbrating_variable_bond',
                          'bbrating_highinterestcurrentaccount'
                          ]
        return bestbuy_fields

    @staticmethod
    def get_ordering(bb_slug):
        bb_slug = bb_slug.lower()
        if bb_slug.find('easy') > -1:
            return 'bbrating_easyaccess'
        elif bb_slug.find('fixed-rate-bond') > -1:
            return 'bbrating_fixedrate_bonds'
        elif bb_slug.find('fixed-rate-isa') > -1:
            return 'bbrating_fixed_isa'
        elif bb_slug.find('notice') > -1:
            return 'bbrating_notice'
        elif bb_slug.find('monthly') > -1:
            return 'bbrating_monthly_income'
        elif bb_slug.find('regular') > -1:
            return 'bbrating_regularsavings'
        elif bb_slug.find('children') > -1:
            return 'bbrating_childrenssavings'
        elif bb_slug.find('variable-bond') > -1:
            return 'bbrating_variable_bond'
        elif bb_slug.find('variable-rate-isa') > -1:
            return 'bbrating_variable_isa'
        elif bb_slug.find('high-interest-current-account') > -1:
            return 'bbrating_highinterestcurrentaccount'
        return 'title'

    def calculate_amount(self, initial_amount, iterations=11):
        i = 0
        retval = initial_amount
        if self.gross_rate:
            while i < 11:
                retval += retval * self.gross_rate
                i += 1
        return retval

    def get_access(self):
        access = []
        if self.master_product.is_post_access:
            access.append('Post')
        if self.master_product.is_internet_access:
            access.append('Online')
        if self.master_product.is_branch_access:
            access.append('Branch')
        if self.master_product.is_phone_access:
            access.append('Phone')

        return ", ".join(access)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Product, self).save(*args, **kwargs)

    def is_isa(self):
        if self.bestbuy_set.all().exists():
            for bestbuy in self.bestbuy_set.all():
                if 'isa' in str(bestbuy.title).lower():
                    return True
        return False


class BestBuy(models.Model):
    BESTBUY_TITLE_DISPLAY_CHOICES = (
        ('High Interest Current Accounts', 'High Interest Current Accounts'),
        ('Current Accounts', 'High Interest Current Accounts'),
        ('Easy Access', 'Easy Access'),
        ('Fixed Rate Bonds', 'Fixed Rate Bonds'),
        ('Variable Rate ISAs', 'Variable Rate ISAs'),
        ('Fixed Rate ISAs', 'Fixed Rate ISAs'),
        ('Notice Accounts', 'Notice Accounts'),
        ('Monthly Income', 'Monthly Income'),
        ('Regular Savings', 'Regular Savings'),
        ('Children\'s Accounts', 'Children\'s Accounts'),
        ('Junior ISA', 'Junior ISAs'),
        ('Index Linked Certificate', 'Index Linked Certificate'),
        ('Variable Rate Bond', 'Variable Rate Bond'),
        ('Sharia Accounts', 'Sharia Accounts'),
        ('Help to Buy ISA', 'Help to Buy ISAs'),
    )

    BESTBUY_CLIENT_TYPE_CHOICES = (
        ( 'p', 'Personal'),
        ( 'b', 'Business'),
        ( 'c', 'Charity'),

    )

    title = models.CharField(max_length=TODO_LENGTH,
                             choices=BESTBUY_TITLE_DISPLAY_CHOICES)
    slug = models.CharField(max_length=TODO_LENGTH,
                            help_text="""The slug is a url encoded version of your title and is used to create the web address""")

    created_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)

    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               null=True,
                               blank=True,
                               help_text="""The author's name appears as a citation against the description""")

    meta_description = models.CharField(max_length=200,
                                        blank=True,
                                        null=True,
                                        verbose_name='Tables Meta Description')
    comparison_meta_description = models.CharField(max_length=200,
                                                   blank=True,
                                                   null=True,
                                                   verbose_name='Comparison Page Meta Description')

    description = models.TextField(blank=True,
                                   help_text="""Please enter a short description describing the Best Buy type""")
    landing_page_description = models.TextField(blank=True,
                                                help_text="""Please enter a short description describing the Best Buy type""")
    order = models.IntegerField(blank=True,
                                null=True,
                                help_text="""You can affect the ordering of the Best Buys by adding in a number here, we order from smallest to largest.""")

    products = models.ManyToManyField('Product',
                                      through='Ranking')
    has_table = models.BooleanField(default=False,
                                    verbose_name="Show best buy table?")

    tips = models.TextField(blank=True)
    is_fixed = models.NullBooleanField(blank=True,
                                       null=True,
                                       default=False)
    is_bond = models.BooleanField(default=False)
    is_isa = models.BooleanField(default=False)
    ratetracker_enabled = models.NullBooleanField(blank=True,
                                                  null=True,
                                                  default=False,
                                                  verbose_name="Show on Rate Tracker")
    client_type = models.CharField(max_length=3, choices=BESTBUY_CLIENT_TYPE_CHOICES, default='p')

    class Meta:
        ordering = ('order',)

    def get_bestbuy_table(self):
        bestbuy_type = self.get_client_type_display().lower()
        bestbuy_overview = "{bestbuy_type}_table".format(bestbuy_type=bestbuy_type)
        return reverse(bestbuy_overview, kwargs={'bestbuy_slug': self.slug})

    def get_personal_products(self, ratetracker=False, balance=None, exclude_hidden=True, term=None, external=False,
                              old_order_by=True):
        if 'ISA' in self.get_title_display() and ratetracker:
            products = self.products.filter(link_to_products__date_replaced=None,
                                            master_product__account_type__iexact='P',
                                            is_isa_transfers_in=True)
        else:
            products = self.products.filter(master_product__account_type__iexact='P',
                                            link_to_products__date_replaced=None)
        if balance is not None:
            products = products.filter(maximum__gte=balance,
                                       minimum__lte=balance)
        if exclude_hidden:
            products = products.exclude(link_to_products__hidden=True)
        if term is not None:
            products = products.filter(link_to_products__term=term)
        if external:
            products = products.filter(link_to_products__rank=0)
        if old_order_by:
            products = products.order_by('link_to_products')
        return products.select_related('products__provider', 'link_to_products')

    def get_business_products(self, ratetracker=False, balance=None, exclude_hidden=True, term=None, external=False,
                              old_order_by=True):

        products = self.products.filter(master_product__account_type__icontains='B',
                                        link_to_products__date_replaced=None)
        if balance is not None:
            products = products.filter(maximum__gte=balance,
                                       minimum__lte=balance)
        if exclude_hidden:
            products = products.exclude(link_to_products__hidden=True)
        if term is not None:
            products = products.filter(link_to_products__term=term)
        if external:
            products = products.filter(link_to_products__rank=0)
        if old_order_by:
            products = products.order_by('link_to_products')
        return products.select_related('products__provider', 'link_to_products')

    def get_pros(self):
        return self.advantagesblock_set.filter(type='pro')

    def __str__(self):
        return self.get_title_display()

    def __unicode__(self):
        return u'%s' % self.get_title_display()

    def save(self, *args, **kwargs):
        if self.slug in EMPTY_VALUES:
            unicode_string = unicode(self.get_title_display())
            self.slug = better_slugify(unicode_string)
        super(BestBuy, self).save(*args, **kwargs)


class TrustTypes(models.Model):
    uuid = UUIDField(primary_key=True)
    title = models.TextField(default='')


class InterestPaidFrequency(models.Model):
    uuid = UUIDField(primary_key=True)
    title = models.TextField(default='')


class MasterProduct(BaseModel):
    sf_product_id = models.CharField(max_length=255, unique=True)
    provider = models.ForeignKey('Provider', related_name='master_products', blank=True, null=True)
    status = models.CharField(max_length=20, default='Default')
    bestbuy_type = models.ManyToManyField('BestBuy', blank=True, null=True)

    ACCOUNT_TYPE_OPTIONS = (
        ('P', 'Personal'),
        ('p', 'Personal'),
        ('B', 'Business'),
        ('b', 'Business'),
        ('C', 'Charity'),
        ('c', 'Charity'),
        ('O', 'Unknown')
    )

    account_type = models.CharField(choices=ACCOUNT_TYPE_OPTIONS, verbose_name='Account Type', max_length=1,
                                    default='P')

    available_from = models.DateField(blank=True, null=True)
    available_to = models.DateField(blank=True, null=True)

    is_internet_access = models.BooleanField(default=False, verbose_name="Internet Access")
    is_phone_access = models.BooleanField(default=False, verbose_name="Telephone Access")
    is_post_access = models.BooleanField(default=False, verbose_name="Post Access")
    is_branch_access = models.BooleanField(default=False, verbose_name="Branch Access")
    is_cc_access = models.BooleanField(default=False, verbose_name="Cash Card Access")

    is_open_internet = models.BooleanField(default=False, verbose_name="Can it be opened via the internet")
    is_open_telephone = models.BooleanField(default=False, verbose_name="Can it be opened via the phone")
    is_open_post = models.BooleanField(default=False, verbose_name="Can it be opened through the post")
    is_open_branch = models.BooleanField(default=False, verbose_name="Can it be opened through the post")
    is_open_cc = models.BooleanField(default=False, verbose_name="Can it be opened via a cash card")

    is_isa_transfers_in = models.BooleanField(default=False, verbose_name="Transfer ISAs in")

    is_fixed = models.BooleanField(default=False, blank=True)

    facts = MarkupField(default='', markup_type='markdown')
    fscs_licence = models.CharField(max_length=TODO_LENGTH, blank=True, null=True)

    term = models.IntegerField(default=0)
    term_fixed_date = models.DateField(null=True, blank=True)

    notice = models.IntegerField(default=0)

    shariaa = models.BooleanField(default=False)

    existing_only = models.BooleanField(default=False)
    locals_only = models.BooleanField(default=False)

    operating_balance = models.DecimalField(default=0, decimal_places=10, max_digits=18)
    operating_balance_rate = models.DecimalField(default=0, decimal_places=10, max_digits=18)

    other_reason_to_exclude_this_product = models.TextField(default='', blank=True)
    other_reason_compliance_checked = models.BooleanField(default=False)

    trust_funds_accepted = models.BooleanField(default=False)
    trust_types_excluded = models.ManyToManyField(TrustTypes)

    interest_paid_frequency = models.ManyToManyField(InterestPaidFrequency)

    minimum_age = models.IntegerField(null=True, blank=True, default=0)
    maximum_age = models.IntegerField(null=True, blank=True, default=0)

    # This is the monthly amount required to keep the account open / retain the bonus
    minimum_monthly = models.DecimalField(default=0, blank=True, decimal_places=3, max_digits=18)
    maximum_monthly = models.DecimalField(default=0, blank=True, decimal_places=3, max_digits=18)

    open_limit_total = models.IntegerField(default=-1)
    open_limit_own_name = models.IntegerField(default=-1)
    open_limit_joint_name = models.IntegerField(default=-1)

    bonus_term = models.IntegerField(default=0)

    bonus_end_date = models.DateField(null=True, blank=True)

    exclude_from_api_for = models.ManyToManyField(ApiExcludedItem, blank=True, null=True)

    verdict = models.TextField(blank=True, null=True)

    url = models.URLField(null=True, blank=True, max_length=300)

    is_paid = models.NullBooleanField(default=False)

    moved_to = models.ForeignKey('MasterProduct', null=True, blank=True)

    revert_on_bonus_end = models.BooleanField(default=False)
    revert_on_maturity = models.BooleanField(default=False)

    removal_reason = models.TextField(default='')

    def get_latest_sc_code(self):
        try:
            scList = self.master_product.all().order_by('-sc_code')
            return scList.first()
        except:
            return None

    def get_latest_rate(self, *args, **kwargs):
        return self.get_latest_rate_for_date(date=datetime.datetime.now(), *args, **kwargs)

    def get_latest_rate_for_date(self, balance, opening_date=None, monthly=False, date=None):
        """
        Get the current rate for this product tier, taking into account the balance and if monthly interest is required.

        Also understand the concept of split rate products and will return a blended rate for these products.
        """

        product_tiers = ProductTier.objects.filter(product=self)

        filtered_product_tiers = product_tiers.filter(maximum__gte=balance, minimum__lte=balance,
                                                      publish_after__lte=datetime.datetime.now())

        if filtered_product_tiers.exists():
            latest_product_tier = filtered_product_tiers.latest()

            if latest_product_tier.split_interest:
                if monthly:
                    split_rate = latest_product_tier.get_monthly_rate(opening_date)
                else:
                    split_rate = latest_product_tier.get_rate(opening_date)

                product_tier_balance = balance - latest_product_tier.minimum

                product_tier_return = product_tier_balance * (split_rate / 100)

                lower_tier_maximum = latest_product_tier.minimum - 1
                lower_blended_rate = self.get_latest_rate(balance=lower_tier_maximum, monthly=monthly)
                lower_tiers_return = lower_blended_rate * lower_tier_maximum
                rate = ((product_tier_return + lower_tiers_return) / balance)
                return rate
            else:
                if monthly:
                    return filtered_product_tiers.latest().get_monthly_rate(opening_date)
                return filtered_product_tiers.latest().get_rate(opening_date)
        return Decimal(0)

    def get_latest_product_tier(self, balance):
        now = datetime.datetime.now()
        product_tiers = self.producttier_set.all()
        return product_tiers.filter(maximum__gte=balance, minimum__lte=balance, publish_after__lte=now).latest()

    def get_latest_old_product_tier(self, balance=None):
        old_product_tiers = self.master_product.all()

        # filter the sclist by value and then order it by publish date
        if balance is not None:
            old_product_tiers = old_product_tiers.filter(minimum__lte=balance,
                                                         maximum__gte=balance)

        old_product_tiers = old_product_tiers.filter(publish_after__lt=datetime.datetime.now() + timedelta(days=1),
                                                     is_fixed=False).order_by('title',
                                                                              '-publish_after').filter(
            master_product__status__in=['Live', 'Closed'])

        if old_product_tiers.exists():
            return old_product_tiers.first()
        return None

    def return_product_from_balance(self, value):

        latest_old_product_tier = self.get_latest_old_product_tier(value)

        if latest_old_product_tier is None:
            # They have pushed themselves over or under the tiers so
            # order by max, if balance is over then use the max else use the min.
            old_product_tiers = self.master_product.all()
            old_product_tiers = old_product_tiers.order_by('-maximum', '-publish_after')
            if value < old_product_tiers.first().maximum:
                return old_product_tiers.last()
            return old_product_tiers.first()
        else:
            return latest_old_product_tier

    def return_product(self):

        self.get_latest_old_product_tier()
        if self.master_product.exists():
            scList = self.master_product.filter(publish_after__lte=datetime.datetime.now()).order_by(
                '-publish_after').filter(
                Q(master_product__status__iexact='Live') | Q(master_product__status__iexact='Closed'))
            if scList.exists():
                return scList.values_list('pk', 'master_product__title')[0]

    def return_product_within_balance(self, balance):
        # returns the sccode to migrate a user to if their balance has put them up
        scList = self.master_product.all()

        # filter the sclist by value and then order it by publish date
        balance = Decimal(balance)
        scList = scList.filter(minimum__lte=balance, maximum__gte=balance)
        scList = scList.filter(publish_after__lt=datetime.datetime.now() + timedelta(days=0), is_fixed=False).order_by(
            'title', '-publish_after').filter(Q(master_product__status='Live') | Q(master_product__status='Closed'))

        if scList.exists():
            return scList.values_list('pk', 'title')[0]
        return None

    def get_outside_balance(self, balance):
        min = self.master_product.all().order_by('minimum')[0].minimum
        max = self.master_product.all().order_by('maximum').reverse()[0].maximum
        if balance < min or balance > max:
            return True

        return False

    def get_latest_monthly_rate(self, value, opening_date=None):
        scList = self.master_product.all()

        # filter the sclist by value and then order it by publish date
        scList = scList.filter(Q(minimum__lte=value) & Q(maximum__gte=value))
        scList = scList.filter(publish_after__lt=datetime.datetime.now() + timedelta(days=1), is_fixed=False).order_by(
            'title', '-publish_after').filter(Q(master_product__status='Live') | Q(master_product__status='Closed'))

        if not scList:
            # they have pushed themselves over or under the tiers so
            # order by max, if balance is over then use the max else use the min.
            scList = self.master_product.all()
            scList = scList.order_by('-maximum')
            if not value > scList[0].maximum:
                scList = scList.order_by('maximum')

        return scList[0].monthly_gross

    @cached_property
    def get_bestbuy_type(self):
        return self.bestbuy_type.first()

    @cached_property
    def get_account_type(self):
        if self.account_type is not None:
            return self.account_type.upper()
        else:
            return 'P'


class Ranking(models.Model):
    RANKING_TERMS = (
        (0, 'No Term'),
        (1, 'up to 1 Year'),
        (2, '1-2 Years'),
        (3, '2-3 Years'),
        (4, '3-4 Years'),
        (5, '5 Years and over')
    )

    product = models.ForeignKey('Product', related_name='link_to_products')
    bestbuy = models.ForeignKey('BestBuy')
    rank = models.IntegerField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, default=datetime.datetime.now)
    date_replaced = models.DateTimeField(null=True, blank=True)
    hidden = models.BooleanField(default=False)
    term = models.PositiveSmallIntegerField(default=0, choices=RANKING_TERMS)

    class Meta:
        ordering = ('bestbuy__title', 'term', 'rank', '-date_replaced')
        app_label = 'products'
        unique_together = (('product', 'bestbuy', 'date_replaced'), ('rank', 'term', 'bestbuy', 'date_replaced'))

    def __str__(self):
        status = "Replaced: {replaced}".format(
            replaced=self.date_replaced.strftime('%Y-%m-%d %H:%M:%s')) if self.date_replaced is not None else 'Current'
        return " - ".join([self.bestbuy.get_title_display(), str(self.rank), status])

    @staticmethod
    @atomic
    def replace():
        current_rankings = Ranking.objects.filter(date_replaced=None)

        time_replaced = datetime.datetime.now()
        for ranking in current_rankings:
            old_pk = ranking.pk
            ranking.pk = None
            ranking.date_replaced = time_replaced
            try:
                ranking.save()
            except IntegrityError:
                logger.error('Ranking.replace() - Error duplicating ranking {id}'.format(id=old_pk))
            ranking.pk = old_pk
            ranking.date_replaced = None
            ranking.date_created = time_replaced
            try:
                ranking.save()
            except IntegrityError:
                logger.error('Ranking.replace() - Error creating duplicate ranking {id}'.format(id=old_pk))


class AdvantagesBlock(models.Model):
    bestbuy = models.ForeignKey('BestBuy')

    TYPE_CHOICES = (
        ('pro', 'Pro'),
        ('con', 'Con'),
    )

    type = models.CharField(max_length=20, choices=TYPE_CHOICES, blank=True)
    text = models.CharField(max_length=500, blank=True)


EMAIL_TIMEFRAME = (
    # (1, 'Daily'),
    (2, 'Deliver Weekly'),
    (3, 'Deliver Monthly'),
)


class WeeklyRateAlert(models.Model):
    uuid = UUIDField(primary_key=True)
    email = models.EmailField()
    signup_date = models.DateTimeField(auto_now_add=True)
    frequency = models.IntegerField(choices=EMAIL_TIMEFRAME, default=2)

    def save(self, *args, **kwargs):
        super(WeeklyRateAlert, self).save(*args, **kwargs)


class WeeklyBusinessRateAlert(models.Model):
    uuid = UUIDField(primary_key=True)
    email = models.EmailField()
    signup_date = models.DateTimeField(auto_now_add=True)
    frequency = models.IntegerField(choices=EMAIL_TIMEFRAME, default=2)

    def save(self, *args, **kwargs):
        super(WeeklyBusinessRateAlert, self).save(*args, **kwargs)


class FSCSLimitType(models.Model):
    uuid = UUIDField(primary_key=True)
    name = models.TextField()
    balance_limit = models.DecimalField(decimal_places=3, max_digits=19, default=0)
    balance_unlimited = models.BooleanField(default=False)
    currency_code = models.TextField(default='GBP')
    multiplier_if_joint = models.DecimalField(default=Decimal(2), decimal_places=3, max_digits=19)

    def __str__(self):
        return self.name


class ProductTierManager(models.Manager):
    def refine_by_balance(self, balance):
        return super(ProductTierManager, self).get_query_set().filter(Q(minimum__lte=balance) & Q(maximum__gte=balance))


class ProductTier(BaseModel):
    """This is the documentation for a product."""
    uuid = UUIDField(primary_key=True)
    product_tier_manager = ProductTierManager()
    objects = models.Manager()

    sc_code = models.CharField(max_length=10, help_text="This is Savings Champion unique identifier for this product",
                               unique=True)
    publish_after = models.DateField(blank=True, null=True,
                                     help_text="We omit products from searches if their publish date is in the future")

    available_until = models.DateField(blank=True, null=True,
                                       help_text="This product tier couldn't be opened past this date.")

    ACCOUNT_TYPE_OPTIONS = (
        ('P', 'Personal'),
        ('p', 'Personal'),
        ('B', 'Business'),
        ('b', 'Business'),
        ('C', 'Charity'),
        ('c', 'Charity'),
        ('O', 'Unknown')
    )

    provider = models.ForeignKey('Provider', related_name='product_tiers')
    minimum = models.IntegerField(verbose_name="Minimum Deposit", blank=True, null=True, default=0)
    maximum = models.IntegerField(verbose_name="Maximum Deposit", blank=True, null=True, default=0)
    minimum_monthly = models.IntegerField(blank=True, null=True, default=0)
    maximum_monthly = models.IntegerField(blank=True, null=True, default=0)
    aer = models.DecimalField(decimal_places=4, max_digits=7, blank=True, default=0)
    gross_rate = models.DecimalField(decimal_places=4, max_digits=7, default=0)
    monthly_gross = models.DecimalField(decimal_places=4, max_digits=7, blank=True, default=0)
    # TODO this will not be right
    net_20 = models.DecimalField(decimal_places=4, max_digits=7, blank=True, default=0)
    net_40 = models.DecimalField(decimal_places=4, max_digits=7, blank=True, default=0)
    # TODO bestbuy type
    # bestbuy_type = models.ManyToManyField('products.BestBuy', related_name='bestbuy_product_tiers', null=True, blank=True)
    ratetracker_type = models.TextField(blank=True, null=True)

    is_internet_access = models.BooleanField(default=False, verbose_name="Internet Access")
    is_phone_access = models.BooleanField(default=False, verbose_name="Telephone Access")
    is_post_access = models.BooleanField(default=False, verbose_name="Post Access")
    is_branch_access = models.BooleanField(default=False, verbose_name="Branch Access")
    is_cc_access = models.BooleanField(default=False, verbose_name="Cash Card Access")

    is_open_internet = models.BooleanField(default=False, verbose_name="Can it be opened via the internet")
    is_open_telephone = models.BooleanField(default=False, verbose_name="Can it be opened via the phone")
    is_open_post = models.BooleanField(default=False, verbose_name="Can it be opened through the post")
    is_open_branch = models.BooleanField(default=False, verbose_name="Can it be opened through a branch")
    is_open_cc = models.BooleanField(default=False, verbose_name="Cash Card")

    is_isa_transfers_in = models.BooleanField(default=False, verbose_name="Transfer ISAs in")

    withdrawals = models.TextField(blank=True, null=True)
    # TODO check the type here
    fscs_licence = models.TextField(blank=True, null=True)
    is_sc_stamp = models.BooleanField(default=False)

    # Are SC paid commission for this product?
    is_paid = models.BooleanField(default=False)

    bbrating_easyaccess = models.IntegerField(null=True, blank=True, verbose_name="Easy Access Best Buy Rating",
                                              default=0)
    bbrating_fixedrate_bonds = models.IntegerField(null=True, blank=True,
                                                   verbose_name="Fixed Rate Bonds Best Buy Rating", default=0)
    bbrating_variable_isa = models.IntegerField(null=True, blank=True, verbose_name="Variable ISA Best Buy Rating",
                                                default=0)
    bbrating_fixed_isa = models.IntegerField(null=True, blank=True, verbose_name="Fixed ISA Best Buy Rating", default=0)
    bbrating_notice = models.IntegerField(null=True, blank=True, verbose_name="Notice Accounts Best Buy Rating",
                                          default=0)
    bbrating_over50 = models.IntegerField(null=True, blank=True, verbose_name="Over 50s Best Buy Rating", default=0)
    bbrating_monthly_income = models.IntegerField(null=True, blank=True, verbose_name="Monthly Income Best Buy Rating",
                                                  default=0)
    bbrating_regularsavings = models.IntegerField(null=True, blank=True, verbose_name="Regular Savings Best Buy Rating",
                                                  default=0)
    bbrating_childrenssavings = models.IntegerField(null=True, blank=True,
                                                    verbose_name="Children Savings Best Buy Rating", default=0)
    bbrating_variable_bond = models.IntegerField(null=True, blank=True, verbose_name="Variable Bonds Best Buy Rating",
                                                 default=0)
    bbrating_highinterestcurrentaccount = models.IntegerField(null=True, blank=True,
                                                              verbose_name="High Interest Current Account Best Buy Rating",
                                                              default=0)

    bonus_amount = models.DecimalField(decimal_places=4, max_digits=7, blank=True, null=True)
    underlying_gross_rate = models.DecimalField(decimal_places=4, max_digits=7, default=0)
    url = models.URLField(null=True, blank=True, max_length=300)

    sf_product_tier_id = models.CharField(max_length=255, unique=True)
    is_fixed = models.BooleanField(default=False, blank=True)

    product = models.ForeignKey('MasterProduct', blank=True, null=True)
    verdict = models.TextField(blank=True, null=True)

    joint_account_only = models.BooleanField(default=False)

    tier_type = models.TextField(default='', blank=True)

    # Denotes a split interest tier which uses interest rates from lower balances
    split_interest = models.NullBooleanField(default=False)

    exclude_from_api_for = models.ManyToManyField(ApiExcludedItem, blank=True, null=True)

    def __unicode__(self):
        try:
            return u'Provider: %s | Product: %s' % (self.provider.title, self.product.title)
        except:
            return u'%s' % self.title

    class Meta:
        get_latest_by = 'publish_after'

    def get_gross_rate(self):
        if self.gross_rate:
            return self.gross_rate / 100
        return 0

    @property
    def maximum_age(self):
        if settings.DEBUG:
            logger.warning('a ProductTier object handled a read for maximum_age', extra={
                'stack': True,
            })
        return self.product.maximum_age

    @property
    def minimum_age(self):
        if settings.DEBUG:
            logger.warning('a ProductTier object handled a read for minimum_age', extra={
                'stack': True,
            })
        return self.product.minimum_age

    @property
    def notice(self):
        if settings.DEBUG:
            logger.warning('a ProductTier object handled a read for notice', extra={
                'stack': True,
            })
        return self.product.notice

    @property
    def term(self):
        if settings.DEBUG:
            logger.warning('a ProductTier object handled a read for term', extra={
                'stack': True,
            })
        return self.product.term

    @property
    def existing_only(self):
        if settings.DEBUG:
            logger.warning('a ProductTier object handled a read for existing_only', extra={
                'stack': True,
            })

        return self.product.existing_only

    @property
    def locals_only(self):
        if settings.DEBUG:
            logger.warning('a ProductTier object handled a read for locals_only', extra={
                'stack': True,
            })

        return self.product.locals_only

    @property
    def term_fixed_date(self):
        if settings.DEBUG:
            logger.warning('a ProductTier object handled a read for term_fixed_date', extra={
                'stack': True,
            })

        return self.product.term_fixed_date

    @property
    def account_type(self):
        if settings.DEBUG:
            logger.warning('a ProductTier object handled a read for account_type', extra={
                'stack': True,
            })

        return self.product.account_type

    @account_type.setter
    def account_type(self, value):
        if settings.DEBUG:
            logger.warning('a ProductTier object handled a save for account_type', extra={
                'stack': True,
            })

        self.product.account_type = value
        self.product.save()

    @property
    def status(self):
        if settings.DEBUG:
            logger.warning('a ProductTier object handled a read for status', extra={
                'stack': True,
            })

        return self.product.status

    @status.setter
    def status(self, value):
        if settings.DEBUG:
            logger.warning('a ProductTier object handled a save for status', extra={
                'stack': True,
            })

        self.product.status = value
        self.product.save()

    @property
    def facts(self):
        if settings.DEBUG:
            logger.warning('a ProductTier object handled a read for facts', extra={
                'stack': True,
            })

        return self.product.facts

    @facts.setter
    def facts(self, value):
        if settings.DEBUG:
            logger.warning('a ProductTier object handled a save for facts', extra={
                'stack': True,
            })
        self.product.facts = value
        self.product.save()

    @property
    def bonus_term(self):
        if settings.DEBUG:
            logger.warning('a ProductTier object handled a read for bonus_term', extra={
                'stack': True,
            })
        return self.product.bonus_term

    @bonus_term.setter
    def bonus_term(self, value):
        if settings.DEBUG:
            logger.warning('a ProductTier object handled a save for bonus_term', extra={
                'stack': True,
            })
        self.product.bonus_term = value
        self.product.save()

    @property
    def bonus_end_date(self):
        if settings.DEBUG:
            logger.warning('a ProductTier object handled a read for bonus_end_date', extra={
                'stack': True,
            })
        return self.product.bonus_end_date

    @bonus_end_date.setter
    def bonus_end_date(self, value):
        if settings.DEBUG:
            logger.warning('a ProductTier object handled a save for bonus_end_date', extra={
                'stack': True,
            })
        self.product.bonus_end_date = value
        self.product.save()

    def get_account_type(self):
        if self.account_type is not None:
            try:
                for option in self.ACCOUNT_TYPE_OPTIONS:
                    if option[0] == self.account_type:
                        return option[1]
            except ValueError:
                pass

        return ''

    def get_term(self):
        if self.term:
            try:
                term = int(self.term)
                if term % 12 == 0:
                    return '%s years' % (term / 12)
                return '%s months' % term
            except ValueError:
                pass

        return ''

    def get_gross_rate_percent(self):
        if self.gross_rate:
            return self.gross_rate
        return 0

    def get_aer_percent(self):
        if self.aer:
            return self.aer
        return 0

    def show_opening_date(self):
        if self.bonus_end_date in EMPTY_VALUES or self.bonus_term > 0:
            return True
        return False

    def fixed_bonus_not_expired(self):
        if self.bonus_end_date not in EMPTY_VALUES:
            if self.bonus_end_date > datetime.datetime.now().date():
                return True
        return False

    def fixed_bonus_has_expired(self):
        if self.bonus_end_date not in EMPTY_VALUES:
            if self.bonus_end_date < datetime.datetime.now().date():
                return True
        return False

    def get_rate(self, opening_date=None):
        """
        Returns the rate of the product based on whether it has expired or not
        Takes into account bonus terms
        """

        if self.product.bonus_end_date:
            if self.product.bonus_end_date < datetime.datetime.now().date():
                return self.underlying_gross_rate
            else:
                return self.gross_rate

        if self.product.bonus_term > 0:
            if opening_date is not None:
                bonus_term_plus_one = self.product.bonus_term + 1
                expiry_date = opening_date + relativedelta(months=bonus_term_plus_one)
            else:
                return self.underlying_gross_rate
            if expiry_date < datetime.datetime.now().date():
                return self.underlying_gross_rate
            else:
                return self.gross_rate
        return self.gross_rate

    def get_monthly_rate(self, opening_date=None):
        """
        Returns the rate of the product based on monthly interest, it doesn't understand bonuses yet.
        """
        return self.monthly_gross

    def get_latest_rate(self, balance, monthly=False, opening_date=None):
        """
        Get the current rate for this product tier, taking into account the balance and if monthly interest is required.

        Also understand the concept of split rate products and will return a blended rate for these products.
        """

        if self.split_interest:
            product_tiers = ProductTier.objects.filter(product=self.product)
            filtered_product_tiers = product_tiers.filter(maximum__gte=balance, minimum__lte=balance,
                                                          available_until=None)

            if filtered_product_tiers.exists():
                latest_product_tier = filtered_product_tiers.latest()
                if monthly:
                    split_rate = latest_product_tier.get_monthly_rate(opening_date=opening_date)
                else:
                    split_rate = latest_product_tier.get_rate(opening_date=opening_date)

                product_tier_balance = balance - latest_product_tier.minimum

                product_tier_return = product_tier_balance * split_rate

                lower_tier_maximum = latest_product_tier.minimum - 1
                lower_blended_rate = self.get_latest_rate(balance=lower_tier_maximum, monthly=monthly, opening_date=opening_date)
                lower_tiers_return = lower_blended_rate * lower_tier_maximum

                return ((product_tier_return + lower_tiers_return) / balance) * 100
        else:
            product_tiers = ProductTier.objects.filter(product=self.product)
            filtered_product_tiers = product_tiers.filter(maximum__gte=balance, minimum__lte=balance,
                                                          available_until=None)
            if filtered_product_tiers.exists():
                if monthly:
                    return filtered_product_tiers[0].get_monthly_rate(opening_date=opening_date)
                return filtered_product_tiers[0].get_rate(opening_date=opening_date)
        return Decimal(0)

    def get_bestbuy_type(self, balance=None):
        return self.bestbuy_type.all()[0]

    @staticmethod
    def get_bestbuy_fields():
        """ return a list of bestby bestbuy_fields (without the prefix) as strings """
        bestbuy_fields = ['bbrating_easyaccess',
                          'bbrating_variable_isa',
                          'bbrating_easyaccess',
                          'bbrating_fixedrate_bonds',
                          'bbrating_variable_isa',
                          'bbrating_fixed_isa',
                          'bbrating_notice',
                          'bbrating_over50',
                          'bbrating_monthly_income',
                          'bbrating_regularsavings',
                          'bbrating_childrenssavings',
                          'bbrating_variable_bond',
                          'bbrating_highinterestcurrentaccount'
                          ]
        return bestbuy_fields

    @staticmethod
    def get_ordering(bb_slug):
        bb_slug = bb_slug.lower()
        if bb_slug.find('easy') > -1:
            return 'bbrating_easyaccess'
        elif bb_slug.find('fixed-rate-bond') > -1:
            return 'bbrating_fixedrate_bonds'
        elif bb_slug.find('fixed-rate-isa') > -1:
            return 'bbrating_fixed_isa'
        elif bb_slug.find('notice') > -1:
            return 'bbrating_notice'
        elif bb_slug.find('monthly') > -1:
            return 'bbrating_monthly_income'
        elif bb_slug.find('regular') > -1:
            return 'bbrating_regularsavings'
        elif bb_slug.find('children') > -1:
            return 'bbrating_childrenssavings'
        elif bb_slug.find('variable-bond') > -1:
            return 'bbrating_variable_bond'
        elif bb_slug.find('variable-rate-isa') > -1:
            return 'bbrating_variable_isa'
        elif bb_slug.find('high-interest-current-account') > -1:
            return 'bbrating_highinterestcurrentaccount'
        return 'title'

    def calculate_amount(self, initial_amount, iterations=11):
        i = 0
        retval = initial_amount
        if self.gross_rate:
            while i < 11:
                retval += retval * self.gross_rate
                i += 1
        return retval

    def get_access(self):
        access = []
        if self.product.is_post_access:
            access.append('Post')
        if self.product.is_internet_access:
            access.append('Online')
        if self.product.is_branch_access:
            access.append('Branch')
        if self.product.is_phone_access:
            access.append('Phone')

        return ", ".join(access)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(ProductTier, self).save(*args, **kwargs)

    def is_isa(self):
        if self.bestbuy_set.all().exists():
            for bestbuy in self.bestbuy_set.all():
                if 'isa' in str(bestbuy.title).lower():
                    return True
        return False



class THBToolReminder(models.Model):
    uuid = UUIDField(primary_key=True)
    name = models.TextField(default='')
    email = models.EmailField()
    phone_number = models.TextField(default='')
    reminder_date = models.DateField()
    callback = models.BooleanField(default=False)
    source = models.ForeignKey(Referrer, null=True)
    scheduled_callback = models.BooleanField(default=False)
    sent = models.BooleanField(default=False)

    @staticmethod
    def add_reminder(name, email, deposit_date, callback, source=None, phone_number=''):
        reminder_date = deposit_date + timedelta(weeks=24)
        if source == '':
            source = None
        if source is not None:
            source = Referrer.objects.get(pk=source)

        return THBToolReminder(name=name, email=email, callback=callback, reminder_date=reminder_date, source=source,
                               phone_number=phone_number).save()

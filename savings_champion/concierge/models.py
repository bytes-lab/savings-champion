from datetime import datetime, timedelta
from celery.task import task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django_extensions.db.fields import UUIDField

from common.models import UserReferral
from products.models import Provider, MasterProduct, BestBuy

ADVISER_QUEUE_CHOICES = (
    (0, 'Pending Contact'),
    (1, 'Contacted'),
    (2, 'Fake details'),
    (3, 'Fact Find 1'),
    (4, 'Illustration'),
    (5, 'No Contact'),
    (6, 'No Contact 2'),
    (7, 'No Contact 3'),
    (8, 'Unsuitable'),
    (9, 'Signed Up'),
    (10, 'Emailed'),
    (11, 'Recommendation')
)

PREFERRED_CONTACT_TIME_CHOICES = (
    ('Anytime', 'Anytime (9-5 weekdays)'),
    ('Morning', 'Morning (9-12 weekdays)'),
    ('Afternoon', 'Afternoon (12-5 weekdays)')
)

SOURCE_LIST = (
    ('', ''),
    ('7 Pitfalls', '7 Pitfalls'),
    ('Video 0.1%', 'Video 0.1%'),
    ('Video', 'Video'),
    ('Basket', 'Basket'),
    ('Basket (Concierge)', 'Basket (Concierge)'),
    ('Basket (Healthcheck)', 'Basket (Healthcheck)'),
    ('Basket (Healthcheck and Concierge)', 'Basket (Healthcheck and Concierge)'),
    ('Rate Tracker > 100K', 'Rate Tracker > 100K'),
    ('Inbound Call', 'Inbound Call'),
    ('Referral', 'Referral'),
    ('Trust', 'Trust Concierge'),
    ('Trust Concierge', 'Trust Concierge'),
    ('Charity Concierge', 'Charity Concierge'),
    ('Business Concierge', 'Business Concierge'),
    ('Intermediary', 'Intermediary'),
    ('50 Pound Challenge', '50 Pound Challenge'),
    ('Product Questionnaire', 'Product Questionnaire'),
    ('The Biggest Mistake', 'The Biggest Mistake'),
    ('The Value Of Advice', 'The Value Of Advice'),
    ('THB Tool', 'Temporary High Balance Tool')
)


class AdviserQueue(models.Model):
    uuid = UUIDField(primary_key=True)
    adviser = models.ForeignKey(settings.AUTH_USER_MODEL, null=True)
    name = models.TextField(default='')
    email = models.EmailField(unique=True)
    telephone = models.TextField(default='')
    preferred_contact_time = models.TextField(choices=PREFERRED_CONTACT_TIME_CHOICES, default='Anytime')
    source = models.TextField(default='', choices=SOURCE_LIST)
    status = models.PositiveSmallIntegerField(choices=ADVISER_QUEUE_CHOICES, default=0)
    interaction_started = models.DateTimeField(auto_now_add=True)
    interaction_ended = models.DateTimeField(auto_now=True)
    fee = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    portfolio_value = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    unsuitable_reason = models.TextField(default='')
    _claim_time = models.DecimalField(max_digits=14, decimal_places=0, null=True, blank=True)

    @property
    def claim_time(self):
        if self._claim_time is not None:
            return timedelta(seconds=self._claim_time)
        else:
            return None

    @claim_time.setter
    def claim_time(self, value):
        assert isinstance(value, timedelta)
        self._claim_time = value.total_seconds()

    @staticmethod
    def add_to_queue(email, first_name, last_name, lead_source,
                     telephone_number=None, date_of_birth=None, preferred_contact_time=None):

        from concierge.tasks import register_enquiry

        AdviserQueue.objects.get_or_create(email=email)
        AdviserQueue.objects.filter(email=email).update(
            name='{first_name} {last_name}'.format(first_name=first_name,
                                                   last_name=last_name),
            source=lead_source,
            telephone=telephone_number,
            preferred_contact_time=preferred_contact_time if preferred_contact_time is not None else 'Anytime'
        )

        if date_of_birth is not None:
            date_of_birth = date_of_birth.isoformat()
        User = get_user_model()
        user = User.objects.filter(email=email)

        referrers = []
        if user.exists():
            user_referrals = UserReferral.objects.filter(user=user)
            user_referrers = user_referrals.values('referrer__name')
            referrers = list(user_referrers)
            for referrer in referrers:
                if 'referrer__name' in referrer:
                    if referrer['referrer__name'] is not None:
                        referrer['name'] = referrer['referrer__name']
                    else:
                        referrer['name'] = 'Unknown'
                    del referrer['referrer__name']

        if not referrers:
            referrers = [{'name': 'Unknown'}]

        register_enquiry.apply_async(args=(
            email,
            first_name,
            last_name,
            lead_source,
            referrers,
            str(telephone_number),
            date_of_birth,
            )
        )

    @staticmethod
    def add_note_to_cmt(email, note):
        from concierge.tasks import add_note_to_enquiry
        add_note_to_enquiry.apply_async(args=(email, note))

    class Meta:
        ordering = ['status']
        permissions = (
            ('adviser', 'Is a savings adviser'),
            ('manage_advisers', 'Can manage savings advisers')
        )

    @staticmethod
    def new_lead(email):
        now = datetime.now()
        one_day_back = now - timedelta(days=1)
        return not AdviserQueue.objects.filter(interaction_started__gte=one_day_back,
                                               interaction_started__lte=now,
                                               email__iexact=email).exists()

    def add_note(self, note):
        User = get_user_model()
        if User.objects.filter(email=self.email).exists():
            user = User.objects.get(email=self.email)
            ConciergeUserNotes(user=user, note=note).save()
            return True
        return False


class AdviserQueueHistory(models.Model):
    uuid = UUIDField(primary_key=True)
    adviser_queue = models.ForeignKey(AdviserQueue)
    status = models.PositiveSmallIntegerField(choices=ADVISER_QUEUE_CHOICES, default=0)
    source = models.TextField(default='', choices=SOURCE_LIST)
    date = models.DateTimeField(auto_now_add=True)
    fee = models.DecimalField(max_digits=5, decimal_places=4, default=0)
    portfolio_value = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    unsuitable_reason = models.TextField(default='')


class ConciergeUserPool(models.Model):
    uuid = UUIDField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    term = models.IntegerField(default=None, verbose_name='Maximum Term Length', null=True)
    balance = models.DecimalField(default=0, decimal_places=2, max_digits=19, verbose_name='Required Balance')

    class Meta:
        unique_together = ('user', 'term')

    def __str__(self):
        return "%s %d %s" % (self.user.email, self.term, self.balance)


class ConciergeUserOption(models.Model):
    uuid = UUIDField(primary_key=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    enquiry = models.ForeignKey(AdviserQueue, null=True)
    birth_date = models.DateField(default=datetime(year=1900, month=1, day=1), null=True, blank=True,
                                  verbose_name='To take advantage of age related accounts')
    business = models.BooleanField(default=False, verbose_name='I represent a business')
    charity = models.BooleanField(default=False, verbose_name='I represent a charity')
    child = models.BooleanField(default=False, verbose_name='I represent a child')
    current_accounts = models.BooleanField(default=True, verbose_name='I am open to using current accounts')
    ignore_fscs = models.BooleanField(default=False, verbose_name='I want to ignore FSCS Protection')
    minimum_opening_balance = models.DecimalField(default=0, decimal_places=3, max_digits=19,
                                                  help_text='I will not automatically open an account under this balance (Doesn\'t affect pinned accounts)')
    maximum_opening_balance = models.DecimalField(default=0, decimal_places=3, max_digits=19,
                                                  help_text='I will not automatically open an account over this balance unless it\'s protected (Doesn\'t affect pinned accounts, overridden by provider risks)')
    no_lowest_rate = models.BooleanField(default=False,
                                         help_text='Debug option, Service will not give up once reaching the bottom lowest rate in their existing portfolio.')
    existing_customer = models.BooleanField(default=True, verbose_name='I am an existing customer of a bank')
    local_customer = models.BooleanField(default=True, verbose_name='I am interested in local members accounts')
    shariaa = models.BooleanField(default=False,
                                  verbose_name='I am interested in products where the rate and capital is not guaranteed due to shariaa law')

    open_post = models.BooleanField(default=True, verbose_name='Post')
    open_internet = models.BooleanField(default=True, verbose_name='The Internet')
    open_telephone = models.BooleanField(default=True, verbose_name='Telephone')
    open_branch = models.BooleanField(default=False, verbose_name='Branch')

    access_post = models.BooleanField(default=True, verbose_name='Post')
    access_internet = models.BooleanField(default=True, verbose_name='The Internet')
    access_telephone = models.BooleanField(default=True, verbose_name='Telephone')
    access_branch = models.BooleanField(default=False, verbose_name='Branch')

    use_existing_accounts = models.BooleanField(default=True, verbose_name='I would like to reuse my existing accounts')

    monthly_interest = models.BooleanField(default=False, verbose_name='Monthly interest')

    joint_name = models.BooleanField(default=False, verbose_name='To take advantage of joint accounts')

    dual_portfolio = models.BooleanField(default=False, verbose_name='I represent two people')

    def get_age(self, named_client=True):
        # Get the age of the client, migrating this to use the lead capture data.
        # Will try to use the Concierge Option data if no lead capture data exists
        # todo: Remove birth_date from ConciergeOption
        if ConciergeLeadCapture.objects.filter(user=self.user, named_user=named_client).exists():
            lead_capture = ConciergeLeadCapture.objects.get(user=self.user, named_user=named_client)
            years = datetime.today().year - lead_capture.date_of_birth.year
        elif self.birth_date is not None:
            years = datetime.today().year - self.birth_date.year
        else:
            years = timedelta()
        return years


class ConciergeUserNotes(models.Model):
    uuid = UUIDField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    note = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


class ConciergeUserLicenceRisk(models.Model):
    uuid = UUIDField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    provider = models.ForeignKey(Provider,
                                 help_text="Select any member of the banking licence, the licence owner will be discovered automatically")
    maximum_balance = models.DecimalField(default=0, decimal_places=3, max_digits=19)

    class Meta:
        unique_together = ('user', 'provider')


class ConciergeUserProviderRisk(models.Model):
    uuid = UUIDField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    provider = models.ForeignKey(Provider)
    maximum_balance = models.DecimalField(default=0, decimal_places=3, max_digits=19)

    class Meta:
        unique_together = ('user', 'provider')


class ConciergeUserRemovedProduct(models.Model):
    uuid = UUIDField(primary_key=True)
    concierge_user = models.ForeignKey(ConciergeUserOption)
    master_product = models.ForeignKey(MasterProduct, null=True)

    class Meta:
        unique_together = ('concierge_user', 'master_product')


class ConciergeUserRequiredProduct(models.Model):
    uuid = UUIDField(primary_key=True)
    concierge_user = models.ForeignKey(ConciergeUserOption)
    master_product = models.ForeignKey(MasterProduct, null=True)
    balance = models.DecimalField(max_digits=19, decimal_places=3, default=0)


class EmailTemplate(models.Model):
    uuid = UUIDField(primary_key=True)
    title = models.TextField(default='', unique=True)
    body = models.TextField(default='')

    def __str__(self):
        return self.title


class ConciergeLeadCapture(models.Model):
    EMPLOYMENT_TYPES = (
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time')
    )

    INTEREST_PAYMENT_OPTIONS = (
        ('add', 'Add to accounts'),
        ('move', 'Moved to another account')
    )

    INTEREST_PAYMENT_FREQUENCY = (
        ('monthly', 'Monthly'),
        ('annually', 'Annually')
    )

    JOINT_ACCOUNT_AUTHORITY = (
        ('client1', 'Client1 Only'),
        ('client2', 'Client2 Only'),
        ('either', 'Either Client'),
        ('both', 'Both Clients')
    )

    TAX_BANDS = (
        ('n', 'Non Taxpayer'),
        ('b', 'Basic Rate'),
        ('h', 'Higher Rate'),
        ('a', 'Additional Rate')
    )

    uuid = UUIDField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    title = models.CharField(max_length=10)
    first_name = models.TextField()
    middle_names = models.TextField(null=True, blank=True)
    last_name = models.TextField()
    maiden_name = models.TextField(default='', null=True, blank=True)
    mothers_maiden_name = models.TextField()
    date_of_birth = models.DateField(default=datetime.today)
    place_of_birth = models.TextField()
    address = models.TextField()
    postcode = models.TextField()
    date_moved_in = models.DateField(default=datetime.today)
    country_of_residence = models.TextField()
    uk_resident = models.BooleanField(default=False)
    tax_band = models.CharField(max_length=2, choices=TAX_BANDS, default='b')
    required_gross_interest = models.IntegerField(default=0)
    previous_address = models.TextField()
    months_at_previous_address = models.IntegerField(default=0)
    national_insurance_number = models.CharField(max_length=255)
    passport_number = models.CharField(max_length=255)
    passport_expiry_date = models.DateField(default=datetime.today)
    passport_issue_date = models.DateField(default=datetime.today)
    home_tel_number = models.CharField(max_length=255)
    daytime_tel_number = models.CharField(max_length=255, null=True, blank=True)
    mobile = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField()
    ratetracker_email = models.EmailField()
    occupation = models.CharField(max_length=255)
    employment_status = models.CharField(max_length=255)
    type_of_employment = models.CharField(choices=EMPLOYMENT_TYPES, max_length=10)
    marital_status = models.CharField(max_length=255)
    account_holders_name = models.CharField(max_length=255)
    bank_name = models.CharField(max_length=255)
    bank_sort_code = models.CharField(max_length=255)
    bank_account_number = models.CharField(max_length=255)
    bank_address = models.TextField()
    source_of_assets = models.TextField()
    interest_payment_options = models.CharField(choices=INTEREST_PAYMENT_OPTIONS, max_length=4)
    interest_payment_frequency = models.CharField(choices=INTEREST_PAYMENT_FREQUENCY, max_length=10)
    joint_account_authority = models.CharField(choices=JOINT_ACCOUNT_AUTHORITY, max_length=10)
    contact_providers_allowed = models.BooleanField(default=False)
    temporary_credentials_allowed = models.BooleanField(default=False)
    agree_terms_allowed = models.BooleanField(default=False)
    large_print = models.BooleanField(default=False)
    marketing_allowed = models.BooleanField(default=False)
    notes = models.TextField(null=True, blank=True)
    named_user = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'named_user')


class ConciergeProviderAccountTypeLimitation(models.Model):
    uuid = UUIDField(primary_key=True)
    provider = models.ForeignKey(Provider)
    maximum_balance = models.DecimalField(default=0, decimal_places=3, max_digits=18)
    bestbuys = models.ManyToManyField(BestBuy)

    class Meta:
        verbose_name = 'ConciergeProviderAccountTypeLimit'


class ConciergeUserAcceptedProduct(models.Model):
    RESTRICTIONS = (
        ('open_branch', 'Allowed opening this product in branch'),
        ('open_telephone', 'Allowed opening this product via telephone'),
        ('open_internet', 'Allowed opening this product in internet'),
        ('open_branch', 'Allowed opening this product in post'),

        ('access_post', 'Allowed opening this product in branch'),
        ('access_telephone', 'Allowed opening this product via telephone'),
        ('access_internet', 'Allowed opening this product in internet'),
        ('access_post', 'Allowed opening this product in post'),

        ('existing', 'Allowed opening this product as user is an existing member'),
        ('locals', 'Allowed opening this product as user is a local'),
        ('sharia', 'Allowed opening this Sharia\'a product'),

        ('joint_account', 'Allowed opening this product as a joint account'),
        ('current_account', 'Allowed opening this product as a current account'),

        ('provider_maximum', 'Allowed to open more of this product by provider'),

        ('opening_threshold', 'Allowed opening this product under the users minimum threshold'),
        ('other_reason', 'Allowed opening this product despite other reasons to exclude')
    )

    uuid = UUIDField(primary_key=True)
    concierge_user = models.ForeignKey(ConciergeUserOption)
    product = models.ForeignKey(MasterProduct)
    restriction = models.TextField(choices=RESTRICTIONS)
    accepted = models.BooleanField(default=True)

    class Meta:
        unique_together = ('concierge_user', 'product', 'restriction')

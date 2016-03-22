# coding=utf-8
import datetime
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django_extensions.db.fields import UUIDField
import unicodedata
import re

TODO_LENGTH = 200


class BaseModel(models.Model):
    title = models.CharField(max_length=TODO_LENGTH)
    slug = models.CharField(max_length=TODO_LENGTH,
                            help_text="""The slug is a url encoded version of your title and is used to create the web address""")

    created_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ('title',)
        abstract = True

    def __str__(self):
        return self.title

    def __unicode__(self):
        return u'%s' % self.title

    def save(self, *args, **kwargs):
        if self.slug in EMPTY_VALUES:
            self.slug = better_slugify(self.title)
        super(BaseModel, self).save(*args, **kwargs)

class Referrer(models.Model):
    uuid = UUIDField(primary_key=True)
    name = models.TextField()

    def __str__(self):
        return self.name

class UserReferral(models.Model):
    REFERRAL_ACTION_CHOICES = (
        ('unknown', 'User Performed An Unknown Paid For Action'),
        ('signup', 'User Signed Up'),
        ('rate_tracker', 'User Subscribed To RateTracker'),
        ('rate_tracker_used', 'User has used RateTracker'),
        ('rate_alerts', 'User Subscribed To Rate Alerts'),
        ('newsletter', 'User Subscribed To Newsletter'),
        ('savers_priority_list', 'User Subscribed To The Savers Priority List'),
        ('seven_pitfalls', 'User Signed Up Via Seven Pitfalls To Larger Savers'),
        ('petition', 'User Subscribed To The Petition'),
        ('concierge_enquiry', 'User Enquired About Concierge'),
        ('concierge_client', 'User Signed Up To Concierge'),
        ('recurring_daily_best_buys', 'User Signed Up For Recurring Best Buys - Daily'),
        ('recurring_weekly_best_buys', 'User Signed Up For Recurring Best Buys - Weekly'),
        ('recurring_monthly_best_buys', 'User Signed Up For Recurring Best Buys - Monthly'),
        ('recurring_business_daily_best_buys', 'User Signed Up For Business Recurring Best Buys - Daily'),
        ('recurring_business_weekly_best_buys', 'User Signed Up For Business Recurring Best Buys - Weekly'),
        ('recurring_business_monthly_best_buys', 'User Signed Up For Business Recurring Best Buys - Monthly'),
        ('fifty_pound_challenge', 'User Signed Up For The £50 Challenge'),
        ('the_biggest_mistake', 'User Signed Up For The Biggest Mistake'),
        ('the_value_of_advice', 'User Signed Up For The Value Of Advice'),
        ('tpo_referral', 'User was referred to TPO'),
        ('bj_referral', 'User was referred to Beckford James'),
        ('concierge_pages', 'User signed up via concierge pages'),
        ('iht_guide', 'User requested the IHT Guide'),
        ('pension_options', 'User requested the pension options guide'),
        ('thb_remind_me_fscs', 'User Signed Up For A FSCS Drop Reminder'),
        ('thb_alert_me_fscs', 'User Signed Up For A THB Expiry Reminder'),
        ('thb_book_callback', 'User Signed Up For A THB Callback'),
        ('fake', 'User was marked as fake by the Concierge Advisers')
    )

    REFERRAL_ACTION_CHOICES_FLAT = [x[0] for x in REFERRAL_ACTION_CHOICES]

    uuid = UUIDField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    referrer = models.ForeignKey(Referrer, null=True)
    referral_action = models.CharField(choices=REFERRAL_ACTION_CHOICES, max_length=130, default='unknown')
    referral_term = models.TextField(default='', blank=True)
    referral_campaign = models.TextField(default='', blank=True)
    referral_medium = models.TextField(default='', blank=True)
    referral_date = models.DateTimeField(auto_now_add=True)
    referral_paid = models.BooleanField(default=False)
    referral_paid_date = models.DateTimeField(null=True)
    referrer_from = models.ForeignKey(Referrer, null=True, related_name='referrerfrom')

    def save(self, *args, **kwargs):
        if self.referrer is None:
            # Check if this person has already been referred previously.
            referrers = UserReferral.objects.filter(user=self.user).exclude(referrer=None)
            if referrers.exists():
                # Previous referrer hasn't been catered for, cater for it now.
                self.referrer = referrers[0].referrer
        if self.referral_paid and self.referral_paid_date is None:
            self.referral_paid_date = datetime.datetime.now()
        super(UserReferral, self).save(*args, **kwargs)

    def __str__(self):
        if self.referrer is not None:
            return "%s %s %s" % (self.user.email, self.referrer.name, self.get_referral_action_display())
        else:
            return "%s %s" % (self.user.email, self.get_referral_action_display())

    class Meta:
        unique_together = ('user', 'referral_action')
        ordering = ('referral_date',)


class Profile(models.Model):
    """ Contains the info that we store alongside the End Users -
    not the CMS users.

    CMS User data will be in the AuthorProfile table.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL)

    dob = models.DateField(blank=True, null=True)

    telephone = models.CharField(max_length=250, blank=True, null=True)
    salutation = models.CharField(max_length=10)
    postcode = models.CharField(max_length=10, blank=True, null=True)
    newsletter = models.NullBooleanField(blank=True, null=True, default=False)
    ratealerts = models.NullBooleanField(blank=True, null=True, default=False)
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True, blank=True, null=True)
    is_synched = models.NullBooleanField(blank=True, null=True, default=False,
                                         help_text="Signifies if the user details have been synced with the SalesForce system")

    ip_address = models.CharField(max_length=100, blank=True, null=True)
    source = models.CharField(max_length=100, blank=True, null=True)

    savings_calculator_email = models.EmailField(null=True, blank=True)

    skeleton_user = models.NullBooleanField(blank=True, null=True, default=False,
                                            help_text="""Whether they have been created from the sync or not""")
    filled_in_name = models.BooleanField(default=True)

    ratetracker_threshold = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    ratetracker_threshold_set = models.BooleanField(default=False)

    def full_name(self):
        return u'%s %s %s' % (self.salutation, self.user.first_name, self.user.last_name)

    def user_email(self):
        return u'%s' % self.user.email

    @property
    def is_client(self):
        return CampaignsSignup.objects.filter(email=self.user.email, is_client=True).exists()

    def age(self):
        d = datetime.date.today()
        return (d.year - self.dob.year) - int((d.month, d.day) < (self.dob.month, self.dob.day))

    def save(self, *args, **kwargs):
        from common.tasks import create_user_profile, update_subscription_on_email_service

        super(Profile, self).save(*args, **kwargs)
        if not self.is_synched:
            create_user_profile.apply_async([self.pk], countdown=1)

        if self.ratealerts:
            update_subscription_on_email_service.delay(self.user.email, interest_group=u'Rate Alerts')
        else:
            update_subscription_on_email_service.delay(self.user.email, interest_group=u'Rate Alerts', subscribe=False)

    class Meta:
        get_latest_by = 'created_date'
        permissions = (
            (u'change_sccode', u'Can update SC codes for multiple accounts'),
            (u'add_product', u'Can add a product to a customers portfolio'),
            (u'change_user_portfolio', u'Can change a users portfolio'),
            (u'change_user_activation', u'Can change a users activation status'),
            (u'change_user_email', u'Can change a users email address'),
            (u'add_concierge_client', u'Can add a new concierge client'),
            (u'change_user_password', u'Can change a users password'),
            (u'change_user_subscriptions', u'Can change a users subscriptions'),
            (u'change_user_sync', u'Can change a users sync status'),
        )


def better_slugify(value):
    """
    Converts to lowercase, removes non-word characters (alphanumerics and
    underscores) and converts spaces to hyphens. Also strips leading and
    trailing whitespace.
    """
    value = re.sub(u'[^\w\s-]', u'', value).strip().lower()
    return mark_safe(re.sub(u'[-\s]+', u'-', value))


class UserNext(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    uuid = models.CharField(max_length=255, blank=True, null=True)


class UUIDNext(models.Model):
    uuid = models.CharField(unique=True, max_length=255)
    params = models.CharField(max_length=500, blank=True, null=True)
    next = models.CharField(max_length=50)


class AuthorProfile(models.Model):
    """ CMS User data is captured here - this is not for end Users """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='author_profile')
    slug = models.SlugField(blank=True)
    linked_in_url = models.URLField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)
    watercolor_image = models.ImageField(upload_to='biographies/', blank=True, null=True)
    small_image = models.ImageField(upload_to='biographies/', blank=True, null=True)
    biography = models.TextField(verbose_name='Biography Content', blank=True, null=True,
                                 help_text="""The description will be added to the Biography page""")

    def __unicode__(self):
        return '%s %s' % (self.user.first_name, self.user.last_name)

    def save(self, *args, **kwargs):
        name = '%s %s' % (self.user.first_name, self.user.last_name)
        self.slug = slugify(name)
        super(AuthorProfile, self).save(*args, **kwargs)


EMPTY_VALUES = ['', u'', None]


class Rates(models.Model):
    # Bank of England Base Rate
    boe_rate = models.DecimalField(max_digits=4, decimal_places=2)
    inflation_rate = models.DecimalField(max_digits=4, decimal_places=2)

    created_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Rates'

    def __unicode__(self):
        return 'Bank of England Base Rate %s, Inflation Rate %s' % (self.boe_rate, self.inflation_rate)


class Tweet(models.Model):
    class Meta:
        get_latest_by = 'last_updated'

    title = models.CharField(max_length=255)
    summary = models.CharField(max_length=255)
    created_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)


class CarouselTab(models.Model):
    title = models.CharField(max_length=500)
    description = models.CharField(max_length=500)
    order = models.IntegerField()
    media = models.ImageField(upload_to='carousel/', blank=True, null=True)
    cta_link_title = models.CharField(blank=True, null=True, max_length=100)
    cta_link = models.URLField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'%s' % self.title


class NewsletterSignup(models.Model):
    email = models.EmailField()
    created_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    is_synched = models.NullBooleanField(blank=True, null=True, default=False)
    activation_key = models.CharField(max_length=40, null=True)
    is_activated = models.BooleanField(default=True)
    source = models.CharField(max_length=100, blank=True, null=True)

    def save(self, *args, **kwargs):
        from common.tasks import update_subscription_on_email_service
        super(NewsletterSignup, self).save()
        if not self.is_activated and self.pk is not None:
            update_subscription_on_email_service.delay(self.email, subscribe=False)
        elif self.is_activated:
            update_subscription_on_email_service.delay(self.email)

    def delete(self, using=None):
        from common.tasks import update_subscription_on_email_service
        update_subscription_on_email_service.delay(self.email, subscribe=False)
        super(NewsletterSignup, self).delete(using=using)


class RateAlertsSignup(models.Model):
    email = models.EmailField()
    created_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    is_synched = models.NullBooleanField(blank=True, null=True, default=False)
    activation_key = models.CharField(max_length=40, null=True)
    is_activated = models.BooleanField(default=True)
    source = models.CharField(max_length=100, blank=True, null=True)

    def save(self, *args, **kwargs):
        existing = bool(self.pk)
        super(RateAlertsSignup, self).save()
        if not self.is_activated and existing:
            from common.tasks import update_subscription_on_email_service
            update_subscription_on_email_service.delay(self.email, interest_group=u'Rate Alerts', subscribe=False)
        elif self.is_activated:
            from common.tasks import update_subscription_on_email_service
            update_subscription_on_email_service.delay(self.email, interest_group=u'Rate Alerts')

    def delete(self, using=None):
        from common.tasks import update_subscription_on_email_service
        update_subscription_on_email_service.delay(self.email, interest_group=u'Rate Alerts', subscribe=False)
        super(RateAlertsSignup, self).delete(using=using)

class CampaignsSignup(models.Model):
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=100, blank=True, null=True)
    alt_telephone = models.CharField(max_length=100, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    newsletter = models.NullBooleanField(blank=True, null=True, default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    is_synched = models.NullBooleanField(blank=True, null=True, default=True)
    best_call_time = models.CharField(max_length=10, blank=True, null=True)
    is_client = models.NullBooleanField(blank=True, null=True, default=False)
    is_fake = models.BooleanField(default=False)
    source = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        ordering = ['created_date']


class ReminderSignup(models.Model):
    email = models.EmailField()
    created_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    is_synched = models.NullBooleanField(blank=True, null=True, default=False)
    healthcheck = models.NullBooleanField(blank=True, null=True, default=False)
    bestbuys = models.NullBooleanField(blank=True, null=True, default=False)


@receiver(post_save, sender=Profile)
def profile_save_handler(sender, instance, created, raw, using, **kwargs):
    if created:
        if instance.newsletter:
            email = instance.user.email
            if not NewsletterSignup.objects.filter(email=email).exists():
                news_signup = NewsletterSignup()
                news_signup.email = email
                news_signup.is_synched = False
                news_signup.save()
        if instance.ratealerts:
            email = instance.user.email
            if not RateAlertsSignup.objects.filter(email=email).exists():
                rate_signup = RateAlertsSignup()
                rate_signup.email = email
                rate_signup.is_synched = False
                rate_signup.save()

class HealthcheckSignup(models.Model):
    uuid = UUIDField(primary_key=True)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    telephone = models.CharField(max_length=20, unique=True,
                                 error_messages={'unique': "A healthcheck request with this telephone number already exists."})
    date_requested = models.DateTimeField(auto_now_add=True)

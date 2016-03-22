# coding=utf-8
from datetime import datetime
from django.db import models
from django.forms import SlugField
from django.utils.text import slugify
from django_extensions.db.fields import UUIDField
from common.models import BaseModel
from django.conf import settings
from django.core.urlresolvers import reverse
from common.utils import build_url

TODO_LENGTH = 200


class Page(BaseModel):
    lft = models.IntegerField()
    rgt = models.IntegerField()

    is_section = models.BooleanField(default=False, verbose_name="Add to the top navigation",
                                     help_text="""Selecting this checkbox will attempt to add this page to the top navigation""")

    is_footer = models.BooleanField(default=False, verbose_name="Add to the footer navigation",
                                    help_text="""These pages will appear along the footer and are generally for site T&Cs and site statements.""")

    meta_description = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        ordering = ('lft',)


    def __init__(self, *args, **kwargs):
        super(Page, self).__init__(*args, **kwargs)
        self.children = []
        self.parent = None
        self.is_root = False

    def get_child(self, slug):
        """ Gets child by slug """
        for child in self.children:
            if child.slug == slug:
                return child
        return None

    def push_child(self, child):
        self.children.append(child)

    def get_by_id(self, id):
        if self.id == id:
            return self
        for child in self.children:
            tmp = child.get_by_id(id)
            if tmp is not None:
                return tmp
        return None

    def add(self, pge):
        if self.lft < pge.lft and pge.rgt < self.rgt:

            for child in self.children:
                if child.add(pge) is None:
                    child.parent = self
                    return None

            pge.parent = self
            self.children.append(pge)
            return None

        return pge

    def get_absolute_url(self):
        values = []
        parent = self.parent
        while parent is not None:
            if not parent.is_root:
                values.insert(0, parent.slug)
            parent = parent.parent

        if not self.is_root:
            values.append(self.slug)

        return '/%s/' % ('/'.join(values))

    def values(self, arr=None):
        """ Returns hierarchy as a list of lists for django template tags """
        if arr is None:
            arr = []
        arr.append(self)
        for child in self.children:
            child.values(arr)

        return arr

    def get_section(self):
        retval = None
        if self.is_section:
            return self

        parent = self.parent
        while parent is not None:
            if parent.is_section:
                return parent
            parent = parent.parent

        return retval

    # def values_list(self, arr = None):
    #        """ Returns hierarchy as a flat list """
    #        if arr is None :
    #            arr = []
    #        arr.append(self)
    #        for child in self.children :
    #            arr = child.values(arr)
    #        return arr
    #

    def get_parents_of(self, pge, values):
        if pge.lft > self.lft and pge.rgt < self.rgt:
            values.append(self)
            for child in self.children:
                child.get_parents_of(pge, values)
        return values

    def rebuild(self, left):
        right = left + 1
        for child in self.children:
            right = child.rebuild(right)

        self.lft = left
        self.rgt = right
        return right + 1


class PageBody(models.Model):
    page = models.OneToOneField('pages.Page', related_name='body')
    text = models.TextField(blank=True, verbose_name='Page Content')

    class Meta:
        verbose_name = 'Page Content'

TEASER_LENGTH = getattr(settings, 'TEASER_LENGTH', 250)

EMPTY_VALUES = ['', u'', None]


class BaseArticle(models.Model):
    title = models.CharField(max_length=TODO_LENGTH, unique=True)
    slug = models.SlugField(max_length=TODO_LENGTH,
                            help_text="""The slug is a url encoded version of your title and is used to create the web address""",
                            unique=True)

    created_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)

    author = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True)
    publish_date = models.DateField(null=True)
    meta_description = models.CharField(max_length=200, blank=True, null=True)

    body = models.TextField(blank=True, verbose_name='Page Content')

    teaser = models.CharField(blank=True, max_length=1000, help_text="""A teaser is normally a truncated sample of the Article Content,
    if left blank, the CMS will create it from the first %s characters of the Page Content.""" % TEASER_LENGTH)

    show_ratetracker_form = models.BooleanField(default=False)
    show_newsletter_form = models.BooleanField(default=False)
    show_ratealert_form = models.BooleanField(default=False)
    show_joint_form = models.BooleanField(default=False)
    show_concierge_form = models.BooleanField(default=False)
    show_isa_tool = models.BooleanField(default=False)
    show_iht_advert = models.BooleanField(default=False)

    outbrain_content = models.BooleanField(default=False)

    class Meta:
        ordering = ('-publish_date',)
        abstract = True

    def __unicode__(self):
        return u'%s' % self.title

    def save(self, *args, **kwargs):
        if self.slug in EMPTY_VALUES:
            self.slug = slugify(self.title)
        if self.teaser in EMPTY_VALUES:
            # TODO do in a more clever way
            if len(self.body) >= TEASER_LENGTH:
                self.teaser = self.body[TEASER_LENGTH]
            else:
                self.teaser = self.body
        super(BaseArticle, self).save(*args, **kwargs)

    def get_absolute_url(self):
        if self.type == 'guide':
            return reverse('view_advice', args=[self.slug])
        elif self.type == 'article':
            return reverse('view_article', args=[self.slug])


class Article(BaseArticle):
    document = models.ManyToManyField('pages.Document', blank=True, null=True)
    image = models.ImageField(null=True, blank=True, upload_to='guide_cover_images')
    guide_section = models.CharField(max_length=50, null=True, blank=True)
    type = models.TextField()
    genre = models.CharField(max_length=500, default="OpEd")
    tags = models.CharField(max_length=500, default="savings account, interest rate, banking, finance, investment,")
    url_reverse = models.TextField(null=True, blank=True)


class PageBlock(models.Model):
    block_key = models.CharField(max_length=40)
    block_title = models.CharField(max_length=150)
    block_description = models.CharField(max_length=255, blank=True, null=True)
    text = models.TextField(blank=True, verbose_name='Content')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True)
    max_length = models.IntegerField()
    cta_link = models.URLField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now=True, blank=True, null=True)
    last_updated = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        verbose_name = 'Page Block'
        verbose_name_plural = 'Page Blocks'

    def __unicode__(self):
        return u'%s' % self.block_title


class FormMessage(models.Model):
    message_key = models.CharField(max_length=30)
    text = models.TextField(blank=True, verbose_name='Form Message')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True)

    class Meta:
        verbose_name = 'Form Message'
        verbose_name_plural = 'Form Messages'

    def __unicode__(self):
        return u'%s' % self.message_key


class Jargon(BaseModel):
    first_char = models.CharField(max_length=1, blank=True)

    description = models.TextField(blank=True, verbose_name='Page Content')

    class Meta:
        verbose_name = 'Jargon'
        verbose_name_plural = 'Jargon'
        ordering = ('title', )

    def save(self, *args, **kwargs):
        if self.title:
            self.first_char = self.title.lower()[0]
        super(Jargon, self).save(*args, **kwargs)


class Document(BaseModel):
    document = models.FileField(upload_to='documents/', blank=True, null=True)


class BlogItem(BaseArticle):
    GENERE_CHOICES = (
        ('Blog', 'Blog'),
        ('Ask the experts', 'Ask the experts')
    )

    genre = models.CharField(max_length=500, default="Blog", choices=GENERE_CHOICES)
    tags = models.CharField(max_length=500, default="savings account, interest rate, banking, finance, investment,")

    def get_absolute_url(self):
        return reverse('view_ask_the_experts', args=[self.slug])


class ParentPage(BaseModel):
    main_nav = models.BooleanField(blank=True, default=False)
    body = models.TextField(blank=True, help_text="""Used if no child pages are available""")
    meta = models.TextField(blank=True, help_text="""Overridden by child pages""")

    def get_absolute_url(self):
        return '/%s/' % self.slug


class ChildPage(BaseModel):
    parent = models.ForeignKey('ParentPage', blank=True)
    meta = models.TextField(blank=True)
    body = models.TextField(blank=True)
    footer_nav = models.BooleanField(default=False)
    order = models.IntegerField(blank=True, default=1)

    def get_absolute_url(self):
        if self.parent:
            return '/%s/%s/' % (self.parent.slug, self.slug)
        else:
            return '/%s/' % (self.slug)


class FAQ(BaseModel):
    pass


class FAQBlock(models.Model):
    faq = models.ForeignKey('FAQ')
    question = models.TextField(blank=True)
    answer = models.TextField(blank=True)
    order = models.IntegerField(default=1)


class StaticPage(BaseModel):
    pass


class StaticPageBlock(models.Model):
    staticpage = models.ForeignKey('StaticPage')
    block_id = models.CharField(max_length=1000, blank=True)
    block = models.TextField(blank=True)


class BaseComment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    comment_date = models.DateTimeField(auto_now_add=True, blank=True)
    comment = models.TextField(blank=True)
    approved = models.BooleanField(default=True)


class ArticleComment(BaseComment):
    article_comment = models.ForeignKey(Article)

    def build_approve_url(self):
        return build_url('approve_comment', get={'id': self.id, 'article': 'true'})


class BlogComment(BaseComment):
    blog_comment = models.ForeignKey(BlogItem)

    def build_approve_url(self):
        return build_url('approve_comment', get={'id': self.id})


class RateAlert(models.Model):
    title = models.CharField(max_length=TODO_LENGTH)
    slug = models.SlugField(max_length=TODO_LENGTH)
    bestbuy = models.ForeignKey('products.BestBuy')
    body = models.TextField(blank=True)
    publish_date = models.DateField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ('title',)

    def get_absolute_url(self):
        return reverse('view_ratealert', args=[self.slug])

    def __unicode__(self):
        return u'%s' % self.title

    def save(self, *args, **kwargs):
        try:
            super(RateAlert, self).save(*args, **kwargs)
        except:
            self.slug = slugify("%s %s %s" % (datetime.now().date(), self.bestbuy.get_title_display(), self.title))
            super(RateAlert, self).save(*args, **kwargs)


class AwardCategory(models.Model):
    uuid = UUIDField(primary_key=True)
    slug = SlugField()
    title = models.TextField()
    order = models.IntegerField(null=True, unique=True)

    def __str__(self):
        return "#%s - %s" % (str(self.order), self.title)

    class Meta:
        ordering = ['order']


class Award(models.Model):
    AWARD_RANKING = (
        (0, 'Winner'),
        (98, 'Highly Commended'),
        (99, 'Highly Commended'),
    )
    uuid = UUIDField(primary_key=True)
    provider = models.ForeignKey('products.Provider')
    product = models.ForeignKey('products.MasterProduct', null=True, blank=True)
    slug = SlugField()
    ranking = models.IntegerField(choices=AWARD_RANKING)
    category = models.ForeignKey(AwardCategory)
    awarded_date = models.DateField(default=datetime.today)

    def __str__(self):
        return " ".join([self.get_ranking_display(), self.category.title, self.provider.title])

    def image_url(self):
        return "img/awards/%s-%s-%s-image.png" % (self.get_ranking_display(),
                                                  self.category.title.replace(' ', '_'),
                                                  self.awarded_date)

    class Meta:
        ordering = ['ranking']

    def save(self, *args, **kwargs):
        super(Award, self).save(*args, **kwargs)

        from pages.tasks import create_award_image

        create_award_image.apply_async(kwargs={'award_id': self.pk, 'year': True, 'ranking': True, 'details': False},
                                       countdown=1)


class Petition(models.Model):
    uuid = UUIDField(primary_key=True)
    first_name = models.TextField()
    last_name = models.TextField()
    email = models.TextField(null=True)
    postcode = models.TextField()


class SevenPitfallsSignup(models.Model):
    uuid = UUIDField(primary_key=True)
    name = models.TextField()
    email = models.EmailField()
    phone = models.TextField()


class NISAGuideSignup(models.Model):
    uuid = UUIDField(primary_key=True)
    name = models.TextField()
    email = models.EmailField()


class IHTGuideSignup(models.Model):
    uuid = UUIDField(primary_key=True)
    name = models.TextField()
    email = models.EmailField()
    phone = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)


PUBLICATION_TYPES = (
    (1, 'Newspaper'),
    (2, 'Radio'),
    (3, 'TV/Video')
)

PRESS_PUBLICATION_RANK = (
    (1, 'National'),
    (2, 'Local'),
    (3, 'Other')
)


class PressAppearancePublication(models.Model):
    uuid = UUIDField(primary_key=True)
    name = models.TextField(verbose_name='Publication')
    ranking = models.IntegerField(choices=PRESS_PUBLICATION_RANK, default=3)

    def __str__(self):
        return self.name

    def count_posts(self):
        return self.pressappearance_set.count()

    class Meta:
        ordering = ['ranking', 'name']


class PressAppearance(models.Model):
    uuid = UUIDField(primary_key=True)
    publication_type = models.IntegerField(choices=PUBLICATION_TYPES, default=1)
    publication = models.ForeignKey(PressAppearancePublication)
    title = models.TextField()
    author = models.TextField()
    link = models.URLField(blank=True, null=True)
    date_featured = models.DateTimeField()

    def __str__(self):
        return " ".join([self.get_publication_type_display(), self.publication.name, self.title])

    class Meta:
        unique_together = ('publication_type', 'publication', 'title', 'author', 'link', 'date_featured')
        ordering = ['-date_featured']


class SavingsPriorityListSignup(models.Model):
    uuid = UUIDField(primary_key=True)
    name = models.TextField(default='')
    email = models.EmailField()


class SavingsPriorityListOptionSignup(models.Model):
    uuid = UUIDField(primary_key=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    easy_access = models.BooleanField(default=True)
    notice = models.BooleanField(default=True)
    one_year = models.BooleanField(default=True)
    two_to_three_year = models.BooleanField(default=True)
    four_to_five_year = models.BooleanField(default=True)
    over_five_years = models.BooleanField(default=True)


class FiftyPoundChallengeSignup(models.Model):
    uuid = UUIDField(primary_key=True)
    name = models.TextField()
    email = models.EmailField()
    phone = models.TextField()


class FiftyPoundChallengeAccount(models.Model):
    ACCOUNT_TYPES = (
        ('easy_access', 'Easy Access Account'),
        ('notice', 'Notice Account'),
        ('current', 'High Interest Current Account'),
        ('1y_fixed_rate', '1Yr Fixed Rate Bond'),
        ('2y_fixed_rate', '2Yr Fixed Rate Bond'),
        ('3y_fixed_rate', '3Yr Fixed Rate Bond'),
        ('4y_fixed_rate', '4Yr Fixed Rate Bond'),
        ('5y_fixed_rate', '5Yr Fixed Rate Bond'),
        ('6y_fixed_rate', '6Yr Fixed Rate Bond'),
        ('7y_fixed_rate', '7Yr Fixed Rate Bond'),
        ('other_fixed_rate', 'Other Fixed Rate Bond'),
        ('variable_rate', 'Variable Rate Bond'),
        ('regular_saver', 'Regular Savings Account'),
        ('fixed_rate_isa', 'Fixed Rate ISA'),
        ('variable_rate_isa', 'Variable Rate ISA')
    )

    challenge_signup = models.ForeignKey(FiftyPoundChallengeSignup)
    amount = models.TextField()
    rate = models.TextField()
    account_type = models.TextField(choices=ACCOUNT_TYPES)


class ProductQuestionaireSignup(models.Model):
    FUND_CHOICES = (
        ('0-50k', '£0 - £50,000'),
        ('50k-100k', '£50,000 - £100,000'),
        ('100k-250k', '£100,000 - £250,000'),
        ('250k-1M', '£250,000 - £1,000,000'),
        ('1M-plus', '£1,000,000 plus'),
    )

    uuid = UUIDField(primary_key=True)
    first_name = models.TextField()
    last_name = models.TextField()
    email = models.EmailField()
    phone = models.TextField()
    easy_access = models.BooleanField(default=False)
    notice_1_3 = models.BooleanField(default=False)
    notice_3_6 = models.BooleanField(default=False)
    fixed_rate_1 = models.BooleanField(default=False)
    fixed_rate_2 = models.BooleanField(default=False)
    funds = models.TextField(choices=FUND_CHOICES, default='0-50k')


class TheBiggestMistakeSignup(models.Model):
    uuid = UUIDField(primary_key=True)
    name = models.TextField()
    email = models.EmailField()
    phone = models.TextField()


class ProductFAQ(models.Model):
    uuid = UUIDField(primary_key=True)
    name = models.TextField()
    slug = models.SlugField()
    provider_url = models.URLField(default='')
    logobar = models.TextField(default='logobar.html')

    def __unicode__(self):
        return self.name


class ProductFAQuestion(models.Model):
    uuid = UUIDField(primary_key=True)
    faq = models.ForeignKey(ProductFAQ)
    question = models.TextField()
    answer = models.TextField()

    def __unicode__(self):
        return u"{0} - {1}".format(self.faq, self.question)


class FactFindSignup(models.Model):
    uuid = UUIDField(primary_key=True)
    name = models.TextField()
    email = models.EmailField()
    phone = models.TextField()


class FactFindAccount(models.Model):
    ACCOUNT_TYPES = (
        ('easy_access', 'Easy Access Account'),
        ('notice', 'Notice Account'),
        ('current', 'High Interest Current Account'),
        ('1y_fixed_rate', '1Yr Fixed Rate Bond'),
        ('2y_fixed_rate', '2Yr Fixed Rate Bond'),
        ('3y_fixed_rate', '3Yr Fixed Rate Bond'),
        ('4y_fixed_rate', '4Yr Fixed Rate Bond'),
        ('5y_fixed_rate', '5Yr Fixed Rate Bond'),
        ('6y_fixed_rate', '6Yr Fixed Rate Bond'),
        ('7y_fixed_rate', '7Yr Fixed Rate Bond'),
        ('other_fixed_rate', 'Other Fixed Rate Bond'),
        ('variable_rate', 'Variable Rate Bond'),
        ('regular_saver', 'Regular Savings Account'),
        ('fixed_rate_isa', 'Fixed Rate ISA'),
        ('variable_rate_isa', 'Variable Rate ISA')
    )

    challenge_signup = models.ForeignKey(FactFindSignup)
    account_type = models.TextField(choices=ACCOUNT_TYPES)
    provider = models.ForeignKey('products.Provider', null=True)
    amount = models.TextField()
    rate = models.TextField()


class PensionOptionSignup(models.Model):
    uuid = UUIDField(primary_key=True)
    first_name = models.TextField()
    last_name = models.TextField()
    email = models.EmailField()
    phone = models.TextField()
    postcode = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)


class MindfulMoneyHealthcheckSignup(models.Model):
    uuid = UUIDField(primary_key=True)
    first_name = models.TextField()
    last_name = models.TextField()
    email = models.EmailField()
    phone = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)


class MoneyToTheMassesSignup(models.Model):
    uuid = UUIDField(primary_key=True)
    name = models.TextField()
    email = models.EmailField()
    phone = models.TextField()


class ChallengerBankGuideSignup(models.Model):
    uuid = UUIDField(primary_key=True)
    name = models.TextField()
    email = models.EmailField()

class IHTSqueezePageSignup(models.Model):
    uuid = UUIDField(primary_key=True)
    name = models.TextField()
    email = models.EmailField()
    phone = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)

class PSASqueezePageSignup(models.Model):
    uuid = UUIDField(primary_key=True)
    email = models.EmailField()
    date_created = models.DateTimeField(auto_now_add=True)


class HighWorthSqueezePageSignup(models.Model):
    uuid = UUIDField(primary_key=True)
    name = models.TextField(default='')
    email = models.EmailField()
    phone = models.TextField(default='')
    date_created = models.DateTimeField(auto_now_add=True)

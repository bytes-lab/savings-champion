from products.models import Product, Provider, BestBuy, ProductPortfolio, RatetrackerReminder, ProviderBestBuy, \
    MasterProduct, AdvantagesBlock, Ranking, \
    FSCSLimitType, ProductTier, InterestPaidFrequency
from django.contrib import admin
from products.forms import BestBuyModelForm
from products.csv_exports import export_portfolio, export_reminder
from common.actions import mark_synched, mark_unsynched
from products.actions import ExportMasterProducts


class ProductInline(admin.TabularInline):
    model = Product
    fields = ('sc_code', 'publish_after', 'title', 'provider', 'gross_rate', 'minimum', 'maximum', 'bonus_term',
              'underlying_gross_rate')
    readonly_fields = (
    'sc_code', 'publish_after', 'title', 'provider', 'gross_rate', 'minimum', 'maximum', 'bonus_term',
    'underlying_gross_rate')
    ordering = ('-sc_code',)
    extra = 0


class ProductTierInline(admin.TabularInline):
    model = ProductTier
    fields = ('sc_code', 'publish_after', 'title', 'provider', 'gross_rate', 'minimum', 'maximum', 'bonus_term',
              'underlying_gross_rate')
    readonly_fields = (
        'sc_code', 'publish_after', 'title', 'provider', 'gross_rate', 'minimum', 'maximum', 'bonus_term',
        'underlying_gross_rate')
    ordering = ('-sc_code',)
    extra = 0


class RankingInline(admin.TabularInline):
    model = BestBuy.products.through
    #account_name = BestBuy.products.through.product.account_type
    fields = ('product', 'rank')
    readonly_fields = ('product', 'rank')
    ordering = ('rank',)
    extra = 0
    inlines = [ProductInline, ]


class AdvantagesInline(admin.TabularInline):
    model = AdvantagesBlock
    extra = 0


class BestBuyAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title',)
    list_display = ('title', 'client_type', 'author', 'last_updated', 'created_date', 'order')
    form = BestBuyModelForm
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'order', 'author', 'has_table', 'ratetracker_enabled', 'is_fixed', 'is_bond',
                       'description', 'landing_page_description', 'tips', 'client_type')
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('meta_description', 'comparison_meta_description')
        }),)

    inlines = [RankingInline, AdvantagesInline, ]

    def save_model(self, request, obj, form, change):
        if obj.author is None:
            obj.author = request.user
        obj.save()


class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}

    list_display = (
    'sc_code', 'title', 'provider', 'aer', 'gross_rate', 'minimum', 'maximum', 'publish_after', 'created_date',
    'last_updated')
    search_fields = ('title', 'provider__title', 'sc_code')
    list_filter = ('bestbuy_type',)


class ProductTierAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}

    list_display = (
        'sc_code', 'title', 'provider', 'aer', 'gross_rate', 'minimum', 'maximum', 'publish_after', 'created_date',
        'last_updated')
    search_fields = ('title', 'provider__title', 'sc_code')
    list_filter = ('is_internet_access', 'is_post_access', 'is_branch_access')


class ProviderBestBuyAdmin(admin.ModelAdmin):
    list_display = ('provider',)
    list_per_page = 20


class ProductPortfolioAdmin(admin.ModelAdmin):
    search_fields = ('user__email', 'master_product__title', 'provider__title', 'user__username')

    list_display = ('user_email', 'master_product', 'opening_date', 'created_date', 'last_updated', 'is_synched')
    list_per_page = 20
    fields = (
    'user', 'user_email', 'master_product', 'provider', 'account_type', 'balance', 'is_deleted', 'is_synched', 'opening_date', 'bonus_term',
    'notice')
    readonly_fields = ('user', 'user_email', 'master_product', 'provider', 'account_type')
    actions = [export_portfolio("CSV Export", ), mark_synched, mark_unsynched]
    list_filter = ('created_date',)
    ordering = ['-last_updated']

    def SC_Code(self, obj):
        return obj.master_product.get_latest_old_product_tier(balance=obj.balance).sc_code

    def user_email(self, obj):
        return obj.user.email

    def user_username(self, obj):
        return obj.user.username


class RatetrackerReminderAdmin(admin.ModelAdmin):
    search_fields = ('user__email', 'provider__title', 'user__username')
    list_display = (
    'user_email', 'provider', 'account_type', 'maturity_date', 'created_date', 'last_updated', 'is_synched')
    list_per_page = 20
    list_filter = ('created_date',)
    actions = [export_reminder("CSV Export", ), mark_synched, mark_unsynched]
    ordering = ['-last_updated']

    def user_email(self, obj):
        return obj.user.email


class MasterProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'sf_product_id', 'provider__title')
    list_filter = ('provider__title', 'bestbuy_type', 'account_type', 'status')
    fieldsets = (
        (None, {
            'fields': (('title', 'slug'), 'sf_product_id', 'provider', ('account_type', 'status'), 'bestbuy_type',
                       ('available_from', 'available_to'),
                       ('is_internet_access', 'is_phone_access', 'is_post_access', 'is_branch_access', 'is_cc_access'),
                       ('is_open_internet', 'is_open_telephone', 'is_open_post'),
                       ('existing_only', 'locals_only'),
                       ('is_open_branch', 'is_open_cc', 'is_fixed'),
                       ('facts', 'fscs_licence'),
                       ('verdict',),
                       ('term', 'term_fixed_date', 'notice'),
                       ('operating_balance', 'operating_balance_rate'),
                       ('open_limit_total', 'open_limit_own_name', 'open_limit_joint_name'),
                       ('other_reason_to_exclude_this_product', 'other_reason_compliance_checked'),
                       ('exclude_from_api_for', 'url'),
                       'bonus_term',
            )
        }),
    )

    list_display = ('title', 'sf_product_id', 'provider', 'Tier_Amount')
    inlines = [ProductInline, ProductTierInline]
    actions = [ExportMasterProducts]

    def Tier_Amount(self, obj):
        return obj.master_product.all().count()


class ProviderAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    list_display = ('title', 'fscs_parent')


from django.contrib.admin import SimpleListFilter

class NullListFilter(SimpleListFilter):
    def lookups(self, request, model_admin):
        return (
            ('1', 'Null', ),
            ('0', '!= Null', ),
        )

    def queryset(self, request, queryset):
        if self.value() in ('0', '1'):
            kwargs = { '{0}__isnull'.format(self.parameter_name) : self.value() == '1' }
            return queryset.filter(**kwargs)
        return queryset

class ReplacedNullListFilter(NullListFilter):
    title = u'Date Replaced'
    parameter_name = u'date_replaced'

class RankingAdmin(admin.ModelAdmin):
    model = Ranking
    raw_id_fields = ('product',)
    list_filter = (ReplacedNullListFilter, 'rank', 'bestbuy')


class FSCSLimitTypeAdmin(admin.ModelAdmin):
    pass


class InterestPaidFrequencyAdmin(admin.ModelAdmin):
    pass



admin.site.register([ProviderBestBuy, ], ProviderBestBuyAdmin)
admin.site.register(Provider, ProviderAdmin)
admin.site.register([BestBuy, ], BestBuyAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductTier, ProductTierAdmin)
admin.site.register(MasterProduct, MasterProductAdmin)
admin.site.register(ProductPortfolio, ProductPortfolioAdmin)
admin.site.register(RatetrackerReminder, RatetrackerReminderAdmin)
admin.site.register(Ranking, RankingAdmin)
admin.site.register(FSCSLimitType, FSCSLimitTypeAdmin)
admin.site.register(InterestPaidFrequency, InterestPaidFrequencyAdmin)

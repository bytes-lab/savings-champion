from pages.models import Page, PageBody, Article, PageBlock, Jargon, FormMessage, Document, BlogItem, ParentPage, \
    ChildPage, AwardCategory, Award, \
    PressAppearance, PressAppearancePublication, ProductFAQuestion, ProductFAQ
from pages.models import FAQ, FAQBlock, StaticPage, StaticPageBlock, ArticleComment, BlogComment, RateAlert
from django.contrib import admin
from django.conf import settings
from common.admin import BaseModelAdmin
from pages.forms import PageForm, PageBodyForm, ArticleForm, PageBlockForm, BlogItemForm
from pages import utils
from pages.adminforms import ParentPageAdForm, ChildPageAdForm, FAQAdForm, StaticPageBlockAdForm, RateAlertAdForm


class PageBodyInline(admin.TabularInline):
    model = PageBody
    form = PageBodyForm


class ChildPageInline(admin.StackedInline):
    model = ChildPage
    form = ChildPageAdForm
    extra = 0
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("order",)


class ArticleCommentInline(admin.TabularInline):
    model = ArticleComment
    extra = 0


class BlogCommentInline(admin.TabularInline):
    model = BlogComment
    extra = 0


class FAQBlockInline(admin.TabularInline):
    model = FAQBlock
    form = FAQAdForm
    extra = 0


class StaticPageBlockInline(admin.TabularInline):
    model = StaticPageBlock
    form = StaticPageBlockAdForm
    extra = 0


class DocumentAdmin(BaseModelAdmin):
    model = Document


class PageAdmin(BaseModelAdmin):
    form = PageForm

    list_display = ('title', 'last_updated', 'created_date',)
    exclude = ('lft', 'rgt')
    inlines = [
        PageBodyInline,
    ]

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'parent_page', 'is_section', 'is_footer',)
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('meta_description',)
        }),)

    def save_model(self, request, obj, form, change):

        hierarchy = utils.load_hierarchy()

        if hierarchy is None:
            # only needed for the first run
            obj.lft = 1
            obj.rgt = 2
            obj.save()
        else:
            # if object id we need to check if parent has changed
            if obj.id:
                # 

                current_page = hierarchy.get_by_id(obj.id)

                parent_page = form.cleaned_data.get('parent_page', hierarchy)
                if current_page.parent.id != parent_page.id:
                    # moving it
                    current_page.parent.children.remove(current_page)

                    # what about the childre
                    obj.children = current_page.children

                    parent = hierarchy.get_by_id(parent_page.id)

                    parent.push_child(obj)
                    hierarchy.rebuild(1)
                    values = hierarchy.values()
                    for value in values:
                        value.save()
                else:
                    obj.save()

            else:
                # if not specified we make the parent to be the root
                parent_page = form.cleaned_data.get('parent_page', hierarchy)

                # find parent in hierarchy
                parent = hierarchy.get_by_id(parent_page.id)

                # forcing this to get the right left and right
                parent.push_child(obj)
                hierarchy.rebuild(1)
                values = hierarchy.values()
                #import pdb
                #pdb.set_trace()
                for value in values:
                    value.save()

    def delete_model(self, request, obj):
        hierarchy = utils.load_hierarchy()

        current_page = hierarchy.get_by_id(obj.id)
        if current_page and current_page.parent.id:
            current_page.parent.children.remove(current_page)
        hierarchy.rebuild(1)
        values = hierarchy.values()
        for value in values:
            value.save()

        obj.delete()


admin.site.register(Page, PageAdmin)

admin.site.register(Document, DocumentAdmin)
admin.site.register(FormMessage, admin.ModelAdmin)


class PageBlockAdmin(admin.ModelAdmin):
    form = PageBlockForm
    list_display = ('block_key', 'block_title', 'created_date', 'last_updated')


admin.site.register(PageBlock, PageBlockAdmin)


class JargonAdmin(BaseModelAdmin):
    exclude = ('first_char',)
    list_display = ('title', 'created_date', 'last_updated')


admin.site.register(Jargon, JargonAdmin)
TEASER_LENGTH = getattr(settings, 'TEASER_LENGTH', 200)
EMPTY_VALUES = ['', u'', None]


class ArticleAdmin(BaseModelAdmin):
    list_display = ('title', 'author', 'type', 'last_updated', 'created_date')
    form = ArticleForm
    #exclude = ('author',)
    raw_id_fields = ("document",)
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'author', 'publish_date', 'type', 'genre', 'tags', 'show_ratetracker_form',
                       'show_newsletter_form', 'show_ratealert_form', 'show_joint_form', 'show_concierge_form',
                       'show_iht_advert', 'guide_section', 'outbrain_content')
        }),
        ('Content', {
            'fields': ('body', 'teaser', 'document', 'image', 'url_reverse')
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('meta_description',)
        }),)

    list_filter = ('outbrain_content',)

    inlines = [ArticleCommentInline, ]

    def save_model(self, request, obj, form, change):
        #if obj.id is None:
        #    obj.author = request.user


        if obj.teaser in EMPTY_VALUES:
            obj.teaser = obj.body[:TEASER_LENGTH]

        obj.save()


admin.site.register([Article, ], ArticleAdmin)


class BlogItemAdmin(BaseModelAdmin):
    list_display = ('title', 'author', 'last_updated', 'created_date')
    form = BlogItemForm
    #exclude = ('author',)
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'author', 'publish_date', 'genre', 'tags', 'show_ratetracker_form',
                       'show_newsletter_form', 'show_ratealert_form', 'show_joint_form', 'show_concierge_form')
        }),
        ('Content', {
            'fields': ('body', 'teaser',)
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('meta_description',)
        }),)

    inlines = [BlogCommentInline, ]

    def save_model(self, request, obj, form, change):
        #if obj.id is None:
        #    obj.author = request.user


        if obj.teaser in EMPTY_VALUES:
            obj.teaser = obj.body[:TEASER_LENGTH]

        obj.save()


admin.site.register([BlogItem, ], BlogItemAdmin)


class ParentPageAdmin(BaseModelAdmin):
    inlines = [ChildPageInline, ]
    form = ParentPageAdForm


class ChildPageAdmin(BaseModelAdmin):
    list_display = ('title', 'parent', 'order')
    form = ChildPageAdForm

    def parent(self, obj):
        return obj.parent_page.title


class FAQAdmin(BaseModelAdmin):
    inlines = [FAQBlockInline, ]


class StaticPageAdmin(BaseModelAdmin):
    inlines = [StaticPageBlockInline, ]


class RateAlertAdmin(BaseModelAdmin):
    fields = ['title', 'slug', 'publish_date', 'bestbuy', 'body']
    list_display = ('title', 'bestbuy', 'publish_date')
    ordering = ['-publish_date']
    form = RateAlertAdForm


class AwardCategoryAdmin(admin.ModelAdmin):
    model = AwardCategory


class AwardAdmin(admin.ModelAdmin):
    model = Award


class PressAppearanceAdmin(admin.ModelAdmin):
    model = PressAppearance


class PressAppearancePublicationAdmin(admin.ModelAdmin):
    model = PressAppearancePublication

class ProductFAQAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    model = ProductFAQ


class ProductFAQuestionAdmin(admin.ModelAdmin):
    model = ProductFAQuestion


admin.site.register(ParentPage, ParentPageAdmin)
admin.site.register(ChildPage, ChildPageAdmin)
admin.site.register(FAQ, FAQAdmin)
admin.site.register(StaticPage, StaticPageAdmin)
admin.site.register(RateAlert, RateAlertAdmin)
admin.site.register(AwardCategory, AwardCategoryAdmin)
admin.site.register(Award, AwardAdmin)
admin.site.register(PressAppearance, PressAppearanceAdmin)
admin.site.register(PressAppearancePublication, PressAppearancePublicationAdmin)

admin.site.register(ProductFAQ, ProductFAQAdmin)
admin.site.register(ProductFAQuestion, ProductFAQuestionAdmin)






















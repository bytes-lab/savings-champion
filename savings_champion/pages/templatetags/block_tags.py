from django import template
from pages.models import StaticPage, StaticPageBlock
from django.views.decorators.cache import cache_page

register = template.Library()


class GetStaticBlockNode(template.Node):
    """
    Check if value exists in the context, if it doesn't load it in
    """

    def __init__(self, main_slug, block_id, context_var):
        self.main_slug = main_slug
        self.block_id = block_id
        self.context_var = context_var
        
    def render(self, context):        
        try:
            staticpage = StaticPage.objects.get(slug=self.main_slug)
            try:
                block = staticpage.staticpageblock_set.get(block_id=self.block_id)
            except StaticPageBlock.MultipleObjectsReturned:
                block = staticpage.staticpageblock_set.filter(block_id=self.block_id).first()
            context[self.context_var] = block.block
        except StaticPage.DoesNotExist:
            context[self.context_var] = ''
            pass
        except StaticPageBlock.DoesNotExist:
            context[self.context_var] = ''
            pass
        
        return ''


@cache_page(60 * 60 * 6)
@register.tag('get_static_block')
def get_static_block(parser, token):
    func_name, main_slug, block_id, _, context_var = token.split_contents()
    return GetStaticBlockNode(main_slug, block_id, context_var)


class GetStaticBlockNodeByVariable(template.Node):
    def __init__(self, main_slug, block_id, context_var):
        self.main_slug = main_slug
        self.block_id = template.Variable(block_id)
        self.context_var = context_var

    def render(self, context):
        try:
            block_id = self.block_id.resolve(context)
            try:
                block = StaticPageBlock.objects.get(staticpage__slug=self.main_slug, block_id=str(block_id))
            except StaticPageBlock.MultipleObjectsReturned:
                block = StaticPageBlock.objects.filter(staticpage__slug=self.main_slug, block_id=str(block_id)).first()
            context[self.context_var] = block.block
        except StaticPage.DoesNotExist:
            context[self.context_var] = ''
            pass
        except StaticPageBlock.DoesNotExist:
            context[self.context_var] = ''
            pass

        return ''


@cache_page(60 * 60 * 6)
@register.tag('get_static_block_by_variable')
def get_static_block_by_variable(parser, token):
    func_name, main_slug, block_id, _, context_var = token.split_contents()
    return GetStaticBlockNodeByVariable(main_slug, block_id, context_var)

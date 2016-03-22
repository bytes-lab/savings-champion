from django import template
from HTMLParser import HTMLParser
from django.conf import settings
from pages.models import Page, PageBlock, FormMessage
from pages import utils

register = template.Library()

SITETREE = 'sitetree'

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


class SitetreeNode(template.Node):
    """
    Check if value exists in the context, if it doesn't load it in
    """

    def __init__(self, context_var, queryset=None):
        self.context_var = context_var
        
    def render(self, context):
        
        sitetree = context.get(self.context_var, None)
        if not sitetree :
            context[self.context_var] = utils.load_hierarchy()
        else :
            print 'already found in the context'
        return ''
  
@register.tag
def get_sitetree(parser, token):
    func_name, _, context_var = token.split_contents()
    return SitetreeNode(context_var)

class FooterLinksNode(template.Node):
    """
    Check if value exists in the context, if it doesn't load it in
    """

    def __init__(self, sitetree, context_var, queryset=None):
        self.context_var = context_var
        self.sitetree = template.Variable(sitetree)
        
    def render(self, context):

        sitetree = self.sitetree.resolve(context)
        retval = []
        if sitetree and sitetree.children:
            for child in sitetree.children :
                if child.is_footer :
                    retval.append(child)
                    
        context[self.context_var] = retval
        return ''
  
class GetSectionNode(template.Node):
    """
    Check if value exists in the context, if it doesn't load it in
    """

    def __init__(self, page, context_var = 'section'):
        self.context_var = context_var
        self.page = template.Variable(page)
        
    def render(self, context):
        page = self.page.resolve(context)
        if page :
            context[self.context_var] = page.get_section()
        return ''
    
@register.tag
def get_section(parser, token):
    func_name, page, _, context_var = token.split_contents()
    return GetSectionNode(page, context_var)
  
class GetBlockNode(template.Node):
    """
    Check if value exists in the context, if it doesn't load it in
    """

    def __init__(self, key, context_var):
        self.context_var = context_var
        self.key = key
        
    def render(self, context):        
        try :
            block = PageBlock.objects.get(block_key = self.key)
            if '.meta' in self.key :
                "meta descriptions need to be stripped"
                stripped = strip_tags(block.text)
                block.text = stripped.strip()

            context[self.context_var] = block
        except PageBlock.DoesNotExist:
            pass
        
        return ''

class GetEvalBlockNode(template.Node):
    """
    Check if value exists in the context, if it doesn't load it in
    """

    def __init__(self, key, context_var):
        self.context_var = context_var
        self.key = template.Variable(key)
        
    def render(self, context):        
        try :
            block = PageBlock.objects.get(block_key = self.key.resolve(context))
            context[self.context_var] = block
        except PageBlock.DoesNotExist:
            pass
        
        return ''
    
class GetFormMessageNode(template.Node):
    """
    Check if value exists in the context, if it doesn't load it in
    """

    def __init__(self, key, context_var):
        self.context_var = context_var
        self.key = template.Variable(key)
    def render(self, context):
        try :
            block = FormMessage.objects.get(message_key = self.key.resolve(context))
            context[self.context_var] = block
        except FormMessage.DoesNotExist:
            pass
        
        return ''    

@register.tag
def get_footer_links(parser, token):
    func_name, sitetree, _, context_var = token.split_contents()
    return FooterLinksNode(sitetree, context_var)

@register.tag
def get_form_message(parser, token):
    func_name, title, _, context_var = token.split_contents()
    return GetFormMessageNode(title, context_var)

@register.tag
def get_block(parser, token):
    func_name, title, _, context_var = token.split_contents()
    return GetBlockNode(title, context_var)
@register.tag
def get_special_block(parser, token):
    func_name, title, _, context_var = token.split_contents()
    return GetEvalBlockNode(title, context_var)


    

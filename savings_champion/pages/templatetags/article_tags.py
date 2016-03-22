from django import template
from django.conf import settings
from pages.models import Article, BlogItem
from common.templatetags import QuerySetNode
import datetime

register = template.Library()


@register.tag(name="get_latest_articles")
def get_latest_articles(parser, token):
    """ 
    """
    func_name,limit,  _, context_var = token.split_contents()
    return QuerySetNode(context_var, queryset=Article.objects.filter(type='article', publish_date__lte=datetime.datetime.now())[:limit])

@register.tag(name="get_latest_articles_by_distinct_authors")
def get_latest_articles_by_distinct_authors(parser, token):
    """ 
    """
    func_name, user,  _, context_var = token.split_contents()
    return ArticleQuerySetNode(context_var, user)

SUE = 'SueHannums'
ANNA = 'AnnaBowes'

class ArticleQuerySetNode(template.Node):
    """ Template node to return a queryset in a specified 
        variable in the context
    """

    def __init__(self, context_var, user):
        self.context_var = context_var
        self.user = template.Variable(user)

    def render(self, context):
        """
        Needs to get the latest by Sue and Anna
        """
        user = self.user.resolve(context)
        filters = {}
        if user and user.is_authenticated() and user.is_staff :
            pass
        else :
            filters['publish_date__lte'] = datetime.datetime.now()
        results = []
        
        one = Article.objects.filter(author__username=ANNA, **filters)[:1]
        two = Article.objects.filter(author__username=SUE, **filters)[:1]
        if len(one) > 0:
            results.append(one[0])
        if len(two) > 0:
            results.append(two[0])
        
        context[self.context_var] = results
        return ''
    
class LatestBlogItemNode(template.Node):
    """ Template node to return a queryset in a specified 
        variable in the context
    """

    def __init__(self, context_var, user):
        self.context_var = context_var
        self.user = template.Variable(user)

    def render(self, context):
        """
        Needs to get the latest by Sue and Anna
        """
        user = self.user.resolve(context)
        filters = {}
        if user and user.is_authenticated() and user.is_staff :
            pass
        else :
            filters['publish_date__lte'] = datetime.datetime.now()
        result = None        

        one = BlogItem.objects.filter(**filters)[:1]
        if len(one) > 0:
            result = one[0]
            
        context[self.context_var] = result
        return ''

@register.tag(name="get_latest_blog_item")
def get_latest_blog_item(parser, token):
    """ 
    """
    func_name, user,  _, context_var = token.split_contents()
    return LatestBlogItemNode(context_var, user)

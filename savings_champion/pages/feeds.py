from django.contrib.syndication.views import Feed
from pages.models import Article, BlogItem, RateAlert
import datetime
from itertools import chain
from operator import attrgetter

class LatestAllFeed(Feed):
    title = "Savings Champion News and Guides"
    link = 'https://www.savingschampion.co.uk'
    description = "All news from Savings Champion."

    def items(self):
        articles = Article.objects.filter(publish_date__lte=datetime.datetime.now())
        blogs = BlogItem.objects.filter(publish_date__lte=datetime.datetime.now())
        
        posts = sorted(chain(articles, blogs), 
                       key=attrgetter('publish_date'), reverse=True)
        return posts[:10]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.teaser
    
class LatestArticlesFeed(Feed):
    title = "Savings Champion News and Guides"
    link = 'https://www.savingschampion.co.uk'
    description = "Latest Savings News from Savings Champion."

    def items(self):
        return Article.objects.filter(publish_date__lte = datetime.datetime.now()).order_by('-publish_date')[:10]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.teaser
    
class LatestBlogFeed(Feed):
    title = "Savings Champion News and Guides"
    link = 'https://www.savingschampion.co.uk'
    description = "Latest Blog Entries from Savings Champion."

    def items(self):
        return BlogItem.objects.filter(publish_date__lte=datetime.datetime.now()).order_by('-publish_date')[:10]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.teaser
    
class LatestRateAlertsFeed(Feed):
    title = "Savings Champion News and Guides"
    link = 'https://www.savingschampion.co.uk'
    description = "Latest Rate Alerts from Savings Champion."

    def items(self):
        return RateAlert.objects.filter(publish_date__lte = datetime.datetime.now()).order_by('-publish_date')[:10]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.body
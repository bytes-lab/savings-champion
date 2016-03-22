from django.contrib.sitemaps import Sitemap
from pages.models import Page, Article, BlogItem
import datetime
from django.contrib.sites.models import get_current_site
from django.core import urlresolvers
from django.core.paginator import EmptyPage, PageNotAnInteger
from django.http import Http404
from django.template.response import TemplateResponse
from datetime import datetime, timedelta

    
def NewsSitemapView(request, sitemaps, section=None,
            template_name='sitemap.xml', mimetype='application/xml'):
    req_site = get_current_site(request)

    if section is not None:
        if section not in sitemaps:
            raise Http404("No sitemap available for section: %r" % section)
        maps = [sitemaps[section]]
    else:
        maps = sitemaps.values()
    page = request.GET.get("p", 1)

    urls = []
    for site in maps:
        try:
            if callable(site):
                site = site()
            urls.extend(site.get_news_urls(page=page, site=req_site))
        except EmptyPage:
            raise Http404("Page %s empty" % page)
        except PageNotAnInteger:
            raise Http404("No page '%s'" % page)
    return TemplateResponse(request, template_name, {'urlset': urls},
                            content_type=mimetype)
    
    
    
class AbstractSitemapClass():
    changefreq = 'daily'
    url = None
    def get_absolute_url(self):
        return self.url
    
class StaticSitemap(Sitemap):
    pages = {
             'index':'/', #Add more static pages here like this 'example':'url_of_example',
             'Best Buys':'/best-buys/',

             'Rate Tracker' : '/rate-tracker/',
             'Rate Tracker Portfolio' : '/rate-tracker/portfolio/',
             'Concierge Service' : '/concierge-service/',
             
             'Advice and Guides' : '/advice-guides/',
             'Savings News' : '/news/',
             'In the Press' : '/news/in-the-press/',
             'Our Blog' : '/news/our-blog/',
             'Terms and conditions' : '/information/terms-conditions/',
             'Privacy Policy' : '/information/privacy-policy/',
             'Cookie Policy' : '/information/cookie-policy/',
             'Website Security' : '/information/website-security/',
             
             'Why Savings Champion' : '/about-us/why-savings-champion/',
             'How do we make our money' : '/about-us/how-do-we-make-our-money/',
             'Our methodology' : '/about-us/our-methodology/',
             'Our founding team' : '/about-us/our-founding-team/',
             'Testimonials' : '/about-us/testimonials/',
             'Contact Us' : '/about-us/contact-us/',
             }
    main_sitemaps = []
    for page in pages.keys():
        sitemap_class = AbstractSitemapClass()
        sitemap_class.url = pages[page]        
        main_sitemaps.append(sitemap_class)

    def items(self):
        return self.main_sitemaps    
    priority = 0.5
    changefreq = "weekly"  

class BestBuyTablesSitemap(Sitemap):
    pages = {
             'Easy Access' : '/best-buys/personal/easy-access/',
             'Fixed Rate Bond' : '/best-buys/personal/fixed-rate-bond/',
             'Variable Rate ISA' : '/best-buys/personal/variable-rate-isa/',
             'Fixed Rate ISA' : '/best-buys/personal/fixed-rate-isa/',
             'Notice Accounts' : '/best-buys/personal/notice-accounts/',
             'Monthly Income' : '/best-buys/personal/monthly-income/',
             'Regular Savings' : '/best-buys/personal/regular-savings/',
             'Children Accounts' : '/best-buys/personal/childrens-accounts/',            
             }
    main_sitemaps = []
    for page in pages.keys():
        sitemap_class = AbstractSitemapClass()
        sitemap_class.url = pages[page]        
        main_sitemaps.append(sitemap_class)
        
    priority = 1
    changefreq = 'daily'
    
    def items(self):
        return self.main_sitemaps   
    
class PageSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.5
    
    def items(self):
        return Page.objects.all()
    
    
class ArticleSitemap(Sitemap):
    changefreq = 'daily'
    priority = 1
    
    def items(self):
        return Article.objects.all()
    
        
class BlogSitemap(Sitemap):
    changefreq = 'daily'
    priority = 1
    
    def items(self):
        return BlogItem.objects.all()

class NewsSitemap(Sitemap):
# This limit is defined by Google. See the index documentation at
# http://www.google.com/support/webmasters/bin/answer.py?hl=en&answer=74288
    limit = 1000
    def get_url_info(self, item, current_site):
        url_info = super(NewsSitemap, self).get_url_info(item, current_site)
        url_info.update({
            'publication_date': self._get('publication_date', item, None),
            'keywords': self._get('keywords', item, None),
        })
        return url_info

    
class SiteNewsmap(NewsSitemap):
    changefreq = 'daily'
    priority = 1
        
    def publication_date(self, obj):
        return obj.publish_date
    
    def keywords(self, obj):
        return obj.tags
    
    def title(self, obj):
        return obj.title
    
    def genre(self, obj):
        return obj.genre
        
    def __get(self, name, obj, default=None):
        try:
            attr = getattr(self, name)
        except AttributeError:
            return default
        if callable(attr):
            return attr(obj)
        return attr
    
    def get_news_urls(self, page=1, site=None, protocol=None):

        protocol = 'http'

        # Determine domain
        if site is None:
            if Site._meta.installed:
                try:
                    site = Site.objects.get_current()
                except Site.DoesNotExist:
                    pass
            if site is None:
                raise ImproperlyConfigured("To use sitemaps, either enable the sites framework or pass a Site/RequestSite object in your view.")
        domain = site.domain
        urls = []
        for item in self.paginator.page(page).object_list:
            loc = "%s://%s%s" % (protocol, domain, self.__get('location', item))
            priority = self.__get('priority', item, None)
            url_info = {
                'item':       item,
                'location':   loc,
                'lastmod':    self.__get('lastmod', item, None),
                'changefreq': self.__get('changefreq', item, None),
                'priority':   str(priority is not None and priority or ''),
                'publication_date': self.__get('publication_date', item, None),
                'keywords': self.__get('keywords', item, None),
                'title': self.__get('title', item, None),
                'genre': self.__get('genre', item, None),
            }
            urls.append(url_info)

        return urls
    
class ArticleNews(SiteNewsmap):
    def items(self):
        articles = Article.objects.filter(publish_date__lte=datetime.now())[:100]
        return articles
    
    
class BlogNews(SiteNewsmap):
    def items(self):
        blogs = BlogItem.objects.filter(publish_date__lte=datetime.now())[:100]
        return blogs
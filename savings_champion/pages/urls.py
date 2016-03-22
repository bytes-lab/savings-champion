from django.conf.urls import *
from django.views.generic import TemplateView
from pages.feeds import LatestAllFeed, LatestArticlesFeed, LatestBlogFeed, LatestRateAlertsFeed

urlpatterns = patterns('',
                       url(r'^allfeed/$', LatestAllFeed(), name='rss_feed_all'),
                       url(r'^articlefeed/$', LatestArticlesFeed(), name='rss_feed_articles'),
                       url(r'^blogfeed/$', LatestBlogFeed(), name='rss_feed_blogs'),
                       url(r'^ratealertfeed/$', LatestRateAlertsFeed(), name='rss_feed_ratealerts'),
                       url(r'^$', 'pages.views.news_index', name='news_index'),
                       url(r'^in-the-press/$', 'pages.views.press_appearances', name="in_the_press"),
                       url(r'^in-the-press/ajax/$', 'pages.views.press_appearances_ajax', name="in_the_press_ajax"),
                       # url(r'^in-the-press/$', 'pages.views.page_controller', {'parent': 'press', 'left_nav': 'news/leftnav.html'}, name="in_the_press"),
                       url(r'^rate-alerts/latest/$', 'pages.views.view_ratealert_overview',
                           name='view_ratealert_overview'),
                       url(r'^rate-alerts/archive/$', 'pages.views.ratealert_index', name='ratealert_index'),
                       url(r'^savings-news/$', 'pages.views.article_index', name='article_index'),
                       url(r'^ask-the-experts/$', 'pages.views.blog_index', name='blog_index'),
                       url(r'^add_article_comment/$', 'pages.views.add_article_comment', name='add_article_comment'),
                       url(r'^add_blog_comment/$', 'pages.views.add_blog_comment', name='add_blog_comment'),
                       url(r'^savings-news/(?P<post_slug>[\w\-]+)/$', 'pages.views.view_article', name='view_article'),
                       url(r'^our-blog/(?P<post_slug>[\w\-]+)/$', 'pages.views.view_blog', name='view_blog'),
                       url(r'^ask-anna/(?P<post_slug>[\w\-]+)/$', 'pages.views.view_ask_the_experts', name='view_ask_the_experts'),

                       url(r'^rate-alerts/archive/(?P<rateslug>[\w\-]+)/$', 'pages.views.view_ratealert',
                           name='view_ratealert'),
                       url(r'^comment-success/$', 'pages.views.comment_success', name='comment_success'),

                       url(r'^concierge/trust/$', 'pages.views.trust_concierge', name='trust_concierge'),

                       url(r'^static/redirect/15-16-tax-tables-updated/$', 'pages.views.static_redirect', {'file_location': 'docs/Savings_Champion_2015_16_Tax_Tables.pdf'}, name='2015-16_updated_tax_tables_redirect'),
                       url(r'^static/redirect/15-16-tax-tables/$', 'pages.views.static_redirect', {'file_location': 'docs/Savings_Champion_Tax_Tables_2015.pdf'}, name='2015-16_tax_tables_redirect'),
                       url(r'^static/redirect/challenger-bank-guide/$', 'pages.views.static_redirect', {'file_location': 'docs/Guide_to_Challenger_Banks.pdf'}, name='challenger_bank_guide_redirect'),
                       url(r'^static/redirect/securing-your-wealth-guide/$', 'pages.views.static_redirect', {'file_location': 'docs/Securing_your_wealth_guide.pdf'}, name='iht_squeeze_page_redirect'),
                       url(r'^static/redirect/help-to-buy-isa-factsheet/$', 'pages.views.static_redirect', {'file_location': 'docs/help_to_buy_ISA_factsheet.pdf'}, name='help_to_buy_isa_factsheet_redirect'),

                       url(r'^thb_tool/$', TemplateView.as_view(template_name='thb_tool/thb_tool.html')),

                       url(r'^iht-guide-signup/$', 'pages.views.iht_squeeze_page', name='iht_squeeze_page'),
                       url(r'^iht-guide-signup/thank-you/$', 'pages.views.iht_squeeze_page_thankyou', name='iht_squeeze_page_thankyou'),

                       url(r'^psa-factsheet-signup/$', 'pages.views.psa_squeeze_page', name='psa_squeeze_page'),
                       url(r'^psa-factsheet-signup/thank-you/$', 'pages.views.psa_squeeze_page_thankyou', name='psa_squeeze_page_thankyou'),

                       url(r'^high-earners-guide-signup/$', 'pages.views.high_worth_squeeze_page', name='high_worth_squeeze_page'),
                       url(r'^high-earners-guide-signup/thank-you/$', 'pages.views.high_worth_squeeze_page_thankyou', name='high_worth_squeeze_page_thankyou'),
)

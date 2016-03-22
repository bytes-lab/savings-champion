from django.conf.urls import *
from django.views.generic import TemplateView
from sitemaps import ArticleSitemap, BlogSitemap, StaticSitemap, BestBuyTablesSitemap, BlogNews, ArticleNews, \
    PageSitemap
from django.contrib import admin
from django.views.generic import RedirectView
from filebrowser.sites import site

sitemaps = {
    'static': StaticSitemap,
    'pages': PageSitemap,
    'articles': ArticleSitemap,
    'blog': BlogSitemap,
    'bestbuytables': BestBuyTablesSitemap,
}

news_sitemaps = {
    'blognews': BlogNews,
    'articlenews': ArticleNews,
}
urlpatterns = patterns('',

                       # Uncomment the next line to enable the admin:
                       url(r'^admin/filebrowser/', include(site.urls)),
                       (r'^admin/', include(admin.site.urls)),
                       (r'^grappelli/', include('grappelli.urls')),
                       (r'^ckeditor/', include('ckeditor.urls')),
                       (r'^tinymce/', include('tinymce.urls')),
                       (r'^best-buys/', include('products.urls')),
                       (r'^news/', include('pages.urls')),
                       (r'^administration/', include('administration.urls')),
                       (r'^ifa/', include('ifa.urls')),
                       (r'^concierge/', include('concierge.urls')),
                       (r'^api/v1/', include('api.v1.urls')),
                       url(r'^select2/', include('django_select2.urls')),
                       url(r'^ratetracker/', include('rate_tracker.urls')),

                       # redirects from the old site to map to the new site
                       url(r'^jargon-buster/$', 'redirect.jargon_buster_redirect', name="jargon_buster_old"),
                       # more specific match goes first
                       url(r'^advice-guides/fscs-licence-information/$', 'redirect.old_fscs_guide_link'),
                       url(r'^savings-news/in-the-press/$', 'redirect.savings_news_in_the_press_redirect'),
                       url(r'^savings-news/blogs/$', 'redirect.savings_news_blog_index_redirect',
                           name='list_blogs_old'),
                       url(r'^savings-news/blogs/(?P<blog_slug>[\w\-]+)/$', 'redirect.savings_news_blog_view_redirect',
                           name='view_blog_item_old'),
                       url(r'^savings-news/(?P<article_slug>[\w\-]+)/$', 'redirect.savings_news_article_view_redirect',
                           name='view_article_old'),
                       url(r'^savings-news/$', 'redirect.savings_news_article_index_redirect',
                           name='list_articles_old'),

                       url(r'^isa-tracker/', 'redirect.isa_tracker_redirect', name="isa_tracker_old"),

                       url(r'^rate-tracker/1-minute-rate-check/ocomplete/$', 'redirect.old_rate_tracker_redirect',
                           name="opening_date_rate_check_complete_old"),
                       url(r'^rate-tracker/1-minute-rate-check/complete/$', 'redirect.old_rate_tracker_redirect',
                           name="rate_check_complete_old"),
                       url(r'^rate-tracker/help/$', 'redirect.old_rate_tracker_redirect', name="rate_check_help_old"),
                       url(r'^rate-tracker/1-minute-rate-check/$', 'redirect.old_rate_tracker_redirect',
                           name="rate_check_old"),
                       url(r'^rate-tracker/portfolioupdate/$', 'redirect.old_rate_tracker_redirect'),

                       url(r'^newsletters/', 'redirect.old_newsletter_redirect', name='newsletter_signup_old'),

                       url(r'^rate-concierge/', 'redirect.old_concierge_redirect',
                           name='concierge_signup_complete_old'),
                       # end old redirects

                       url(r'^advice-guides/guides/(?P<post_slug>[\w\-]+)/$', 'pages.views.view_article',
                           {'template_file': 'advice/post.html'}, name='view_advice'),
                       url(r'^advice-guides/advice/(?P<child>[\w\-\/]+)$', 'pages.views.child_page_controller',
                           {'parent': 'advice', 'template_file': 'advice/page.html'}, name="advice_page"),
                       url(r'^advice-guides/$', 'pages.views.advice_index', name='advice_guides'),

                       url(r'^rate-tracker/$', 'products.views.savings_healthcheck', name="healthcheck"),
                       url(r'^rate-tracker/faq/$', 'products.views.savings_healthcheck_faq', name="healthcheck_faq"),
                       url(r'^rate-tracker/portfolio/$', 'products.views.savings_healthcheck_portfolio',
                           name="healthcheck-portfolio"),
                       url(r'^rate-tracker/portfolio/print/$', 'products.views.print_portfolio',
                           name="print-healthcheck-portfolio"),
                       url(r'^rate-tracker/portfolio/add/$', 'products.views.savings_healthcheck_portfolio_add_product',
                           name="portfolio_add"),
                       url(r'^rate-tracker/portfolio/addfixed/$',
                           'products.views.savings_healthcheck_portfolio_add_fixed_product', name="portfolio_addfixed"),

                       url(r'^/thisismoney/rate-tracker/1-minute-rate-check/complete/$',
                           'thisismoney.tracker.views.rate_check_complete', name="mainsite_timrate_check_complete"),
                       url(r'^/thisismoney/rate-tracker/1-minute-rate-check/$', 'thisismoney.tracker.views.tracker',
                           name="mainsite_timrate_check"),
                       url(r'^/thisismoney/rate-tracker/$', 'thisismoney.tracker.views.portfolio',
                           name="mainsite_timrate_tracker"),
                       url(r'^/thisismoney/$', 'thisismoney.tracker.views.tracker', name="index_timrate_check"),

                       url(r'^accounts/logout/$', 'common.views.sc_logout', name="sc_logout"),
                       (r'^accounts/', include('common.accounts.urls')),

                       url(r'^redirect/(?P<redirect_key>[\w\-]+)/$', 'common.views.redirect', name="redirector"),

                       url(r'^$', 'common.views.home', name="home"),
                       # (r'^robots.txt$',  direct_to_template, {'template': 'robots.txt', 'mimetype': 'text/plain'}),
                       (r'^robots.txt$', TemplateView.as_view(template_name="robots.txt")),
                       url(r'^savings-healthcheck/$', 'common.signups.savings_health_check',
                           name="savings_health_check"),
                       url(r'^savings-healthcheck/thank-you/$', 'common.signups.savings_health_check_thankyou',
                           name="savings_health_check_thankyou"),

                       # Old Concierge Service Links Block - Maintained for compatibility with old links
                       url(r'^MSS/$', 'concierge.views.landing.index', name='concierge_signup_mss'),
                       url(r'^managed-savings-service/$', 'concierge.views.landing.index',
                           name='concierge_signup_managed_savings_service'),
                       url(r'^concierge-service/$', 'concierge.views.landing.index', name='concierge_signup'),
                       url(r'^concierge-service-video/$', 'concierge.views.landing.index', name='video_signup'),
                       url(r'^concierge-service-video/reader-offer/$', 'concierge.views.landing.index',
                           name='video_signup_campaign'),
                       url(r'^concierge-service/trust/$', 'concierge.views.landing.index',
                           name='concierge_trust_signup'),
                       url(r'^concierge-service/charity/$', 'concierge.views.landing.index',
                           name='concierge_charity_signup'),
                       url(r'^concierge-service/business/$', 'concierge.views.landing.index',
                           name='concierge_business_signup'),
                       url(r'^intermediary/$', 'concierge.views.landing.index', name='intermediary_signup'),
                       url(r'^concierge-service/thankyou/$', 'pages.views.concierge_thankyou',
                           name='concierge_thankyou'),
                       url(r'^concierge-service/faq/$', 'concierge.views.landing.index', name='concierge_faq'),
                       url(r'^concierge-service/more-information/$', 'concierge.views.landing.index',
                           name='concierge_more'),

                       url(r'^signup/newsletter/$', 'common.signups.newsletter', name='signup_newsletter'),
                       url(r'^signup/newsletter/activate/(?P<key>\w+)/$', 'common.signups.activate_newsletter',
                           name='activate_newsletter'),
                       url(r'^signup/thankyou/$', 'common.signups.finish_activation', name='thankyou_newsletter'),
                       url(r'^signup/ratealert/$', 'common.signups.ratealert', name='signup_ratealert'),
                       url(r'^signup/ratealert/activate/(?P<key>\w+)/$', 'common.signups.activate_ratealert',
                           name='activate_ratealert'),
                       url(r'^signup/all/$', 'common.signups.joint_signup', name='signup_all'),
                       url(r'^signup/all/activate/(?P<key>\w+)/$', 'common.signups.activate_ratealert',
                           name='activate_all'),

                       url(r'^ajax/submitcontactform/$', 'common.contact_us.contact_form_submit',
                           name='submit_contact_form'),

                       url(r'^sitemap\.xml$', TemplateView.as_view(template_name="core/sitemapindex.xml")),
                       url(r'^sitemap1\.xml$', 'django.contrib.sitemaps.views.sitemap',
                           {'sitemaps': sitemaps, 'template_name': 'core/sitemap.xml'}),
                       url(r'^news_sitemap.xml$', 'sitemaps.NewsSitemapView',
                           {'sitemaps': news_sitemaps, 'template_name': 'core/news_sitemap.xml'}),

                       url(r'^coming-soon/$', 'pages.views.page_controller', {'parent': 'coming-soon'},
                           name="coming_soon"),
                       url(r'^help/$', 'pages.views.page_controller', {'parent': 'help'}, name="help_index"),

                       url(r'^switch-my-savings-petition-campaign/$', 'pages.views.petition', name='petition'),
                       url(r'^sms/$', 'pages.views.petition', name='petition'),
                       url(
                           r'^switch-my-savings-petition-campaign/thank_you/$',
                           'pages.views.petition_thank_you', name='petition_thank_you'),

                       url(r'^ajax/required/$', 'common.views.ajax_required', name='ajax_required'),

                       url(r'^awards/$', 'pages.views.awards', name='awards'),
                       url(r'^awards/(?P<year>\d+)/$', 'pages.views.awards', name='awards'),

                       url(r'^favicon\.ico$', RedirectView.as_view(url='/static/favicon.ico')),
                       url(r"^select2/", include("django_select2.urls")),

                       url(r'^7-pitfalls-for-larger-savers/$', 'pages.views.seven_pitfalls_for_savers_signup',
                           name='seven_pitfalls_for_savers'),
                       url(r'^7-pitfalls-for-larger-savers/thank-you/$',
                           'pages.views.seven_pitfalls_for_savers_thankyou',
                           name='seven_pitfalls_for_savers_thankyou'),

                       url(r'^nisa-guide/$', 'pages.views.nisa_savings_guide_signup', name='nisa_savings_guide_signup'),
                       url(r'^nisa-guide$', 'pages.views.nisa_savings_guide_signup', name='nisa_savings_guide_signup'),
                       url(r'^nisa/$', 'pages.views.nisa_savings_guide_signup', name='nisa_savings_guide_signup'),
                       url(r'^nisa$', 'pages.views.nisa_savings_guide_signup', name='nisa_savings_guide_signup'),

                       url(r'^nisa-guide/thankyou/$', 'pages.views.nisa_savings_guide_thankyou',
                           name='nisa_savings_guide_thankyou'),

                       url(r'^iht-guide/$', 'pages.views.iht_guide_signup', name='iht_guide_signup'),
                       url(r'^iht-guide/thank-you/$', 'pages.views.iht_guide_thankyou',
                           name='iht_guide_thankyou'),

                       url(r'^fb-iht-guide/$', 'pages.views.fb_iht_guide_signup',
                           name='fb_iht_guide_signup'),
                       url(r'^fb-iht-guide/thank-you/$', 'pages.views.fb_iht_guide_thankyou',
                           name='fb_iht_guide_thankyou'),

                       url(r'^ob-iht-guide/$', 'pages.views.outbrain_iht_guide_signup',
                           name='outbrain_iht_guide_signup'),
                       url(r'^ob1-iht-guide/$', 'pages.views.outbrain_iht_guide_signup', kwargs={'context': {'image_static': 'img/ob_iht_guide/guide2.jpg'}},
                           name='outbrain_iht_guide_signup'),
                       url(r'^ob-iht-guide/thank-you/$', 'pages.views.outbrain_iht_guide_thankyou',
                           name='outbrain_iht_guide_thankyou'),



                       url(r'^budget-summary/thank-you/$', 'pages.views.budget_summary_thankyou',
                           name='budget_summary_thankyou'),

                       url(r'^pension-options/$', 'pages.views.pension_options_signup',
                           name='pension_options_signup'),
                       url(r'^pension-options/thank-you/$', 'pages.views.pension_options_thankyou',
                           name='pension_options_thankyou'),

                       url(r'^savings-priority-list/$', 'pages.views.savings_priority_list_signup',
                           name='savings_priority_list_signup'),
                       url(r'^savings-priority-list/thank-you/$', 'pages.views.savings_priority_list_thankyou',
                           name='savings_priority_list_thankyou'),

                       url(r'^savings-priority-list/option/$', 'pages.views.savings_priority_list_options',
                           name='savings_priority_list_options'),

                       url(r'^50-pound-challenge/$', 'pages.views.fact_find_signup', name='fifty_pound_challenge'),
                       url(r'^50-pound-challenge/thank-you/$', 'pages.views.fact_find_signup',
                           name='fifty_pound_challenge_thankyou'),

                       url(r'^mindful-money-healthcheck/$', 'pages.views.mindful_money_healthcheck_signup',
                           name='mindful_money_healthcheck_signup'),
                       url(r'^mindful-money-healthcheck/thank-you/$', 'pages.views.mindful_money_healthcheck_thankyou',
                           name='mindful_money_healthcheck_thankyou'),

                       url(r'^we-negotiate-savings-interest-rates/$', 'pages.views.product_questionaire_signup',
                           name='product_questionaire'),
                       url(r'^we-negotiate-savings-interest-rates/thank-you/$',
                           'pages.views.product_questionaire_thankyou',
                           name='product_questionaire_thankyou'),

                       url(r'^the-biggest-mistake/$', 'pages.views.the_biggest_mistake_signup',
                           name='the_biggest_mistake'),
                       url(r'^the-biggest-mistake/thank-you/$', 'pages.views.the_biggest_mistake_thankyou',
                           name='the_biggest_mistake_thankyou'),

                       url(r'^7-ways-to-manage-cash-savings/$', 'pages.views.the_biggest_mistake_signup',
                           name='the_biggest_mistake'),
                       url(r'^7-ways-to-manage-cash-savings/thank-you/$', 'pages.views.the_biggest_mistake_thankyou',
                           name='the_biggest_mistake_thankyou'),

                       url(r'^money-to-the-masses/$', 'pages.views.money_to_the_masses_signup',
                           name='money_to_the_masses_signup'),
                       url(r'^money-to-the-masses/thank-you/$', 'pages.views.money_to_the_masses_thankyou',
                           name='money_to_the_masses_thankyou'),

                       url(r'^challenger-banks-guide/$', 'pages.views.challenger_banks_guide_signup',
                           name='challenger_banks_guide_signup'),
                       url(r'^challenger-banks-guide/thank-you/$', 'pages.views.challenger_banks_guide_thankyou',
                           name='challenger_banks_guide_thankyou'),

                       url(r'^products/faq/(?P<product_slug>.+)/', 'pages.views.product_faq',
                           name='savings_champion_verdict'),

                       url(r'^fact-find/$', 'pages.views.fact_find_signup', name='fact_find'),
                       url(r'^fact_find/thank-you/$', 'pages.views.fact_find_thankyou',
                           name='fact_find_thankyou'),

                       url(r'^pensionerbonds/$', 'pages.views.pensioner_bonds', name='pensioner_bonds'),
                       url(r'^pensionerbonds$', 'pages.views.pensioner_bonds', name='pensioner_bonds'),

                       url(r'^report_builder/', include('report_builder.urls')),

                       url(r'^just_error/$', 'common.views.just_error'),

                       url(r'^thb/$', TemplateView.as_view(template_name='thb_tool/thb_tool.html')),
                       url(r'^THB/$', TemplateView.as_view(template_name='thb_tool/thb_tool.html')),

                       ### ======   Nothing beyond this point ====== ###


                       url(r'^(?P<parent>[\w\-]+)/(?P<child>[\w\-]+)/$', 'pages.views.child_page_controller',
                           name='child_controller'),
                       url(r'^(?P<parent>[\w\-]+)/$', 'pages.views.page_controller', name='parent_controller'),
                       )

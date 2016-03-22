from django.shortcuts import redirect

def jargon_buster_redirect(request):
    return redirect('child_controller', parent='help', child='jargon-buster', permanent=True)

def savings_news_article_index_redirect(request):
    return redirect('article_index', permanent=True)

def savings_news_blog_index_redirect(request):
    return redirect('blog_index', permanent=True)

def savings_news_article_view_redirect(request, article_slug=""):
    return redirect('view_article', post_slug=article_slug, permanent=True)

def savings_news_blog_view_redirect(request, blog_slug=""):
    return redirect('view_blog', post_slug=blog_slug, permanent=True)

def savings_news_in_the_press_redirect(request):
    return redirect('in_the_press', permanent=True)

def isa_tracker_redirect(request):
    return redirect('healthcheck', permanent=True)

def old_rate_tracker_redirect(request):
    return redirect('healthcheck', permanent=True)

def old_newsletter_redirect(request):
    return redirect('news_index', permanent=True)

def old_concierge_redirect(request):
    return redirect('concierge_signup', permanent=True)

def old_bestbuy_table_redirect(request, bestbuy_slug=''):
    return redirect('personal_table', bestbuy_slug=bestbuy_slug, permanent=True)
    
def old_bestbuy_table_index_redirect(request, bestbuy_slug=''):
    return redirect('top_accounts', permanent=True)

def old_fscs_guide_link(request, post_slug=""):
    return redirect('view_advice', post_slug="fscs-licence-information", permanent=True)
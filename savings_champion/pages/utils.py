from django.http import Http404
from pages.models import Page


def get_page_or_404(page_hierarchy, url_parts):
    """
    
    """
    if not page_hierarchy:
        raise Http404()
    
    page = None
    for part in url_parts :
        if part :
            page = page_hierarchy.get_child(part)
            if not page :
                raise Http404()
            page_hierarchy = page
    
    return page

def get_page(page_hierarchy, url_parts = []):
    """
    
    """
    if len(url_parts) == 0 :
        return page_hierarchy
    
    if not page_hierarchy:
        return None
    
    page = None
    for part in url_parts :
        if part :
            page = page_hierarchy.get_child(part)
            if not page :
                return None
            page_hierarchy = page
    
    return page


def load_hierarchy():
    
    root = None
    pages = Page.objects.filter(lft__gte = 0, rgt__gte = 0).order_by('lft')
    
    hierarchy = None
    for page in pages :
        if hierarchy is None:
            hierarchy = page
            hierarchy.is_root = True
        else :
            hierarchy.add(page)
    return hierarchy
            
            
def tokenize(value, delimiter = '/'):
    if value != '' :
        return value.split(delimiter)
    return []
    
        
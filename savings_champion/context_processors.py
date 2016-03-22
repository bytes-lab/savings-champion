from django.conf import settings
GA_ACCOUNT = getattr(settings, 'GA_ACCOUNT', None)
IS_LIVE = getattr(settings, 'IS_LIVE', False)
def site_context(request):
    return {'google_account' : GA_ACCOUNT, 'IS_LIVE' : IS_LIVE}
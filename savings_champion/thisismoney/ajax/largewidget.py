#contains the methods for retrieving HTML for the larger version of the TiM widget
from django.http import HttpResponse 
from django.template.loader import get_template
from django.template import RequestContext
from thisismoney.forms import TIMRateTrackerForm
from common.forms import NewsletterForm, RateAlertForm
from pages.forms import ConciergeSignupForm
from pages.models import PageBlock
from django.shortcuts import redirect, render


#SORT OUT CONTEXTS OR FAIL MISERABLY.
def rate_tracker(request, context=None):
    if context is None:
        context = {}
    if request.is_ajax():
        context['ratetracker_form'] = TIMRateTrackerForm()
        return render(request, 'thisismoney/ratetracker/ajax/basic_wizard.html', context)
    else:
        return redirect('ajax_required')

def concierge(request):
    if request.is_ajax():
        c = RequestContext(request)
        c['headermessage'] = PageBlock.objects.get(block_key='tim.concierge.header').text
        c['bodymessage'] = PageBlock.objects.get(block_key='tim.concierge.incentive').text
        data = {'source': 'This is Money'}
        c['conciergeform'] = ConciergeSignupForm(initial=data)
        html = get_template('thisismoney/ratetracker/ajax/concierge.html')
        html_content = html.render(c)
        return HttpResponse(html_content) 
    else:
        return redirect('ajax_required')

def rate_alerts(request):
    if request.is_ajax():
        c = RequestContext(request)
        data = {'source' : 'This is Money'}
        c['newsletterform'] = NewsletterForm(initial=data)
        c['ratealertsform'] = RateAlertForm(initial=data)
        c['message'] = PageBlock.objects.get(block_key='tim.ratealerts.incentive').text
        html = get_template('thisismoney/ratetracker/ajax/rate_alerts.html')
        html_content = html.render(c)
        return HttpResponse(html_content) 
    else:
        return redirect('ajax_required')
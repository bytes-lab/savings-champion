from common.decorators import render_to
from django.contrib.auth import logout
from django.http import HttpResponseRedirect 
from django.core.urlresolvers import reverse
from common.models import UUIDNext, UserNext
from common.accounts.forms import IndexSignupform
from django.shortcuts import render_to_response
from django.template import RequestContext

@render_to()
def home(request, template_file='core/index.html'):
    form = IndexSignupform()
    return {'TEMPLATE': template_file, 'form': form}

def sc_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('home'))

def redirect(request, redirect_key):
    try:
        uuid_next = UUIDNext.objects.get(uuid=redirect_key)
        return HttpResponseRedirect(uuid_next.next + '?' + uuid_next.params)
    except UserNext.DoesNotExist:
        pass
    return HttpResponseRedirect('/')

def ajax_required(request, template_name="common/ajax_required.html"):
    context = RequestContext(request)
    
    return render_to_response(template_name, context_instance=context)

def just_error(request):
    assert False, 'Just errored out for you, as asked...'


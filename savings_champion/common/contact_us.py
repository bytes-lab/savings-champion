from django.http import HttpResponse
from django.template.loader import get_template
from django.template import RequestContext
from django.core.mail import send_mail
from django.shortcuts import redirect


def contact_form_submit(request):
    if request.is_ajax():
        send_mail('New Message from the contact form',
                  "Name: %s \n Email: %s \n Message: %s" % (
                      request.POST['name'], request.POST['email'], request.POST['message']),
                  'savings.champion@savingschampion.co.uk',
                  ['info@savingschampion.co.uk'], fail_silently=False)

        c = RequestContext(request)
        html = get_template('contact_us/contact_success.html')
        html_content = html.render(c)
        return HttpResponse(html_content)
    else:
        return redirect('ajax_required')
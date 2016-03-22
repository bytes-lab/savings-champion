from products.forms import EmailInstructionsForm
from common.models import ReminderSignup
from django.http import HttpResponse 
from django.core.mail import send_mail
from django.shortcuts import redirect

def email_instructions(request):
    if request.method == "POST" and request.is_ajax():
        form = EmailInstructionsForm(request.POST)
        
        if form.is_valid():
            email = form.cleaned_data.get('email', None)
            try:
                signup = ReminderSignup.objects.get(email=email)
            except ReminderSignup.DoesNotExist:
                signup = ReminderSignup()
                signup.email = email
                signup.bestbuys = True
                signup.is_synched = False
                signup.save()
            
        return HttpResponse('true')
    else:
        return redirect('ajax_required')
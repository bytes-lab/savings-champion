from django.contrib.auth import get_user_model
from django.shortcuts import redirect, render
from django.shortcuts import render_to_response
from django.template import RequestContext
from common.models import NewsletterSignup, RateAlertsSignup, Profile
from common.forms import RateAlertsUpsellForm
from django.contrib.sites.models import RequestSite
import uuid
from django.core.mail import send_mail
from common.accounts.forms import SignUpForm
from common.forms import SavingsHealthCheckForm
from concierge.models import AdviserQueue

User = get_user_model()

def send_newsletter_activation(request, signup):
    site = RequestSite(request)
    send_mail('Please activate your subscription',
                       'Please click the following link to activate %s%s%s%s%s' % ('https://', site.domain, '/signup/newsletter/activate/', signup.activation_key, '/'),
                       'savings.champion@savingschampion.co.uk',
                      [signup.email], fail_silently=False)

def send_joint_activation(request, signup):
    site = RequestSite(request)
    send_mail('Please activate your subscription',
                       'Please click the following link to activate %s%s%s%s%s' % ('https://', site.domain, '/signup/all/activate/', signup.activation_key, '/'),
                       'savings.champion@savingschampion.co.uk',
                      [signup.email], fail_silently=False)
    
def send_ratealert_activation(request, signup):
    site = RequestSite(request)
    send_mail('Please activate your subscription',
                       'Please click the following link to activate %s%s%s%s%s' % ('https://', site.domain, '/signup/ratealert/activate/', signup.activation_key, '/'),
                       'savings.champion@savingschampion.co.uk',
                      [signup.email], fail_silently=False)

def create_ratealert(email, activated):
    rasignup = RateAlertsSignup()
    rasignup.email = email
    rasignup.is_activated = activated
    rasignup.is_synched = False
    rasignup.activation_key = str(uuid.uuid4()).replace('-','')
    while RateAlertsSignup.objects.filter(activation_key=rasignup.activation_key).exists():
        rasignup.activation_key = str(uuid.uuid4()).replace('-','')
    rasignup.save()
    
    return rasignup

def create_newsletter(email, activated):
    newsletter = NewsletterSignup()
    newsletter.email = email
    newsletter.is_synched = False
    newsletter.activation_key = str(uuid.uuid4()).replace('-','')
    while NewsletterSignup.objects.filter(activation_key=newsletter.activation_key).exists():
        newsletter.activation_key = str(uuid.uuid4()).replace('-','')
    newsletter.is_activated = activated
    newsletter.save()
    

def newsletter(request, template_file = 'common/signups/checkemail.html'):
    context = RequestContext(request)
    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email', None)
            if NewsletterSignup.objects.filter(email__iexact=email).exists():
                signup = NewsletterSignup.objects.filter(email__iexact=email)[0]
                #someone has tried resigning up - now we need to check if they have activated anywhere else on the site
                if signup.is_activated is False:
                    if User.objects.filter(email__iexact=email).exists():
                        user = User.objects.filter(email__iexact=email)[0]
                        if user.is_active:
                            signup.is_activated = True
                            signup.save()
                            try:
                                profile = user.profile
                            except Profile.DoesNotExist:
                                profile = Profile(user=user)
                                profile.save()
                            except Profile.MultipleObjectsReturned:
                                profiles = Profile.objects.filter(user=user)
                                profile = profiles[0]
                            profile.newsletter = True
                            profile.is_synched = False
                            profile.save()
                            return redirect('thankyou_newsletter')
                        else:
                            send_newsletter_activation(request, signup)  
                            return redirect('signup_newsletter')
                    elif RateAlertsSignup.objects.filter(email=email).exists():
                        rasignup = RateAlertsSignup.objects.get(email=email)
                        if rasignup.is_activated:
                            signup.is_activated = True
                            signup.save()  
                            return redirect('thankyou_newsletter')
                        else:
                            send_newsletter_activation(request, signup)  
                            return redirect('signup_newsletter')
                    else:
                        send_newsletter_activation(request, signup)  
                        return redirect('signup_newsletter')
                else:
                    return redirect('thankyou_newsletter')            
            else:
                newsletter = NewsletterSignup()
                newsletter.email = email
                newsletter.is_synched = False
                newsletter.activation_key = str(uuid.uuid4()).replace('-','')
                newsletter.is_activated = False
                newsletter.save()
                
                send_newsletter_activation(request, newsletter)  
                return redirect('signup_newsletter')
    
    return render_to_response(template_file,
                              context_instance=context)

def activate_newsletter(request, key, template_file = 'common/signups/newsletteractivation.html'):
    context = RequestContext(request)
    signup = NewsletterSignup.objects.get(activation_key=key)
    if not signup.is_activated:
        signup.is_activated = True
        signup.is_synched = False
        signup.save()
        
        if RateAlertsSignup.objects.filter(email__iexact=signup.email).exists():
            rasignup = RateAlertsSignup.objects.get(email__iexact=signup.email)
            rasignup.is_activated = True
            rasignup.save()
            
        if User.objects.filter(active=True, email__iexact=signup.email).exists():
            user = User.objects.get(is_active=True, email__iexact=signup.email)
            try:
                profile = user.profile
            except Profile.DoesNotExist:
                profile = Profile(user=user)
                profile.save()
            except Profile.MultipleObjectsReturned:
                profiles = Profile.objects.filter(user=user)
                profile = profiles[0]
            profile.is_synched = False
            profile.save()
                
    data = {'signup_id' : signup.id}
    context['raform'] = RateAlertsUpsellForm(initial=data)
    return render_to_response(template_file,
                              context_instance=context)

def finish_activation(request, template_file='common/signups/thankyou.html'):
    context = RequestContext(request)
    if request.method == "POST":
        form = RateAlertsUpsellForm(request.POST)
        if form.is_valid():
            signup_id = form.cleaned_data.get('signup_id', None)
            signup = NewsletterSignup.objects.get(id=signup_id)
            email = signup.email
            if RateAlertsSignup.objects.filter(email__iexact=email).exists():
                rasignup = RateAlertsSignup.objects.get(email__iexact=email)
                rasignup.is_activated = True
                rasignup.is_synched = False
                rasignup.save()
            else:
                rasignup = RateAlertsSignup()
                rasignup.email = email
                rasignup.is_activated = True
                rasignup.is_synched = False
                rasignup.save()
            
            if User.objects.filter(email__iexact=signup.email).exists():
                user = User.objects.get(email__iexact=signup.email)
                try:
                    profile = user.profile
                except Profile.DoesNotExist:
                    profile = Profile(user=user)
                    profile.save()
                except Profile.MultipleObjectsReturned:
                    profiles = Profile.objects.filter(user=user)
                    profile = profiles[0]
                profile.is_synched = False
                profile.save()
            return redirect('thankyou_newsletter')
            
    return render_to_response(template_file,
                              context_instance=context)

def activate_ratealert(request, key=None, template_file = 'common/signups/ratealertactivation.html'):
    context = RequestContext(request)
    signup = RateAlertsSignup.objects.get(activation_key=key)
    if not signup.is_activated:
        signup.is_activated = True
        signup.is_synched = False
        signup.save()
        
        if NewsletterSignup.objects.filter(email__iexact=signup.email).exists():
            newssignup = NewsletterSignup.objects.get(email__iexact=signup.email)
            newssignup.is_activated = True
            newssignup.save()
            
        if User.objects.filter(email__iexact=signup.email).exists():
            user = User.objects.get(email__iexact=signup.email)
            try:
                profile = user.profile
            except Profile.DoesNotExist:
                profile = Profile(user=user)
                profile.save()
            except Profile.MultipleObjectsReturned:
                profiles = Profile.objects.filter(user=user)
                profile = profiles[0]
            profile.is_synched = False
            profile.save()
            
    return render_to_response(template_file,
                              context_instance=context)
    
def joint_signup(request):
    context = RequestContext(request)
    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email', None)
            already_newsletter = NewsletterSignup.objects.filter(email__iexact=email).exists()
            already_ratealert = RateAlertsSignup.objects.filter(email__iexact=email).exists()
            if already_newsletter or already_ratealert:
                if already_newsletter and already_ratealert:
                    newsletter = NewsletterSignup.objects.get(email__iexact=email)
                    rasignup = RateAlertsSignup.objects.get(email__iexact=email)
                    if newsletter.is_activated or rasignup.is_activated:
                        newsletter.is_activated = True
                        newsletter.is_synched = False
                        newsletter.save()
                        rasignup.is_activated = True
                        rasignup.is_synched = False                    
                        rasignup.save()
                        return redirect('thankyou_newsletter')
                    else:
                        while RateAlertsSignup.objects.filter(activation_key=rasignup.activation_key).exists():
                            rasignup.activation_key = str(uuid.uuid4()).replace('-','')
                        rasignup.save()
                        send_joint_activation(request, rasignup)
                elif already_newsletter:
                    newsletter = NewsletterSignup.objects.get(email__iexact=email)
                    if newsletter.is_activated:
                        rasignup = create_ratealert(email, True)  
                        return redirect('thankyou_newsletter') 
                    else:
                        rasignup = create_ratealert(email, False)            
                        send_joint_activation(request, rasignup)
                else:
                    rasignup = RateAlertsSignup.objects.get(email__iexact=email)
                    if rasignup.is_activated:
                        newsletter = create_newsletter(email, True)  
                        return redirect('thankyou_newsletter') 
                    else:
                        newsletter = create_newsletter(email, False) 
                        while RateAlertsSignup.objects.filter(activation_key=rasignup.activation_key).exists():
                            rasignup.activation_key = str(uuid.uuid4()).replace('-','')
                        rasignup.save()           
                        send_joint_activation(request, rasignup)
            else:
                #we use the rate alert key to activate both because the rate alerts activation page is generic.
                newsletter = create_newsletter(email, False)            
                rasignup = create_ratealert(email, False)            
                send_joint_activation(request, rasignup)
            
    return redirect('signup_newsletter')
    
def ratealert(request, template_file = 'common/signups/checkemail.html'):
    context = RequestContext(request)
    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email', None)
            try:
                signup = RateAlertsSignup.objects.get(email__iexact=email)
                #someone has tried resigning up - now we need to check if they have activated anywhere else on the site
                if signup.is_activated is False:
                    if User.objects.filter(email__iexact=email).exists():
                        user = User.objects.get(email__iexact=email)
                        if user.is_active:
                            signup.is_activated = True
                            signup.save()
                            try:
                                profile = user.profile
                            except Profile.DoesNotExist:
                                profile = Profile(email__iexact=user)
                                profile.save()
                            except Profile.MultipleObjectsReturned:
                                profiles = Profile.objects.filter(user=user)
                                profile = profiles[0]
                            profile.ratealerts = True
                            profile.is_synched = False
                            profile.save()
                            return redirect('thankyou_newsletter')
                        else:
                            send_ratealert_activation(request, signup)  
                            return redirect('signup_newsletter')
                    elif NewsletterSignup.objects.filter(email__iexact=email).exists():
                        newssignup = NewsletterSignup.objects.get(email__iexact=email)
                        if newssignup.is_activated:
                            signup.is_activated = True
                            signup.save()  
                            return redirect('thankyou_newsletter')
                        else:
                            send_ratealert_activation(request, signup)  
                            return redirect('signup_newsletter')
                    else:
                        send_ratealert_activation(request, signup)  
                        return redirect('signup_newsletter')
                else:
                    return redirect('thankyou_newsletter')            
            except RateAlertsSignup.DoesNotExist:
                ra = RateAlertsSignup()
                ra.email = email
                ra.is_synched = False
                ra.activation_key = str(uuid.uuid4()).replace('-','')
                while RateAlertsSignup.objects.filter(activation_key=ra.activation_key).exists():
                    ra.activation_key = str(uuid.uuid4()).replace('-','')
                ra.is_activated = False
                ra.save()
                
                send_ratealert_activation(request, ra)  
                return redirect('signup_newsletter')
    
    return render_to_response(template_file,
                              context_instance=context)


def savings_health_check(request):
    if request.method == 'POST':
        form = SavingsHealthCheckForm(request.POST)
        if form.is_valid():
            form.save()
            AdviserQueue.add_to_queue(email=form.cleaned_data['email'],
                                      first_name=form.cleaned_data['first_name'],
                                      last_name=form.cleaned_data['last_name'],
                                      lead_source='Healthcheck',
                                      telephone_number=form.cleaned_data['telephone'])
            send_mail('New Savings Healthcheck request',
                      'First name: %s\nLast name: %s\nEmail: %s\nPhone number: %s' % (form.cleaned_data['first_name'],
                                                                                      form.cleaned_data['last_name'],
                                                                                      form.cleaned_data['email'],
                                                                                      form.cleaned_data['telephone']),
                      'savings.champion@savingschampion.co.uk',
                      ['concierge@savingschampion.co.uk'], fail_silently=False)
            return redirect('healthcheck_thankyou')
    else:
        if request.user.is_authenticated():
            form = SavingsHealthCheckForm(initial={'first_name': request.user.first_name,
                                                   'last_name': request.user.last_name,
                                                   'email': request.user.email})
        else:
            form = SavingsHealthCheckForm()
    return render(request, 'common/signups/savings_health_check.html', {'form': form})


def savings_health_check_thankyou(request):
    return render(request, 'common/signups/savings_health_check_thankyou.html')
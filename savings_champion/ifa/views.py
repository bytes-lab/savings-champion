# coding=utf-8
import os
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render
from django.shortcuts import render_to_response
from django.template import RequestContext
from common.accounts.utils import create_stage_one_profile
from common.models import Referrer
from common.tasks import analytics, add_to_campaign_monitor
from common.utils import record_referral_signup
from concierge.models import AdviserQueue
from ifa.forms import IFAForm, BJForm, TPOFactFindForm
from django.template.loader import get_template
from django.template import Context
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

def ifa_landing(request):
    return render(request, 'ifa/landing.html')

def basket_landing(request):
    return render(request, 'ifa/basket_landing.html')

def tpo_signup(request, balance=None):
    if balance == '1':
        form = IFAForm(initial={'signup_amount': '£250,000 - £1million'})
    elif balance == '2':
        form = IFAForm(initial={'signup_amount': '£1million - £5million'})
    elif balance == '3':
        form = IFAForm(initial={'signup_amount': '£5million +'})
    else:
        form = IFAForm()
    if request.method == "POST":
        form = IFAForm(request.POST)

        if form.is_valid():
            form.save()
            if 'referer' in request.session:
                referer = Referrer.objects.get(pk=request.session['referer']).name
            else:
                referer = '(Direct)'
            analytics.delay('event', 'TPO', 'Signup', referer)
            user, user_created, record_stats = create_stage_one_profile(request=request, email=form.cleaned_data.get('email'),
                                                          source='tpo_signup', send_activation=False, login_user=False)

            from common.tasks import update_subscription_on_email_service
            update_subscription_on_email_service.delay(user.email, interest_group=u'TPO Referral')

            text_email = get_template('ifa/ifa_signup_email.txt')
            guide_email = get_template('ifa/ifa_guide_email.txt')
            html_guide_email = get_template('ifa/ifa_guide_email.html')

            client_details = {'name': form.cleaned_data.get('name'),
                              'last_name': form.cleaned_data.get('last_name'),
                              'email': form.cleaned_data.get('email'),
                              'signup_amount': form.cleaned_data.get('signup_amount'),
                              'postcode': form.cleaned_data.get('postcode'),
                              'telephone': form.cleaned_data.get('telephone')}
            c = Context(client_details)

            text_content = text_email.render(c)
            guide_content = guide_email.render(c)
            html_guide_content = html_guide_email.render(c)

            subject, from_email = "New IFA Enquiry", "savings.champion@savingschampion.co.uk"
            to_email = ["ifa@savingschampion.co.uk"]
            AdviserQueue.add_to_queue(client_details['email'],
                                      client_details['name'],
                                      u'.',
                                      u'IFA Signup (TPO) - {value}'.format(value=client_details['signup_amount']),
                                      telephone_number=client_details['telephone'])
            msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
            msg.send()

            subject, from_email = "Your IFA Guide", "info@savingschampion.co.uk"
            msg = EmailMultiAlternatives(subject, guide_content, from_email, [c['email']])
            msg.attach_alternative(html_guide_content, "text/html")
            guide_path = os.path.join(settings.STATIC_ROOT, 'doc', 'ifa',
                                      '9_steps_to_choosing_an_independent_financial_adviser.pdf')
            msg.attach_file(guide_path)
            msg.send()
            record_referral_signup(request, user, user_created, 'tpo_referral')

            return redirect('tpo_thankyou')
        else:
            messages.error(request,
                           'Your input contained errors, or you have already enquired about The Private Office')
    return render(request, 'ifa/tpo_signup_alt.html', {
        'form': form
    })


def bj_signup(request):
    form_1 = BJForm(prefix="bj_form1")
    form_2 = BJForm(prefix="bj_form2")
    if request.method == "POST":
        form_1 = BJForm(request.POST, prefix="bj_form1")
        form_2 = BJForm(request.POST, prefix="bj_form2")
        if form_1.is_valid() or form_2.is_valid():
            if form_1.is_valid():
                form = form_1
            else:
                form = form_2
            form.save()
            if 'referer' in request.session:
                referer = Referrer.objects.get(pk=request.session['referer']).name
            else:
                referer = '(Direct)'
            analytics.delay('event', 'Beckford James', 'Signup', referer)
            user, user_created, record_stats = create_stage_one_profile(request=request, email=form.cleaned_data.get('email'),
                                                          source='beckford_james_signup', send_activation=False,
                                                          login_user=False)

            from common.tasks import update_subscription_on_email_service
            update_subscription_on_email_service.delay(user.email, interest_group=u'Beckford James Referral')

            name = form.cleaned_data.get('name')
            email = form.cleaned_data.get('email')
            telephone = form.cleaned_data.get('telephone')
            postcode = form.cleaned_data.get('postcode')

            text_email = get_template('ifa/bj_signup_email.txt')
            client_details = {'name': name, 'email': email, 'telephone': telephone, 'postcode': postcode}
            c = Context(client_details)

            text_content = text_email.render(c)

            subject, from_email = "New Beckford James Enquiry", "savings.champion@savingschampion.co.uk"
            msg = EmailMultiAlternatives(subject, text_content, from_email,
                                         ["ifa@savingschampion.co.uk", 'sc@beckfordjames.com'])
            msg.send()

            AdviserQueue.add_to_queue(client_details['email'],
                                      client_details['name'],
                                      u'.',
                                      u'IFA (Beckford James) Signup',
                                      telephone_number=client_details['telephone'])

            record_referral_signup(request, user, user_created, 'bj_referral')

            return redirect(reverse('bj_thankyou'))
        else:
            messages.error(request, 'Your input contained errors, or you have already enquired about Beckford James')
    return render(request, 'ifa/bj_signup.html', {
        'bj_form': form_1,
        'bj_form2': form_2
    })


def tpo_thankyou(request, template_file='ifa/tpo_thankyou.html'):
    context = RequestContext(request)
    return render_to_response(template_file,
                              context_instance=context)


def bj_thankyou(request):
    return render(request, 'ifa/bj_thankyou.html')


def tpo_fact_find(request, context=None):
    if context is None:
        context = {}
    form = TPOFactFindForm()
    if request.method == 'POST':
        form = TPOFactFindForm(request.POST)
        if form.is_valid():
            text_email = get_template('ifa/ifa_fact_find_email.txt')
            client_details = {'name': form.cleaned_data.get('name'),
                              'address': form.cleaned_data.get('address'),
                              'office_number': form.cleaned_data.get('office_number'),
                              'home_number': form.cleaned_data.get('home_number'),
                              'mobile_number': form.cleaned_data.get('mobile_number'),
                              'email': form.cleaned_data.get('email'),
                              'marital_status': form.cleaned_data.get('marital_status'),
                              'employment_status': form.cleaned_data.get('employment_status'),
                              'partner_employment_status': form.cleaned_data.get('partner_employment_status'),
                              'occupation': form.cleaned_data.get('occupation'),
                              'partner_occupation': form.cleaned_data.get('partner_occupation'),
                              'total_asset_value': form.cleaned_data.get('total_asset_value'),
                              'partner_total_asset_value': form.cleaned_data.get('partner_total_asset_value'),
                              'joint_total_asset_value': form.cleaned_data.get('joint_total_asset_value'),
                              'total_income': form.cleaned_data.get('total_income'),
                              'partner_total_income': form.cleaned_data.get('partner_total_income'),
                              'joint_total_income': form.cleaned_data.get('joint_total_income'),
                              'protection': form.cleaned_data.get('protection'),
                              'retirement_planning': form.cleaned_data.get('retirement_planning'),
                              'estate_planning': form.cleaned_data.get('estate_planning'),
                              'investment_planning': form.cleaned_data.get('investment_planning')
            }
            c = Context(client_details)

            text_content = text_email.render(c)

            subject, from_email = "New IFA Fact Find", "savings.champion@savingschampion.co.uk"
            to_email = ["ifa@savingschampion.co.uk"]
            msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
            msg.send()

            AdviserQueue.add_to_queue(client_details['email'],
                                      client_details['name'],
                                      u'.',
                                      u'IFA Fact Find (TPO)',
                                      telephone_number=client_details['home_number'])
            return redirect('tpo_fact_find_thankyou')

    context['form'] = form
    return render(request, 'ifa/tpo_fact_find.html', context)


def tpo_fact_find_thankyou(request, context=None):
    if context is None:
        context = {}

    return render(request, 'ifa/ifa_fact_find_thankyou.html', context)
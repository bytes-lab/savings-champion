# coding=utf-8
import datetime
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import permission_required
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.shortcuts import render
from django.template import Template, Context
from django.views.decorators.cache import never_cache
from common.accounts.utils import create_stage_one_profile
from common.utils import record_referral_signup
from concierge.forms import SignedForm, AddClientForm, IllustrationForm, RecommendedForm, UnsuitableForm, FakeForm, \
    NoContactForm
from concierge.models import AdviserQueue, ConciergeUserPool

__author__ = 'josh'

User = get_user_model()


@never_cache
@permission_required('concierge.adviser')
def adviser_dashboard(request, context=None):
    if context is None:
        context = {}

    context['signed_form'] = SignedForm()
    context['add_client_form'] = AddClientForm()
    context['illustration_form'] = IllustrationForm()
    context['recommended_form'] = RecommendedForm()
    context['unsuitable_form'] = UnsuitableForm()
    context['fake_form'] = FakeForm()
    context['no_contact_form'] = NoContactForm()
    return render(request, 'concierge/adviser/dashboard.html', context)


@never_cache
@permission_required('concierge.adviser')
def adviser_statistics_ajax(request, context=None):
    if context is None:
        context = {}

    context['concierge_enquiries'] = AdviserQueue.objects.filter(adviser=None).exclude(status=2)
    context['adviser_clients'] = AdviserQueue.objects.filter(adviser=request.user)
    context['adviser_clients_pending'] = context['adviser_clients'].filter(status__in=[0, 5, 6, 7]).count()
    context['adviser_clients_contacted'] = context['adviser_clients'].filter(status=1).count()
    context['adviser_clients_fake'] = context['adviser_clients'].filter(status=2).count()
    context['adviser_clients_fact_find'] = context['adviser_clients'].filter(status=3).count()
    context['adviser_clients_illustrated'] = context['adviser_clients'].filter(status=4).count()
    context['adviser_clients_unsuitable'] = context['adviser_clients'].filter(status=8).count()
    context['adviser_clients_signed'] = context['adviser_clients'].filter(status=9).count()
    context['adviser_clients_emailed'] = context['adviser_clients'].filter(status=10).count()
    context['adviser_clients_recommendation'] = context['adviser_clients'].filter(status=11).count()
    return render(request, 'concierge/adviser/dashboard_statistics.html', context)


@never_cache
@permission_required('concierge.adviser')
def adviser_personal_leads_ajax(request, context=None):
    if context is None:
        context = {}

    context['adviser_clients_in_progress'] = AdviserQueue.objects.filter(adviser=request.user).exclude(
        status__in=[9, 8, 2, 10])
    return render(request, 'concierge/adviser/dashboard_personal_leads.html', context)


@never_cache
@permission_required('concierge.adviser')
def adviser_unclaimed_leads_ajax(request, context=None):
    if context is None:
        context = {}

    context['concierge_enquiries'] = AdviserQueue.objects.filter(adviser=None).exclude(status=2).order_by('-interaction_started')[:300]
    return render(request, 'concierge/adviser/dashboard_unclaimed_leads.html', context)


@never_cache
@permission_required('concierge.adviser')
def adviser_recent_leads_ajax(request, context=None, name=None, email=None, telephone=None):
    if context is None:
        context = {}

    context['adviser_clients_recent'] = AdviserQueue.objects.filter(adviser=request.user).order_by('interaction_ended')
    if name is not None:
        context['adviser_clients_recent'] = context['adviser_clients_recent'].filter(name__icontains=name)
    elif email is not None:
        context['adviser_clients_recent'] = context['adviser_clients_recent'].filter(email__icontains=email)
    elif telephone is not None:
        context['adviser_clients_recent'] = context['adviser_clients_recent'].filter(telephone__icontains=telephone)

    context['adviser_clients_recent'] = context['adviser_clients_recent'][:100]
    return render(request, 'concierge/adviser/dashboard_recent_leads.html', context)


@permission_required('concierge.adviser')
def adviser_claim_client_ajax(request, enquiry_id):
    leads = AdviserQueue.objects.filter(adviser=None, pk=enquiry_id)
    existing_claimed = AdviserQueue.objects.filter(status=0, adviser=request.user).exists()
    if leads.exists():
        if not existing_claimed:  # Ensure advisers are unable to stockpile leads
            for lead in leads:
                lead.adviser = request.user
                response_time = datetime.datetime.now() - lead.interaction_started
                lead.claim_time = response_time
                lead.save()
            return HttpResponse(status=204)
        return HttpResponse(status=409, content='{"status":"deal with current claimed first"}')
    return HttpResponse(status=409, content='{"status":"doesn\'t exist"}')


@permission_required('concierge.adviser')
def adviser_fake_client_ajax(request, enquiry_id):
    if request.method == 'POST':
        if AdviserQueue.objects.filter(pk=enquiry_id).exists():
            form = UnsuitableForm(request.POST)
            if form.is_valid():
                for client in AdviserQueue.objects.filter(pk=enquiry_id):
                    client.status = 2
                    client.unsuitable_reason = form.cleaned_data['reason']
                    client.add_note('Client marked as fake: %s' % form.cleaned_data['reason'])
                    client.save()
                return HttpResponse(status=204)
    return HttpResponse(status=409, content='{"status":"doesn\'t exist"}')


@permission_required('concierge.adviser')
def adviser_contacted_client_ajax(request, enquiry_id):
    if AdviserQueue.objects.filter(adviser=request.user, pk=enquiry_id).exists():
        for client in AdviserQueue.objects.filter(adviser=request.user, pk=enquiry_id):
            client.status = 1
            client.add_note('Client Contacted')
            client.save()
        return HttpResponse(status=204)
    return HttpResponse(status=409, content='{"status":"doesn\'t exist"}')


@permission_required('concierge.adviser')
def adviser_fact_find_client_ajax(request, enquiry_id):
    if AdviserQueue.objects.filter(adviser=request.user, pk=enquiry_id).exists():
        for client in AdviserQueue.objects.filter(adviser=request.user, pk=enquiry_id):
            client.status = 3
            client.add_note('Client fact find performed')
            client.save()
        return HttpResponse(status=204)
    return HttpResponse(status=409, content='{"status":"doesn\'t exist"}')


@permission_required('concierge.adviser')
def adviser_recommended_client_ajax(request, enquiry_id):
    if request.method == "POST":
        if AdviserQueue.objects.filter(adviser=request.user, pk=enquiry_id).exists():
            form = RecommendedForm(request.POST)
            if form.is_valid():
                aq = AdviserQueue.objects.get(adviser=request.user, pk=enquiry_id)
                aq.status = 11
                aq.portfolio_value = form.cleaned_data['funds_under_management']
                aq.add_note('Client recommendations sent with £%d' % form.cleaned_data['funds_under_management'])
                aq.save()
                try:
                    user = User.objects.get(email=aq.email)
                except User.DoesNotExist:
                    user, _, record_stats = create_stage_one_profile(request, aq.email, 'manual_add_concierge', send_activation=False,
                                                       login_user=False)
                pool, _ = ConciergeUserPool.objects.get_or_create(term=0, user=user,
                                                                  balance=form.cleaned_data['funds_under_management'])
                return HttpResponse(status=204)
            return HttpResponse(status=409, content='{"status":"error in form"}')
        return HttpResponse(status=409, content='{"status":"doesn\'t exist"}')
    return HttpResponse(status=409, content='{"status":"not post"}')


@permission_required('concierge.adviser')
def adviser_illustrated_client_ajax(request, enquiry_id):
    if request.method == "POST":
        if AdviserQueue.objects.filter(adviser=request.user, pk=enquiry_id).exists():
            form = IllustrationForm(request.POST)
            if form.is_valid():

                aq = AdviserQueue.objects.get(adviser=request.user, pk=enquiry_id)
                aq.status = 4
                aq.portfolio_value = form.cleaned_data['funds_under_management']
                aq.add_note('Client illustrated with £%d' % form.cleaned_data['funds_under_management'])
                aq.save()
                try:
                    user = User.objects.get(email=aq.email)
                except User.DoesNotExist:
                    user, _, record_stats = create_stage_one_profile(request, aq.email, 'manual_add_concierge', send_activation=False,
                                                       login_user=False)
                pool, _ = ConciergeUserPool.objects.get_or_create(term=0, user=user, balance=form.cleaned_data['funds_under_management'])
                return HttpResponse(status=204)
            return HttpResponse(status=409, content='{"status":"error in form"}')
        return HttpResponse(status=409, content='{"status":"doesn\'t exist"}')
    return HttpResponse(status=409, content='{"status":"not post"}')


@permission_required('concierge.adviser')
def adviser_signed_client_ajax(request, enquiry_id):
    if request.method == 'POST':
        if AdviserQueue.objects.filter(adviser=request.user, pk=enquiry_id).exists():
            adviser_queue = AdviserQueue.objects.get(pk=enquiry_id)
            form = SignedForm(request.POST, instance=adviser_queue)
            if form.is_valid():
                form.save()
                adviser_queue.status = 9
                adviser_queue.add_note('Client signed up with £%d, fee was charged as £%d' % (form.cleaned_data['portfolio_value'], form.cleaned_data['fee']))
                adviser_queue.save()
                try:
                    user = User.objects.get(email=adviser_queue.email)
                except User.DoesNotExist:
                    user, _, record_stats = create_stage_one_profile(request, adviser_queue.email, 'manual_add_concierge',
                                                       send_activation=False, login_user=False)
                record_referral_signup(request, user, True, 'concierge_client')
                return HttpResponse(status=204)
            else:
                assert False, form.errors
        return HttpResponse(status=409, content='{"status":"doesn\'t exist"}')
    return HttpResponse(status=409, content='{"status":"not post"}')


@permission_required('concierge.adviser')
def adviser_unsuitable_client_ajax(request, enquiry_id):
    if request.method == 'POST':
        if AdviserQueue.objects.filter(adviser=request.user, pk=enquiry_id).exists():
            form = UnsuitableForm(request.POST)
            if form.is_valid():
                for client in AdviserQueue.objects.filter(adviser=request.user, pk=enquiry_id):
                    client.status = 8
                    client.unsuitable_reason = form.cleaned_data['reason']
                    client.add_note('Client marked unsuitable: %s' % form.cleaned_data['reason'])
                    client.save()
                return HttpResponse(status=204)
    return HttpResponse(status=409, content='{"status":"exists"}')


@permission_required('concierge.adviser')
def adviser_no_contact_client_ajax(request, enquiry_id, stage):
    if AdviserQueue.objects.filter(adviser=request.user, pk=enquiry_id).exists():
        if stage == u'1':
            for client in AdviserQueue.objects.filter(adviser=request.user, pk=enquiry_id):
                client.status = 5
                client.add_note('Client could not be contacted x1')
                client.save()
        elif stage == u'2':
            for client in AdviserQueue.objects.filter(adviser=request.user, pk=enquiry_id):
                client.status = 6
                client.add_note('Client could not be contacted x2')
                client.save()
        elif stage == u'3':
            for client in AdviserQueue.objects.filter(adviser=request.user, pk=enquiry_id):
                client.status = 7
                client.add_note('Client could not be contacted x3')
                client.save()
        elif stage == u'4':
            for client in AdviserQueue.objects.filter(adviser=request.user, pk=enquiry_id):
                client.status = 10
                client.add_note('Client was emailed')
                client.save()
            if request.method == 'POST':
                form = NoContactForm(request.POST)
                if form.is_valid():
                    adviser_queue = AdviserQueue.objects.get(pk=enquiry_id)
                    body = form.cleaned_data['template'].body
                    template = Template(body)
                    client_name = form.cleaned_data['client_name'] if form.cleaned_data['client_name'] != '' else adviser_queue.name
                    context = Context({'client_name': client_name,
                                       'adviser': request.user})
                    rendered_template = template.render(context)

                    email = EmailMessage('We tried to return your enquiry, but unfortunately we\'ve missed you',
                                         rendered_template, 'info@savingschampion.co.uk',
                                         [adviser_queue.email],
                                         headers={'Reply-To': request.user.email})

                    email.send(fail_silently=False)
                    return HttpResponse(status=204)
                return HttpResponse(status=500, content=form.errors)
            else:
                return HttpResponse(status=405)
        else:
            return HttpResponse(status=500)
        return HttpResponse(status=204)
    return HttpResponse(status=409, content='{"status":"exists"}')


@never_cache
@permission_required('concierge.adviser')
def adviser_add_client_ajax(request, context=None):
    if context is None:
        context = {}

    if request.method == "POST":
        form = AddClientForm(request.POST)
        if form.is_valid():
            new_client = form.save(commit=False)
            new_client.adviser = request.user
            new_client.add_note('Client was added manually')
            new_client.save()
            create_stage_one_profile(request, new_client.email, 'manual_add_concierge', send_activation=False,
                                     login_user=False)
            return HttpResponse(status=204)
        return HttpResponse(status=409, content='{"status":"%s"}' % form.errors)
    return HttpResponse(status=409, content='{"status":"exists"}')
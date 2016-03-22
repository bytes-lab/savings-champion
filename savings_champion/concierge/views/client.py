import json
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from common.accounts.utils import create_stage_one_profile
from common.utils import record_referral_signup
from concierge.forms import ConciergeUserOptionForm, ConciergeUserNotesForm, ConciergeLeadCaptureForm
from concierge.models import AdviserQueue, ConciergeUserOption, ConciergeUserNotes, ConciergeLeadCapture

User = get_user_model()

__author__ = 'josh'


@never_cache
@permission_required('concierge.adviser')
def adviser_client_dashboard(request, client_id, context=None):
    if context is None:
        context = {}
    if AdviserQueue.objects.filter(pk=client_id, adviser=request.user).exists():
        adviser_queue = AdviserQueue.objects.get(pk=client_id, adviser=request.user)
        try:
            user = User.objects.get(email=adviser_queue.email)
            user_created = False
        except User.DoesNotExist:
            create_profile_output = create_stage_one_profile(request, adviser_queue.email, source='Concierge Signup',
                                                             send_activation=False, login_user=False)
            if isinstance(create_profile_output, tuple):
                user, user_created, record_stats = create_profile_output
            else:
                return create_profile_output
            record_referral_signup(request=request, user=user, user_created=user_created, action='signup')
        context['concierge_user'], _ = ConciergeUserOption.objects.get_or_create(user=user)
        context['user_options_form'] = ConciergeUserOptionForm(instance=context['concierge_user'])
        context['user_notes_form'] = ConciergeUserNotesForm(initial={'user': user})
        context['user_notes'] = ConciergeUserNotes.objects.filter(user=user)

        concierge_lead_capture, _ = ConciergeLeadCapture.objects.get_or_create(user=user, named_user=True)
        context['lead_capture_first'] = ConciergeLeadCaptureForm(prefix='first_client', instance=concierge_lead_capture)

        concierge_lead_capture, _ = ConciergeLeadCapture.objects.get_or_create(user=user, named_user=False)
        context['lead_capture_second'] = ConciergeLeadCaptureForm(prefix='second_client', instance=concierge_lead_capture)
        record_referral_signup(request=request, user=user, user_created=user_created, action='concierge_enquiry')

        return render(request, 'concierge/adviser/client_dashboard.html', context)
    return HttpResponse(status=403)


def adviser_client_notes(request, context=None):
    if context is None:
        context = {}
    form = ConciergeUserNotesForm()
    if request.method == "POST":
        form = ConciergeUserNotesForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            form = ConciergeUserNotesForm(initial={'user': note.user})
            note.save()
            context['user_notes'] = ConciergeUserNotes.objects.filter(user=note.user)
        else:
            if 'user' in request.POST:
                if User.objects.filter(pk=request.POST['user']).exists():
                    user = User.objects.get(pk=request.POST['user'])
                    context['user_notes'] = ConciergeUserNotes.objects.filter(user=user)

    context['user_notes_form'] = form
    return render(request, 'concierge/adviser/user_notes.html', context)


def update_client_details(request, client_id, context=None):

    if context is None:
        context = {}
    if request.method == "POST":
        user = User.objects.get(pk=client_id)
        if AdviserQueue.objects.filter(email=user.email, adviser=request.user).exists():

            first_instance = ConciergeLeadCapture.objects.get(user=user, named_user=True)
            first_form = ConciergeLeadCaptureForm(request.POST, instance=first_instance, prefix='first_client')
            if first_form.has_changed():
                if first_form.is_valid():
                    first_form.save()
                else:
                    messages.error(request, 'First Form Was Not Valid.')
            context['lead_capture_first'] = first_form

            second_instance = ConciergeLeadCapture.objects.get(user=user, named_user=False)
            second_form = ConciergeLeadCaptureForm(request.POST, instance=second_instance, prefix='second_client')
            if second_form.has_changed():
                if second_form.is_valid():
                    second_form.save()
                else:
                    messages.error(request, 'Second Form Was Not Valid.')
            context['lead_capture_second'] = second_form

            return render(request, 'concierge/adviser/client_dashboard_lead_capture_form.html', context)
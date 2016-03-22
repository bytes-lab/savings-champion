from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import permission_required
from django.db.models.aggregates import Min, Avg
from django.shortcuts import render
from administration.forms import ReferrerForm
from common.models import Referrer, UserReferral
from concierge.forms import DateFilterForm
from concierge.models import AdviserQueue, ADVISER_QUEUE_CHOICES, SOURCE_LIST

User = get_user_model()

__author__ = 'josh'


def filter_data(request):
    start_date, end_date = date_filtering(request)
    referrer = None
    try:
        referrer = Referrer.objects.get(pk=request.GET.get('referrer'))
    except Referrer.DoesNotExist:
        pass
    return start_date, end_date, referrer


def date_filtering(request):
    week_ago = datetime.now() - timedelta(weeks=1)
    today = datetime.now() + timedelta(days=1)
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date is None and start_date != '':
        start_date = week_ago
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if end_date is None and end_date != '':
        end_date = today
    else:
        end_date = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
    return start_date, end_date


@permission_required('concierge.manage_advisers')
def management_dashboard(request, context=None):
    if context is None:
        context = {}
    context['date_form'] = DateFilterForm(initial={
        'start_date': (datetime.now() - timedelta(weeks=1)).strftime('%Y-%m-%d'),
        'end_date': datetime.now().strftime('%Y-%m-%d')
    })
    return render(request, 'concierge/management/dashboard.html', context)


@permission_required('concierge.manage_advisers')
def management_statistics_ajax(request, context=None):
    if context is None:
        context = {}

    start_date, end_date, referrer = filter_data(request)

    context['records_began'] = AdviserQueue.objects.exclude(interaction_started=None).aggregate(
        Min('interaction_started'))

    all_adviser_leads = AdviserQueue.objects.all()
    all_adviser_leads_in_date = all_adviser_leads.filter(interaction_ended__gte=start_date,
                                                         interaction_ended__lte=end_date)

    if referrer is not None:
        user_referrals = UserReferral.objects.filter(referrer=referrer).values('user__email')
        all_adviser_leads = all_adviser_leads.filter(email__in=user_referrals)

    context['concierge_enquiries_no_limit'] = all_adviser_leads.filter(adviser=None).exclude(status=2)

    context['concierge_enquiries'] = all_adviser_leads_in_date.filter(adviser=None).exclude(status=2)

    all_adviser_leads = all_adviser_leads.exclude(adviser=None)
    all_adviser_leads_in_date = all_adviser_leads_in_date.exclude(adviser=None)

    context['clients'] = all_adviser_leads_in_date
    context['clients_pending'] = context['clients'].filter(status=0).count()
    context['clients_attempted_contacted'] = context['clients'].filter(status__in=[5, 6, 7]).count()
    context['clients_contacted'] = context['clients'].filter(status=1).count()
    context['clients_fake'] = context['clients'].filter(status=2).count()
    context['clients_fact_find'] = context['clients'].filter(status=3).count()
    context['clients_illustrated'] = context['clients'].filter(status=4).count()
    context['clients_unsuitable'] = context['clients'].filter(status=8).count()
    context['clients_signed'] = context['clients'].filter(status=9).count()
    context['clients_emailed'] = context['clients'].filter(status=10).count()
    context['clients_recommendation'] = context['clients'].filter(status=11).count()
    context['clients_total'] = AdviserQueue.objects.filter(interaction_started__gte=start_date,
                                                           interaction_started__lte=end_date).count()

    context['clients_no_limit'] = all_adviser_leads
    context['clients_pending_no_limit'] = context['clients_no_limit'].filter(status=0).count()
    context['clients_attempted_contacted_no_limit'] = context['clients_no_limit'].filter(status__in=[5, 6, 7]).count()
    context['clients_contacted_no_limit'] = context['clients_no_limit'].filter(status=1).count()
    context['clients_fake_no_limit'] = context['clients_no_limit'].filter(status=2).count()
    context['clients_fact_find_no_limit'] = context['clients_no_limit'].filter(status=3).count()
    context['clients_illustrated_no_limit'] = context['clients_no_limit'].filter(status=4).count()
    context['clients_unsuitable_no_limit'] = context['clients_no_limit'].filter(status=8).count()
    context['clients_signed_no_limit'] = context['clients_no_limit'].filter(status=9).count()
    context['clients_emailed_no_limit'] = context['clients_no_limit'].filter(status=10).count()
    context['clients_recommendation_no_limit'] = context['clients_no_limit'].filter(status=11).count()
    context['clients_total_no_limit'] = AdviserQueue.objects.count()

    return render(request, 'concierge/management/dashboard_statistics.html', context)


@permission_required('concierge.manage_advisers')
def management_adviser_workload_ajax(request, context=None):
    if context is None:
        context = {}

    start_date, end_date, referrer = filter_data(request)

    context['advisers'] = {}
    adviser_queue = AdviserQueue.objects.filter(interaction_ended__gte=start_date,
                                                interaction_ended__lte=end_date)

    if referrer is not None:
        user_referrals = UserReferral.objects.filter(referrer=referrer).values('user__email')
        adviser_queue = adviser_queue.filter(email__in=user_referrals)

    advisers = User.objects.filter(is_staff=True, adviserqueue__in=adviser_queue)
    for adviser in advisers:
        adviser_leads = adviser_queue.filter(adviser=adviser)

        context['advisers'][adviser] = {}
        context['advisers'][adviser]['pending'] = adviser_leads.filter(status=0).count()
        context['advisers'][adviser]['attempted_contact'] = adviser_leads.filter(status__in=[5, 6, 7]).count()
        context['advisers'][adviser]['contacted'] = adviser_leads.filter(status=1).count()
        context['advisers'][adviser]['fake'] = adviser_leads.filter(status=2).count()
        context['advisers'][adviser]['fact_find'] = adviser_leads.filter(status=3).count()
        context['advisers'][adviser]['illustrated'] = adviser_leads.filter(status=4).count()
        context['advisers'][adviser]['no_contact'] = adviser_leads.filter(status=5).count()
        context['advisers'][adviser]['no_contact_2'] = adviser_leads.filter(status=6).count()
        context['advisers'][adviser]['no_contact_3'] = adviser_leads.filter(status=7).count()
        context['advisers'][adviser]['unsuitable'] = adviser_leads.filter(status=8).count()
        context['advisers'][adviser]['signed'] = adviser_leads.filter(status=9).count()
        context['advisers'][adviser]['emailed'] = adviser_leads.filter(status=10).count()
        context['advisers'][adviser]['recommendation'] = adviser_leads.filter(status=11).count()
        context['advisers'][adviser]['all'] = adviser_leads.all().count()
        context['start_date'] = start_date
        context['end_date'] = end_date
        context['referrer'] = referrer

    return render(request, 'concierge/management/dashboard_adviser_workload.html', context)


@permission_required('concierge.manage_advisers')
def management_adviser_reason(request, context=None):
    if context is None:
        context = {}

    start_date, end_date, referrer = filter_data(request)

    adviser_leads = AdviserQueue.objects.filter(interaction_ended__gte=start_date,
                                                interaction_ended__lte=end_date)

    if referrer is not None:
        user_referrals = UserReferral.objects.filter(referrer=referrer).values('user__email')
        adviser_leads = adviser_leads.filter(email__in=user_referrals)

    if 'adviser' in request.GET:
        adviser_id = request.GET['adviser']
        adviser = User.objects.get(pk=adviser_id)
        adviser_leads = adviser_leads.filter(adviser=adviser)

    if 'status' in request.GET:
        status = request.GET['status']
        adviser_leads = adviser_leads.filter(status=int(status))

    if 'source' in request.GET:
        source = request.GET['source']
        adviser_leads = adviser_leads.filter(source=source)

    adviser_leads = adviser_leads.values_list('name', 'email', 'unsuitable_reason', 'adviser__email', 'telephone')

    context['reasons'] = list(adviser_leads)

    return render(request, 'concierge/management/dashboard_adviser_reason.html', context)


@permission_required('concierge.manage_advisers')
def management_source_pipeline_ajax(request, context=None):
    if context is None:
        context = {}
    start_date, end_date, referrer = filter_data(request)
    lead_source = {}
    adviser_queue_objects = AdviserQueue.objects.filter(interaction_ended__gte=start_date,
                                                        interaction_ended__lte=end_date)

    if referrer is not None:
        user_referrals = UserReferral.objects.filter(referrer=referrer).values('user__email')
        adviser_queue_objects = adviser_queue_objects.filter(email__in=user_referrals)

    for source_id, source_display in SOURCE_LIST:
        lead_source[source_id] = {}
        for status_id, status_display in ADVISER_QUEUE_CHOICES:
            lead_source[source_id][status_id] = adviser_queue_objects.exclude(adviser=None).filter(source=source_id,
                                                                                                   status=status_id).count()
        lead_source[source_id]['total'] = adviser_queue_objects.filter(source=source_id).count()
        lead_source[source_id]['unclaimed'] = adviser_queue_objects.filter(status=0, source=source_id).count()

    context['lead_source'] = lead_source

    return render(request, 'concierge/management/source-pipeline.html', context)


@permission_required('concierge.manage_advisers')
def management_adviser_timing_ajax(request, context=None):
    if context is None:
        context = {}
    start_date, end_date, referrer = filter_data(request)

    timing_data = []

    adviser_queue_objects = AdviserQueue.objects.filter(interaction_ended__gte=start_date,
                                                        interaction_ended__lte=end_date).exclude(_claim_time=None)

    if referrer is not None:
        user_referrals = UserReferral.objects.filter(referrer=referrer).values('user__email')
        adviser_queue_objects = adviser_queue_objects.filter(email__in=user_referrals)

    advisers = User.objects.filter(pk__in=adviser_queue_objects.values_list('adviser', flat=True))

    for adviser in advisers:
        timing_data.append({'adviser': adviser.email,
                            'claim_time': timedelta(
                                seconds=adviser_queue_objects.filter(adviser=adviser).aggregate(claim_time=Avg('_claim_time'))['claim_time']
                            )
                            })

    context['timing_data'] = timing_data

    return render(request, 'concierge/management/adviser_timing.html', context)
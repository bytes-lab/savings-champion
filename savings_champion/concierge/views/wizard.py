from django.shortcuts import render
from concierge.forms import ConciergeBasicInformationForm, ConciergeNotQualifiedForm, ConciergeNotSuitableForm
from concierge.models import AdviserQueue


def concierge_wizard(request, client_id, context=None):
    if context is None:
        context = {}

    if request.method == 'POST':
        basic_information = ConciergeBasicInformationForm(client_id, request.POST)
        not_qualified = ConciergeNotQualifiedForm(client_id, request.POST)
        not_suitable = ConciergeNotSuitableForm(client_id, request.POST)

        if basic_information.is_valid():
            basic_information.save()

        if not_qualified.is_valid():
            not_qualified.save(client_id)

        if not_suitable.is_valid():
            not_suitable.save(client_id)

        context['basic_information'] = basic_information
        context['not_qualified'] = not_qualified
        context['not_suitable'] = not_suitable

    else:
        adviser_queue = AdviserQueue.objects.get(pk=client_id)
        context['basic_information'] = ConciergeBasicInformationForm(client_id, initial={'email': adviser_queue.email})
        context['not_qualified'] = ConciergeNotQualifiedForm(client_id)
        context['not_suitable'] = ConciergeNotSuitableForm(client_id)

    return render(request, 'concierge/wizard/steps.html', context)
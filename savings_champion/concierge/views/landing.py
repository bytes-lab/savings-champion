# coding=utf-8
from datetime import datetime
from decimal import InvalidOperation, Decimal
import json
from PIL.Image import new as new_image
from PIL.ImageDraw import Draw
from PIL.ImageFont import truetype
from celery.result import AsyncResult
from django import forms
from django.contrib import messages
from django.contrib.auth import get_user_model, authenticate, login
from django.core.urlresolvers import reverse
from django.forms.models import modelformset_factory
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.cache import never_cache
from common.accounts.forms import IndexSignupform
from common.accounts.utils import create_stage_one_profile
from common.utils import record_referral_signup
from concierge.forms import ConciergeUserPoolForm,  ConciergeUserOptionPublicForm, \
    ConciergeUserPublicPoolForm, ConciergeUserPoolType, ConciergeLandingContactForm, ConciergeLandingContactFormHelper, \
    ConciergeUserPoolFormHelper, ThisIsMoneyConciergeWidgetPoolForm
from concierge.models import ConciergeUserPool, ConciergeUserOption, AdviserQueue
from uuid import uuid4
from concierge.tasks import async_compare_existing_portfolio_to_generated, deactivate_old_temporary_user

User = get_user_model()


def get_temporary_user(request, uuid=None):
    if request.user.is_anonymous():
        if uuid is None:
            uuid = str(uuid4())[0:29]
            email = '%s@local' % uuid
            user, user_created, record_stats = create_stage_one_profile(request, email=email, source='concierge_landing_pages',
                                                          send_activation=False)
            if user_created:
                temp_fake_password = 'hoogaboogah93857238975!"£$!"£'
                user.set_password(temp_fake_password)
                user.save()
                user = authenticate(email=email, password=temp_fake_password)
                if user is not None:
                    login(request, user)
                    deactivate_old_temporary_user.apply_async((email,), countdown=(60 * 60 * 24))
        else:
            user = get_object_or_404(User, pk=uuid)
    else:
        user = request.user
    try:  # Ensure at least one
        ConciergeUserPool.objects.get_or_create(user=user)
    except ConciergeUserPool.MultipleObjectsReturned:
        pass
    ConciergeUserOption.objects.get_or_create(user=user)
    return user


def index(request, uuid=None, context=None):
    if context is None:
        context = {}

    #user = get_temporary_user(request, uuid)

    ConciergeUserPoolFormset = modelformset_factory(ConciergeUserPool, form=ConciergeUserPublicPoolForm, widgets={'user': forms.HiddenInput}, can_delete=True, extra=0)
    context['formset_helper'] = ConciergeUserPoolForm()
    #context['personal_pools'] = ConciergeUserPoolFormset(queryset=ConciergeUserPool.objects.filter(user=user), prefix='personal')
    context['account_type'] = ConciergeUserPoolType()
    context['signup_form'] = ConciergeLandingContactForm()
    context['signup_form_helper'] = ConciergeLandingContactFormHelper()
    context['form'] = IndexSignupform()

    #context['user'] = user
    if request.method == "POST":

        contact_form = ConciergeLandingContactForm(request.POST)
        if contact_form.is_valid():
            adviser_queue, _ = AdviserQueue.objects.get_or_create(email=contact_form.cleaned_data['email'])
            adviser_queue.telephone = contact_form.cleaned_data['phone']
            adviser_queue.name = contact_form.cleaned_data['name']
            adviser_queue.source = 'Concierge Page'
            adviser_queue.save()
            AdviserQueue.add_to_queue(email=contact_form.cleaned_data['email'],
                                      first_name=contact_form.cleaned_data['name'],
                                      last_name='.',
                                      lead_source='Concierge Page',
                                      telephone_number=contact_form.cleaned_data['phone'])
            messages.success(request, 'Your enquiry has been sent to our advisers.')
            user, created, record_stats = create_stage_one_profile(request=request, email=contact_form.cleaned_data['email'],
                                                     source='concierge_landing_pages', send_activation=False,
                                                     login_user=False)
            record_referral_signup(request=request, user=user, user_created=created, action='signup')
            record_referral_signup(request=request, user=user, user_created=created, action='concierge_pages', third_party=False)

        # request_post = request.POST.copy()
        # for field, value in request_post.iteritems():
        #     if 'user' in field:
        #         request_post[field] = user.pk
        #
        #
        # updated_formset = ConciergeUserPoolFormset(request_post, prefix='personal')
        # valid = updated_formset.is_valid()
        # if valid:
        #     updated_formset.save()
        #     updated_formset = ConciergeUserPoolFormset(queryset=ConciergeUserPool.objects.filter(
        #         user=user), prefix='personal')
        # context['personal_pools'] = updated_formset
        #
        # concierge_pool_type = ConciergeUserPoolType(request.POST)
        # if concierge_pool_type.is_valid():
        #     account_type = concierge_pool_type.cleaned_data['account_type']
        #     concierge_user_option, created = ConciergeUserOption.objects.get_or_create(user=user)
        #     if account_type == 'charity':
        #         concierge_user_option.charity = True
        #         concierge_user_option.business = False
        #     elif account_type == 'business':
        #         concierge_user_option.charity = False
        #         concierge_user_option.business = True
        #     else:
        #         concierge_user_option.charity = False
        #         concierge_user_option.business = False
        #     concierge_user_option.save()
        #
        # context['concierge_user_id'] = ConciergeUserOption.objects.get(user=user).pk
        # url = reverse('concierge_landing_stage_one', kwargs={'uuid': user.pk})
        # return HttpResponseRedirect('%s#rate-indication' % url)
    return render(request, 'concierge/landing/index.html', context)

@never_cache
def stage_one(request, uuid=None, context=None):
    if context is None:
        context = {}

    user = get_temporary_user(request, uuid)

    context['worst_engine_output_task_id'] = async_compare_existing_portfolio_to_generated.delay(email=user.email)
    context['best_engine_output_task_id'] = async_compare_existing_portfolio_to_generated.delay(email=user.email, best_case=True)
    context['signup_form'] = ConciergeLandingContactForm()
    context['signup_form_helper'] = ConciergeLandingContactFormHelper()


    concierge_user_option, _ = ConciergeUserOption.objects.get_or_create(user=user)
    context['user_options_form'] = ConciergeUserOptionPublicForm(instance=concierge_user_option, initial={'birth_date': datetime.now})

    if request.method == "POST":

        contact_form = ConciergeLandingContactForm(request.POST)
        if contact_form.is_valid():
            adviser_queue, _ = AdviserQueue.objects.get_or_create(email=contact_form.cleaned_data['email'])
            adviser_queue.telephone = contact_form.cleaned_data['telephone']
            adviser_queue.name = contact_form.cleaned_data['name']
            adviser_queue.source = 'Concierge Page'
            adviser_queue.save()
            AdviserQueue.add_to_queue(email=contact_form.cleaned_data['email'],
                                      first_name=contact_form.cleaned_data['name'],
                                      last_name='.',
                                      lead_source='Concierge Page',
                                      telephone_number=contact_form.cleaned_data['phone'])
            user, created, record_stats = create_stage_one_profile(request=request, email=contact_form.cleaned_data['email'],
                                                     source='concierge_landing_pages', send_activation=False,
                                                     login_user=False)
            record_referral_signup(request, user, True, 'concierge_pages', third_party=False)

        user_options_form = ConciergeUserOptionPublicForm(request.POST, instance=concierge_user_option)

        if user_options_form.is_valid():
            user_options = user_options_form.save(commit=False)
            user_options.user = user
            user_options.save()
            url = reverse('concierge_landing_stage_two', kwargs={'uuid': user.pk})
            return HttpResponseRedirect('%s#rate-indication' % url)
        else:
            context['user_options_form'] = user_options_form

    return render(request, 'concierge/landing/stage_one.html', context)


def stage_one_async(request, context=None):
    if context is None:
        context = {}
    if request.method == 'POST' and 'worst_engine_output_task_id' in request.POST and 'best_engine_output_task_id' in request.POST:
        worst_engine_output_task_id = request.POST.get('worst_engine_output_task_id')
        best_engine_output_task_id = request.POST.get('best_engine_output_task_id')
        worst_engine_output_task = AsyncResult(worst_engine_output_task_id)
        best_engine_output_task = AsyncResult(best_engine_output_task_id)
        context['worst_task_complete'] = worst_engine_output_task.ready()
        context['best_task_complete'] = best_engine_output_task.ready()
        if context['worst_task_complete'] and context['best_task_complete']:
            task_output = worst_engine_output_task.result
            try:
                context['minimum_rate'] = (task_output['generated_interest'] / task_output['total_amount']) * 100
            except (InvalidOperation, ZeroDivisionError):
                context['minimum_rate'] = float(0)

            task_output = best_engine_output_task.result
            try:
                context['maximum_rate'] = (task_output['generated_interest'] / task_output['total_amount']) * 100
            except (InvalidOperation, ZeroDivisionError):
                context['maximum_rate'] = float(0)

            context['generated_interest'] = task_output['generated_interest'] / 12
            return render(request, 'concierge/landing/stage_one_async_result.html', context)
        else:
            data = {
                'worst_task_complete': context['worst_task_complete'],
                'best_task_complete': context['best_task_complete']
            }
            return JsonResponse(data)



def stage_two(request, uuid=None, context=None):
    if context is None:
        context = {}

    user = get_temporary_user(request, uuid)

    context['worst_engine_output_task_id'] = async_compare_existing_portfolio_to_generated.delay(email=user.email)
    context['best_engine_output_task_id'] = async_compare_existing_portfolio_to_generated.delay(email=user.email,
                                                                                                best_case=True)
    context['signup_form'] = ConciergeLandingContactForm()
    context['signup_form_helper'] = ConciergeLandingContactFormHelper()

    concierge_user_option, _ = ConciergeUserOption.objects.get_or_create(user=user)
    context['user_options_form'] = ConciergeUserOptionPublicForm(instance=concierge_user_option)

    if request.method == "POST":

        contact_form = ConciergeLandingContactForm(request.POST)
        if contact_form.is_valid():
            adviser_queue, _ = AdviserQueue.objects.get_or_create(email=contact_form.cleaned_data['email'])
            adviser_queue.telephone = contact_form.cleaned_data['telephone']
            adviser_queue.name = contact_form.cleaned_data['name']
            adviser_queue.source = 'Concierge Page'
            adviser_queue.save()

            AdviserQueue.add_to_queue(email=contact_form.cleaned_data['email'],
                                      first_name=contact_form.cleaned_data['name'],
                                      last_name='.',
                                      lead_source='Concierge Page',
                                      telephone_number=contact_form.cleaned_data['phone'])

        user_options_form = ConciergeUserOptionPublicForm(request.POST, instance=concierge_user_option)

        if user_options_form.is_valid():
            user_options = user_options_form.save(commit=False)
            user_options.user = user
            user_options.save()
            url = reverse('concierge_landing_stage_two', kwargs={'uuid': user.pk})
            return HttpResponseRedirect('%s#rate-indication' % url)
        else:
            context['user_options_form'] = user_options_form

    return render(request, 'concierge/landing/stage_two.html', context)


def stage_two_async(request, context=None):
    if context is None:
        context = {}
    if request.method == 'POST' and 'worst_engine_output_task_id' in request.POST and 'best_engine_output_task_id' in request.POST:
        worst_engine_output_task_id = request.POST.get('worst_engine_output_task_id')
        best_engine_output_task_id = request.POST.get('best_engine_output_task_id')
        worst_engine_output_task = AsyncResult(worst_engine_output_task_id)
        best_engine_output_task = AsyncResult(best_engine_output_task_id)
        context['worst_task_complete'] = worst_engine_output_task.ready()
        context['best_task_complete'] = best_engine_output_task.ready()
        if context['worst_task_complete'] and context['best_task_complete']:
            task_output = worst_engine_output_task.result
            try:
                context['minimum_rate'] = (task_output['generated_interest'] / task_output['total_amount']) * 100
            except (InvalidOperation, ZeroDivisionError):
                context['minimum_rate'] = float(0)

            task_output = best_engine_output_task.result
            try:
                context['maximum_rate'] = (task_output['generated_interest'] / task_output['total_amount']) * 100
            except (InvalidOperation, ZeroDivisionError):
                context['maximum_rate'] = float(0)
            context['generated_interest'] = task_output['generated_interest'] / 12
            context['signup_form'] = ConciergeLandingContactForm()
            context['signup_form_helper'] = ConciergeLandingContactFormHelper()
            return render(request, 'concierge/landing/stage_two_async_result.html', context)
        else:
            data = {
                'worst_task_complete': context['worst_task_complete'],
                'best_task_complete': context['best_task_complete']
            }
            return JsonResponse(data)

def numberline(request, minimum, maximum):

    minimum = Decimal(minimum).quantize(Decimal('.01'))
    maximum = Decimal(maximum).quantize(Decimal('.01'))

    minimum_100 = int(minimum * 100)
    maximum_100 = int(maximum * 100)

    line_maximum = 500

    if maximum_100 <= 0:
        maximum_100 = 0
    if minimum_100 <= 0:
        minimum_100 = 0

    if maximum_100 >= line_maximum:
        maximum_100 = line_maximum
    if minimum_100 >= line_maximum:
        minimum_100 = line_maximum

    if minimum_100 > maximum_100:
        minimum_100 = maximum_100

    offset = 40
    dimensions = (line_maximum + (2*offset), 200)
    bg_colour = (73, 75, 74, 255)  # Page background RGB Code
    fg_colour = (250, 250, 250, 255)  # Off-White
    max_colour = (51, 255, 139, 255)  # Bright Green
    min_colour = (255, 51, 51, 255)  # Bright Red

    image_font = truetype(font="LiberationSans-Regular.ttf", size=16, filename='resources/fonts/LiberationSans-Regular.ttf')

    image = new_image('RGBA', dimensions, bg_colour)
    number_line = Draw(image)

    number_line.line([(offset, 100), (line_maximum+offset, 100)], fg_colour, 3)  # number_line base
    number_line.line([(offset, 70), (offset, 130)], fg_colour, 3)  # minimum line
    number_line.line([(line_maximum+offset, 70), (line_maximum+offset, 130)], fg_colour, 3)  # maximum line

    number_line.line([(minimum_100+offset, 70), (minimum_100+offset, 130)], min_colour, 3)
    number_line.line([(maximum_100+offset, 70), (maximum_100+offset, 130)], max_colour, 3)

    number_line.text((offset-5, 50), '0%', font=image_font, fill=fg_colour)
    number_line.text((line_maximum+offset-5, 50), '{:g}%'.format(line_maximum / 100.0), font=image_font, fill=fg_colour)

    number_line.text((minimum_100+offset-10, 140), '{:.2f}%'.format(minimum), font=image_font, fill=min_colour)
    number_line.text((maximum_100+offset-10, 50), '{:.2f}%'.format(maximum), font=image_font, fill=max_colour)

    response = HttpResponse(content_type='image/png')
    image.save(response, 'PNG')
    return response


@never_cache
def business_index(request, uuid=None, context=None):
    if context is None:
        context = {}

    user = get_temporary_user(request, uuid)

    ConciergeUserPoolFormset = modelformset_factory(ConciergeUserPool, form=ConciergeUserPublicPoolForm,
                                                    widgets={'user': forms.HiddenInput}, can_delete=True, extra=0)
    context['formset_helper'] = ConciergeUserPoolFormHelper()
    context['personal_pools'] = ConciergeUserPoolFormset(queryset=ConciergeUserPool.objects.filter(user=user), prefix='personal')

    context['user'] = user
    if request.method == "POST":


        request_post = request.POST.copy()
        for field, value in request_post.iteritems():
            if 'user' in field:
                request_post[field] = user.pk

        updated_formset = ConciergeUserPoolFormset(request_post, prefix='personal')
        valid = updated_formset.is_valid()
        if valid:
            updated_formset.save()
            concierge_user_option, created = ConciergeUserOption.objects.get_or_create(user=user)
            concierge_user_option.charity = False
            concierge_user_option.business = True
            concierge_user_option.save()
            context['concierge_user_id'] = ConciergeUserOption.objects.get(user=user).pk
            url = reverse('concierge_business_landing_stage_one', kwargs={'uuid': user.pk})
            return HttpResponseRedirect('%s#rate-indication' % url)
        context['personal_pools'] = updated_formset
    return render(request, 'concierge/landing/business/index.html', context)


@never_cache
def business_stage_one(request, uuid=None, context=None):
    if context is None:
        context = {}

    user = get_temporary_user(request, uuid)

    context['worst_engine_output_task_id'] = async_compare_existing_portfolio_to_generated.delay(email=user.email)
    context['best_engine_output_task_id'] = async_compare_existing_portfolio_to_generated.delay(email=user.email,
                                                                                                best_case=True)
    context['signup_form'] = ConciergeLandingContactForm()
    context['signup_form_helper'] = ConciergeLandingContactFormHelper()

    concierge_user_option, _ = ConciergeUserOption.objects.get_or_create(user=user)
    context['user_options_form'] = ConciergeUserOptionPublicForm(instance=concierge_user_option,
                                                                 initial={'birth_date': datetime.now})

    if request.method == "POST":

        contact_form = ConciergeLandingContactForm(request.POST)
        if contact_form.is_valid():
            adviser_queue, _ = AdviserQueue.objects.get_or_create(email=contact_form.cleaned_data['email'])
            adviser_queue.telephone = contact_form.cleaned_data['telephone']
            adviser_queue.name = contact_form.cleaned_data['name']
            adviser_queue.source = 'Concierge Page'
            adviser_queue.save()
            AdviserQueue.add_to_queue(email=contact_form.cleaned_data['email'],
                                      first_name=contact_form.cleaned_data['name'],
                                      last_name='.',
                                      lead_source='Concierge Page',
                                      telephone_number=contact_form.cleaned_data['phone'])

        user_options_form = ConciergeUserOptionPublicForm(request.POST, instance=concierge_user_option)

        if user_options_form.is_valid():
            user_options = user_options_form.save(commit=False)
            user_options.user = user
            user_options.save()
            url = reverse('concierge_business_landing_stage_two', kwargs={'uuid': user.pk})
            return HttpResponseRedirect('%s#rate-indication' % url)
        else:
            context['user_options_form'] = user_options_form

    return render(request, 'concierge/landing/business/stage_one.html', context)

@never_cache
def business_stage_one_async(request, context=None):
    if context is None:
        context = {}
    if request.method == 'POST' and 'worst_engine_output_task_id' in request.POST and 'best_engine_output_task_id' in request.POST:
        worst_engine_output_task_id = request.POST.get('worst_engine_output_task_id')
        best_engine_output_task_id = request.POST.get('best_engine_output_task_id')
        worst_engine_output_task = AsyncResult(worst_engine_output_task_id)
        best_engine_output_task = AsyncResult(best_engine_output_task_id)
        context['worst_task_complete'] = worst_engine_output_task.ready()
        context['best_task_complete'] = best_engine_output_task.ready()
        if context['worst_task_complete'] and context['best_task_complete']:
            task_output = worst_engine_output_task.result
            try:
                context['minimum_rate'] = (task_output['generated_interest'] / task_output['expected_amount']) * 100
                context['minimum_generated_interest'] = task_output['generated_interest']
            except (InvalidOperation, ZeroDivisionError):
                context['minimum_rate'] = float(0)

            task_output = best_engine_output_task.result
            try:
                context['maximum_rate'] = (task_output['generated_interest'] / task_output['expected_amount']) * 100
                context['maximum_generated_interest'] = task_output['generated_interest']
            except (InvalidOperation, ZeroDivisionError):
                context['maximum_rate'] = float(0)

            context['generated_interest'] = task_output['generated_interest'] / 12
            return render(request, 'concierge/landing/business/stage_one_async_result.html', context)
        else:
            data = {
                'worst_task_complete': context['worst_task_complete'],
                'best_task_complete': context['best_task_complete']
            }
            return JsonResponse(data)


@never_cache
def business_stage_two(request, uuid=None, context=None):
    if context is None:
        context = {}

    user = get_temporary_user(request, uuid)

    context['worst_engine_output_task_id'] = async_compare_existing_portfolio_to_generated.delay(email=user.email)
    context['best_engine_output_task_id'] = async_compare_existing_portfolio_to_generated.delay(email=user.email,
                                                                                                best_case=True)
    context['signup_form'] = ConciergeLandingContactForm()
    context['signup_form_helper'] = ConciergeLandingContactFormHelper()

    concierge_user_option, _ = ConciergeUserOption.objects.get_or_create(user=user)
    context['user_options_form'] = ConciergeUserOptionPublicForm(instance=concierge_user_option)

    if request.method == "POST":

        contact_form = ConciergeLandingContactForm(request.POST)
        if contact_form.is_valid():
            adviser_queue, _ = AdviserQueue.objects.get_or_create(email=contact_form.cleaned_data['email'])
            adviser_queue.telephone = contact_form.cleaned_data['telephone']
            adviser_queue.name = contact_form.cleaned_data['name']
            adviser_queue.source = 'Concierge Page'
            adviser_queue.save()

            AdviserQueue.add_to_queue(email=contact_form.cleaned_data['email'],
                                      first_name=contact_form.cleaned_data['name'],
                                      last_name='.',
                                      lead_source='Concierge Page',
                                      telephone_number=contact_form.cleaned_data['phone'])

        user_options_form = ConciergeUserOptionPublicForm(request.POST, instance=concierge_user_option)

        if user_options_form.is_valid():
            user_options = user_options_form.save(commit=False)
            user_options.user = user
            user_options.save()
            url = reverse('concierge_business_landing_stage_two', kwargs={'uuid': user.pk})
            return HttpResponseRedirect('%s#rate-indication' % url)
        else:
            context['user_options_form'] = user_options_form

    return render(request, 'concierge/landing/business/stage_two.html', context)


@never_cache
def business_stage_two_async(request, context=None):
    if context is None:
        context = {}
    if request.method == 'POST' and 'worst_engine_output_task_id' in request.POST and 'best_engine_output_task_id' in request.POST:
        worst_engine_output_task_id = request.POST.get('worst_engine_output_task_id')
        best_engine_output_task_id = request.POST.get('best_engine_output_task_id')
        worst_engine_output_task = AsyncResult(worst_engine_output_task_id)
        best_engine_output_task = AsyncResult(best_engine_output_task_id)
        context['worst_task_complete'] = worst_engine_output_task.ready()
        context['best_task_complete'] = best_engine_output_task.ready()
        if context['worst_task_complete'] and context['best_task_complete']:
            task_output = worst_engine_output_task.result
            try:
                context['minimum_rate'] = (task_output['generated_interest'] / task_output['total_amount']) * 100
            except (InvalidOperation, ZeroDivisionError):
                context['minimum_rate'] = float(0)

            task_output = best_engine_output_task.result
            try:
                context['maximum_rate'] = (task_output['generated_interest'] / task_output['total_amount']) * 100
            except (InvalidOperation, ZeroDivisionError):
                context['maximum_rate'] = float(0)
            context['generated_interest'] = task_output['generated_interest'] / 12
            context['signup_form'] = ConciergeLandingContactForm()
            context['signup_form_helper'] = ConciergeLandingContactFormHelper()
            return render(request, 'concierge/landing/business/stage_two_async_result.html', context)
        else:
            data = {
                'worst_task_complete': context['worst_task_complete'],
                'best_task_complete': context['best_task_complete']
            }
            return JsonResponse(data)


def personal_index(request, uuid=None, context=None):
    if context is None:
        context = {}

    user = get_temporary_user(request, uuid)

    ConciergeUserPoolFormset = modelformset_factory(ConciergeUserPool, form=ConciergeUserPublicPoolForm,
                                                    widgets={'user': forms.HiddenInput}, can_delete=True, extra=0)
    context['formset_helper'] = ConciergeUserPoolForm()
    context['personal_pools'] = ConciergeUserPoolFormset(queryset=ConciergeUserPool.objects.filter(user=user),
                                                         prefix='personal')
    context['signup_form'] = ConciergeLandingContactForm()
    context['signup_form_helper'] = ConciergeLandingContactFormHelper()
    context['form'] = IndexSignupform()

    context['user'] = user
    if request.method == "POST":

        contact_form = ConciergeLandingContactForm(request.POST)
        if contact_form.is_valid():
            adviser_queue, _ = AdviserQueue.objects.get_or_create(email=contact_form.cleaned_data['email'])
            adviser_queue.telephone = contact_form.cleaned_data['phone']
            adviser_queue.name = contact_form.cleaned_data['name']
            adviser_queue.source = 'Concierge Page'
            adviser_queue.save()
            AdviserQueue.add_to_queue(email=contact_form.cleaned_data['email'],
                                      first_name=contact_form.cleaned_data['name'],
                                      last_name='.',
                                      lead_source='Concierge Page',
                                      telephone_number=contact_form.cleaned_data['phone'])
            messages.success(request, 'Your enquiry has been sent to our advisers.')

        request_post = request.POST.copy()
        for field, value in request_post.iteritems():
            if 'user' in field:
                request_post[field] = user.pk

        updated_formset = ConciergeUserPoolFormset(request_post, prefix='personal')
        valid = updated_formset.is_valid()
        if valid:
            updated_formset.save()
            updated_formset = ConciergeUserPoolFormset(queryset=ConciergeUserPool.objects.filter(
                user=user), prefix='personal')
            concierge_user_option, created = ConciergeUserOption.objects.get_or_create(user=user)
            concierge_user_option.charity = False
            concierge_user_option.business = False
            concierge_user_option.save()

        context['personal_pools'] = updated_formset
        context['concierge_user_id'] = ConciergeUserOption.objects.get(user=user).pk
        url = reverse('concierge_personal_landing_stage_one', kwargs={'uuid': user.pk})
        if valid:
            return HttpResponseRedirect('%s#rate-indication' % url)
    return render(request, 'concierge/landing/personal/index.html', context)


@never_cache
def personal_stage_one(request, uuid=None, context=None):
    if context is None:
        context = {}

    user = get_temporary_user(request, uuid)

    context['worst_engine_output_task_id'] = async_compare_existing_portfolio_to_generated.delay(email=user.email)
    context['best_engine_output_task_id'] = async_compare_existing_portfolio_to_generated.delay(email=user.email,
                                                                                                best_case=True)
    context['signup_form'] = ConciergeLandingContactForm()
    context['signup_form_helper'] = ConciergeLandingContactFormHelper()

    concierge_user_option, _ = ConciergeUserOption.objects.get_or_create(user=user)
    context['user_options_form'] = ConciergeUserOptionPublicForm(instance=concierge_user_option,
                                                                 initial={'birth_date': datetime.now})

    if request.method == "POST":

        contact_form = ConciergeLandingContactForm(request.POST)
        if contact_form.is_valid():
            adviser_queue, _ = AdviserQueue.objects.get_or_create(email=contact_form.cleaned_data['email'])
            adviser_queue.telephone = contact_form.cleaned_data['telephone']
            adviser_queue.name = contact_form.cleaned_data['name']
            adviser_queue.source = 'Concierge Page'
            adviser_queue.save()
            AdviserQueue.add_to_queue(email=contact_form.cleaned_data['email'],
                                      first_name=contact_form.cleaned_data['name'],
                                      last_name='.',
                                      lead_source='Concierge Page',
                                      telephone_number=contact_form.cleaned_data['phone'])

        user_options_form = ConciergeUserOptionPublicForm(request.POST, instance=concierge_user_option)

        if user_options_form.is_valid():
            user_options = user_options_form.save(commit=False)
            user_options.user = user
            user_options.save()
            url = reverse('concierge_personal_landing_stage_two', kwargs={'uuid': user.pk})
            return HttpResponseRedirect('%s#rate-indication' % url)
        else:
            context['user_options_form'] = user_options_form

    return render(request, 'concierge/landing/personal/stage_one.html', context)


@never_cache
def personal_stage_one_async(request, context=None):
    if context is None:
        context = {}
    if request.method == 'POST' and 'worst_engine_output_task_id' in request.POST and 'best_engine_output_task_id' in request.POST:
        worst_engine_output_task_id = request.POST.get('worst_engine_output_task_id')
        best_engine_output_task_id = request.POST.get('best_engine_output_task_id')
        worst_engine_output_task = AsyncResult(worst_engine_output_task_id)
        best_engine_output_task = AsyncResult(best_engine_output_task_id)
        context['worst_task_complete'] = worst_engine_output_task.ready()
        context['best_task_complete'] = best_engine_output_task.ready()
        if context['worst_task_complete'] and context['best_task_complete']:
            task_output = worst_engine_output_task.result
            try:
                context['minimum_rate'] = (task_output['generated_interest'] / task_output['total_amount']) * 100
                context['minimum_generated_interest'] = task_output['generated_interest']
            except (InvalidOperation, ZeroDivisionError):
                context['minimum_rate'] = float(0)

            task_output = best_engine_output_task.result
            try:
                context['maximum_rate'] = (task_output['generated_interest'] / task_output['total_amount']) * 100
                context['maximum_generated_interest'] = task_output['generated_interest']
            except (InvalidOperation, ZeroDivisionError):
                context['maximum_rate'] = float(0)

            context['generated_interest'] = task_output['generated_interest'] / 12
            return render(request, 'concierge/landing/personal/stage_one_async_result.html', context)
        else:
            data = {
                'worst_task_complete': context['worst_task_complete'],
                'best_task_complete': context['best_task_complete']
            }
            return JsonResponse(data)


def personal_stage_two(request, uuid=None, context=None):
    if context is None:
        context = {}

    user = get_temporary_user(request, uuid)

    context['worst_engine_output_task_id'] = async_compare_existing_portfolio_to_generated.delay(email=user.email)
    context['best_engine_output_task_id'] = async_compare_existing_portfolio_to_generated.delay(email=user.email,
                                                                                                best_case=True)
    context['signup_form'] = ConciergeLandingContactForm()
    context['signup_form_helper'] = ConciergeLandingContactFormHelper()

    concierge_user_option, _ = ConciergeUserOption.objects.get_or_create(user=user)
    context['user_options_form'] = ConciergeUserOptionPublicForm(instance=concierge_user_option)

    if request.method == "POST":

        contact_form = ConciergeLandingContactForm(request.POST)
        if contact_form.is_valid():
            adviser_queue, _ = AdviserQueue.objects.get_or_create(email=contact_form.cleaned_data['email'])
            adviser_queue.telephone = contact_form.cleaned_data['telephone']
            adviser_queue.name = contact_form.cleaned_data['name']
            adviser_queue.source = 'Concierge Page'
            adviser_queue.save()

            AdviserQueue.add_to_queue(email=contact_form.cleaned_data['email'],
                                      first_name=contact_form.cleaned_data['name'],
                                      last_name='.',
                                      lead_source='Concierge Page',
                                      telephone_number=contact_form.cleaned_data['phone'])

        user_options_form = ConciergeUserOptionPublicForm(request.POST, instance=concierge_user_option)

        if user_options_form.is_valid():
            user_options = user_options_form.save(commit=False)
            user_options.user = user
            user_options.save()
            url = reverse('concierge_personal_landing_stage_two', kwargs={'uuid': user.pk})
            return HttpResponseRedirect('%s#rate-indication' % url)
        else:
            context['user_options_form'] = user_options_form

    return render(request, 'concierge/landing/personal/stage_two.html', context)


@never_cache
def personal_stage_two_async(request, context=None):
    if context is None:
        context = {}
    if request.method == 'POST' and 'worst_engine_output_task_id' in request.POST and 'best_engine_output_task_id' in request.POST:
        worst_engine_output_task_id = request.POST.get('worst_engine_output_task_id')
        best_engine_output_task_id = request.POST.get('best_engine_output_task_id')
        worst_engine_output_task = AsyncResult(worst_engine_output_task_id)
        best_engine_output_task = AsyncResult(best_engine_output_task_id)
        context['worst_task_complete'] = worst_engine_output_task.ready()
        context['best_task_complete'] = best_engine_output_task.ready()
        if context['worst_task_complete'] and context['best_task_complete']:
            task_output = worst_engine_output_task.result
            try:
                context['minimum_rate'] = (task_output['generated_interest'] / task_output['total_amount']) * 100
            except (InvalidOperation, ZeroDivisionError):
                context['minimum_rate'] = float(0)

            task_output = best_engine_output_task.result
            try:
                context['maximum_rate'] = (task_output['generated_interest'] / task_output['total_amount']) * 100
            except (InvalidOperation, ZeroDivisionError):
                context['maximum_rate'] = float(0)
            context['generated_interest'] = task_output['generated_interest'] / 12
            context['signup_form'] = ConciergeLandingContactForm()
            context['signup_form_helper'] = ConciergeLandingContactFormHelper()
            return render(request, 'concierge/landing/personal/stage_two_async_result.html', context)
        else:
            data = {
                'worst_task_complete': context['worst_task_complete'],
                'best_task_complete': context['best_task_complete']
            }
            return JsonResponse(data)


@never_cache
def full_tool_index(request, uuid=None, context=None):
    if context is None:
        context = {}

    user = get_temporary_user(request, uuid)

    ConciergeUserPoolFormset = modelformset_factory(ConciergeUserPool, form=ConciergeUserPublicPoolForm,
                                                    widgets={'user': forms.HiddenInput}, can_delete=True, extra=0)
    context['formset_helper'] = ConciergeUserPoolFormHelper()
    context['personal_pools'] = ConciergeUserPoolFormset(queryset=ConciergeUserPool.objects.filter(user=user),
                                                         prefix='personal')

    context['account_type'] = ConciergeUserPoolType()

    context['user'] = user
    if request.method == "POST":

        request_post = request.POST.copy()
        for field, value in request_post.iteritems():
            if 'user' in field:
                request_post[field] = user.pk

        updated_formset = ConciergeUserPoolFormset(request_post, prefix='personal')
        account_type = ConciergeUserPoolType(request.POST)
        valid = updated_formset.is_valid() and account_type.is_valid()
        if valid:
            updated_formset.save()
            account_type_string = account_type.cleaned_data['account_type']
            concierge_user_option, created = ConciergeUserOption.objects.get_or_create(user=user)
            concierge_user_option.birth_date = concierge_user_option.birth_date if concierge_user_option.birth_date is not None else datetime(year=1900, month=1, day=1)
            concierge_user_option.personal = (account_type_string == 'personal')
            concierge_user_option.charity = (account_type_string == 'charity')
            concierge_user_option.business = (account_type_string == 'business')
            concierge_user_option.save()
            url = reverse('concierge_full_tool_landing_stage_one', kwargs={'uuid': user.pk})
            return HttpResponseRedirect('%s#rate-indication' % url)
        context['personal_pools'] = updated_formset
        context['account_type'] = account_type
    return render(request, 'concierge/landing/full_tool/index.html', context)


@never_cache
def full_tool_stage_one(request, uuid=None, context=None):
    if context is None:
        context = {}

    user = get_temporary_user(request, uuid)

    context['worst_engine_output_task_id'] = async_compare_existing_portfolio_to_generated.delay(email=user.email)
    context['best_engine_output_task_id'] = async_compare_existing_portfolio_to_generated.delay(email=user.email,
                                                                                                best_case=True)
    context['signup_form'] = ConciergeLandingContactForm()
    context['signup_form_helper'] = ConciergeLandingContactFormHelper()

    concierge_user_option, _ = ConciergeUserOption.objects.get_or_create(user=user)
    context['user_options_form'] = ConciergeUserOptionPublicForm(instance=concierge_user_option,
                                                                 initial={'birth_date': datetime.now})

    if request.method == "POST":

        contact_form = ConciergeLandingContactForm(request.POST)
        user_options_form = ConciergeUserOptionPublicForm(request.POST, instance=concierge_user_option)

        if contact_form.is_valid() and user_options_form.is_valid():
            adviser_queue, _ = AdviserQueue.objects.get_or_create(email=contact_form.cleaned_data['email'])
            adviser_queue.telephone = contact_form.cleaned_data['phone']
            adviser_queue.name = contact_form.cleaned_data['name']
            adviser_queue.source = 'Concierge Page'
            adviser_queue.save()
            user.first_name = contact_form.cleaned_data['name']
            user.save()
            user.profile.savings_calculator_email = contact_form.cleaned_data['email']
            user.profile.telephone = contact_form.cleaned_data['phone']
            user.profile.save()
            AdviserQueue.add_to_queue(email=contact_form.cleaned_data['email'],
                                      first_name=contact_form.cleaned_data['name'],
                                      last_name='.',
                                      lead_source='Concierge Page',
                                      telephone_number=contact_form.cleaned_data['phone'])
            AdviserQueue.add_note_to_cmt(email=contact_form.cleaned_data['email'],
                                         note=u'User concierge tool portfolio is availible at: https://savingschampion.co.uk{url}'.format(
                                             url=reverse('engine_index',
                                                         kwargs={
                                                             'email': contact_form.cleaned_data['email']
                                                         })
                                         ))
            user_options = user_options_form.save(commit=False)
            user_options.user = user
            user_options.save()
            url = reverse('concierge_full_tool_landing_stage_two', kwargs={'uuid': user.pk})
            return HttpResponseRedirect('%s#rate-indication' % url)
        else:
            context['signup_form'] = contact_form
            context['user_options_form'] = user_options_form
    return render(request, 'concierge/landing/full_tool/stage_one.html', context)


@never_cache
def full_tool_stage_one_async(request, context=None):
    if context is None:
        context = {}
    if request.method == 'POST' and 'worst_engine_output_task_id' in request.POST and 'best_engine_output_task_id' in request.POST:
        worst_engine_output_task_id = request.POST.get('worst_engine_output_task_id')
        best_engine_output_task_id = request.POST.get('best_engine_output_task_id')
        worst_engine_output_task = AsyncResult(worst_engine_output_task_id)
        best_engine_output_task = AsyncResult(best_engine_output_task_id)
        context['worst_task_complete'] = worst_engine_output_task.ready()
        context['best_task_complete'] = best_engine_output_task.ready()
        if context['worst_task_complete'] and context['best_task_complete']:
            task_output = worst_engine_output_task.result
            try:
                context['minimum_rate'] = (task_output['generated_interest'] / task_output['expected_amount']) * 100
                context['minimum_generated_interest'] = task_output['generated_interest']
            except (InvalidOperation, ZeroDivisionError):
                context['minimum_rate'] = float(0)

            task_output = best_engine_output_task.result
            try:
                context['maximum_rate'] = (task_output['generated_interest'] / task_output['expected_amount']) * 100
                context['maximum_generated_interest'] = task_output['generated_interest']
            except (InvalidOperation, ZeroDivisionError):
                context['maximum_rate'] = float(0)

            context['generated_interest'] = task_output['generated_interest'] / 12

            user = get_temporary_user(request)
            concierge_user_option, _ = ConciergeUserOption.objects.get_or_create(user=user)
            context['user_options_form'] = ConciergeUserOptionPublicForm(instance=concierge_user_option,
                                                                         initial={'birth_date': concierge_user_option.birth_date.strftime('%Y-%m-%d')})
            context['signup_form'] = ConciergeLandingContactForm()
            context['user'] = user
            return render(request, 'concierge/landing/full_tool/stage_one_async_result.html', context)
        else:
            data = {
                'worst_task_complete': context['worst_task_complete'],
                'best_task_complete': context['best_task_complete']
            }
            return JsonResponse(data)


@never_cache
def full_tool_stage_two(request, uuid=None, context=None):
    if context is None:
        context = {}

    user = get_temporary_user(request, uuid)

    context['worst_engine_output_task_id'] = async_compare_existing_portfolio_to_generated.delay(email=user.email)
    context['best_engine_output_task_id'] = async_compare_existing_portfolio_to_generated.delay(email=user.email,
                                                                                                best_case=True)
    context['signup_form'] = ConciergeLandingContactForm(initial={
        'phone': user.profile.telephone,
        'name': user.first_name,
        'email': user.profile.savings_calculator_email
    })
    context['signup_form_helper'] = ConciergeLandingContactFormHelper()

    concierge_user_option, _ = ConciergeUserOption.objects.get_or_create(user=user)
    context['user_options_form'] = ConciergeUserOptionPublicForm(instance=concierge_user_option)

    if request.method == "POST":

        contact_form = ConciergeLandingContactForm(request.POST)
        concierge_user_option, _ = ConciergeUserOption.objects.get_or_create(user=user)
        user_options_form = ConciergeUserOptionPublicForm(request.POST, instance=concierge_user_option)

        if user_options_form.is_valid() and contact_form.is_valid():
            user_options = user_options_form.save(commit=False)
            user_options.user = user
            user_options.save()
            telephone = user.profile.telephone
            name = user.first_name
            email = user.profile.savings_calculator_email
            AdviserQueue.add_to_queue(email=email,
                                      first_name=name,
                                      last_name='.',
                                      lead_source='Concierge Page',
                                      telephone_number=telephone)
            deactivate_old_temporary_user(user.email)
            messages.success(request, 'Thank you for your enquiry, an adviser will be in touch as soon as possible. '
                                      'Below are other things we can assist you with.')
            url = reverse('home')
            return HttpResponseRedirect('%s' % url)
        else:
            context['user_options_form'] = user_options_form

    return render(request, 'concierge/landing/full_tool/stage_two.html', context)


def full_tool_stage_two_thank_you(request, uuid=None, context=None):
    return render(request, 'concierge/landing/full_tool/stage_two_thank_you.html', context)

@never_cache
def full_tool_stage_two_async(request, context=None):
    if context is None:
        context = {}
    if request.method == 'POST' and 'worst_engine_output_task_id' in request.POST and 'best_engine_output_task_id' in request.POST:
        worst_engine_output_task_id = request.POST.get('worst_engine_output_task_id')
        best_engine_output_task_id = request.POST.get('best_engine_output_task_id')
        worst_engine_output_task = AsyncResult(worst_engine_output_task_id)
        best_engine_output_task = AsyncResult(best_engine_output_task_id)
        context['worst_task_complete'] = worst_engine_output_task.ready()
        context['best_task_complete'] = best_engine_output_task.ready()
        if context['worst_task_complete'] and context['best_task_complete']:
            task_output = worst_engine_output_task.result
            try:
                context['minimum_rate'] = (task_output['generated_interest'] / task_output['total_amount']) * 100
            except (InvalidOperation, ZeroDivisionError):
                context['minimum_rate'] = float(0)

            task_output = best_engine_output_task.result
            try:
                context['maximum_rate'] = (task_output['generated_interest'] / task_output['total_amount']) * 100
            except (InvalidOperation, ZeroDivisionError):
                context['maximum_rate'] = float(0)
            context['generated_interest'] = task_output['generated_interest'] / 12

            user = get_temporary_user(request)
            context['signup_form'] = ConciergeLandingContactForm(initial={
                'phone': user.profile.telephone,
                'name': user.first_name,
                'email': user.profile.savings_calculator_email
            })
            context['signup_form_helper'] = ConciergeLandingContactFormHelper()
            context['user'] = user
            return render(request, 'concierge/landing/full_tool/stage_two_async_result.html', context)
        else:
            data = {
                'worst_task_complete': context['worst_task_complete'],
                'best_task_complete': context['best_task_complete']
            }
            return JsonResponse(data)


def this_is_money_concierge_widget(request, context=None):
    if context is None:
        context = {}
    user = get_temporary_user(request)
    concierge_form = ThisIsMoneyConciergeWidgetPoolForm(initial={
        'user': user
    })
    if request.method == 'POST':
        concierge_form = ThisIsMoneyConciergeWidgetPoolForm(request.POST)
        pools = ConciergeUserPool.objects.filter(user=user)
        pools.delete()
        if concierge_form.is_valid():
            ConciergeUserPool.objects.get_or_create(user=user,
                                                    balance=concierge_form.cleaned_data['balance'],
                                                    term=concierge_form.cleaned_data['term']
                                                    )
            if concierge_form.cleaned_data['balance'] > 50000000:
                context['results'] = {
                    'generated_interest': 0,
                    'over_limit': True
                }
            else:
                context['results'] = async_compare_existing_portfolio_to_generated(user.email, best_case=True)
            return render(request, 'concierge/landing/this_is_money/widget_done.html', context)
    context['concierge_form'] = concierge_form
    return render(request, 'concierge/landing/this_is_money/widget.html', context)

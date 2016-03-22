from decimal import InvalidOperation
import urllib
from django import forms
from django.contrib.auth import get_user_model
from django.forms.models import modelformset_factory
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.cache import never_cache
from common.accounts.utils import create_stage_one_profile
from concierge.engine import compare_existing_portfolio_to_generated
from concierge.forms import ConciergeUserForm, ConciergeUserOptionForm, \
    ConciergeUserRequiredProductForm, ConciergeUserAddExistingProductForm, \
    ConciergeUserPrivatePoolForm
from concierge.models import ConciergeUserPool, ConciergeUserRequiredProduct, ConciergeUserRemovedProduct, \
    ConciergeUserOption, ConciergeUserAcceptedProduct
from products.models import ProductPortfolio, MasterProduct, Provider, Product, RatetrackerReminder


def engine_index(request, email=None, context=None):
    if context is None:
        context = {}
    if 'form' not in context:
        context['form'] = ConciergeUserForm(initial={'email': email})

    context['email'] = email

    return render(request, 'concierge/engine/index.html', context)


def load_user(concierge_user, context):
    context['concierge_user_id'] = concierge_user.pk
    context['user_options_form'] = ConciergeUserOptionForm(instance=concierge_user)
    ConciergeUserPoolFormset = modelformset_factory(ConciergeUserPool, form=ConciergeUserPrivatePoolForm,
                                                    widgets={'user': forms.HiddenInput},
                                                    can_delete=True,
                                                    extra=0)
    context['pools'] = ConciergeUserPoolFormset(
        queryset=ConciergeUserPool.objects.filter(user=concierge_user.user))
    context['required_accounts'] = ConciergeUserRequiredProduct.objects.filter(concierge_user=concierge_user)
    context['removed_products'] = ConciergeUserRemovedProduct.objects.filter(concierge_user=concierge_user)
    context['require_product_form'] = ConciergeUserRequiredProductForm(initial={'concierge_user': concierge_user})
    ratetracker_reminders = RatetrackerReminder.objects.filter(user=concierge_user.user, is_deleted=False)
    context['current_fixed_term_accounts'] = ratetracker_reminders
    context['current_accounts'] = ProductPortfolio.objects.filter(user=concierge_user.user, is_deleted=False)
    context['add_existing_product_form'] = ConciergeUserAddExistingProductForm(initial={'user': concierge_user.user})
    context['allowed_accounts'] = ConciergeUserAcceptedProduct.objects.filter(concierge_user=concierge_user)

    return context

@never_cache
def engine_load_user(request, email=None, context=None):
    if context is None:
        context = {}
    if request.method == "POST":
        form = ConciergeUserForm(request.POST)
        if form.is_valid():
            User = get_user_model()
            try:
                user = User.objects.get(email=form.cleaned_data['email'])
            except User.DoesNotExist:
                user, _, record_stats = create_stage_one_profile(request, email=form.cleaned_data['email'], source='CMT Dashboard',
                                                   send_activation=False, login_user=False)
            concierge_user, created = ConciergeUserOption.objects.get_or_create(user=user)
            context = load_user(concierge_user, context)
        else:
            context['form'] = form
            return render(request, 'concierge/engine/index_no_wrapper.html', context)
    elif email is not None:
        concierge_user, created = ConciergeUserOption.objects.get_or_create(user__email=email)
        context = load_user(concierge_user, context)

    else:
        context['form'] = ConciergeUserForm()
        return render(request, 'concierge/engine/index_no_wrapper.html', context)

    return render(request, 'concierge/engine/user_management.html', context)


def engine_update_user(request, concierge_user_id, context=None):
    if context is None:
        context = {}
    if request.method == "POST":
        concierge_user = ConciergeUserOption.objects.get(pk=concierge_user_id)
        form = ConciergeUserOptionForm(request.POST, instance=concierge_user)
        context['user_options_form'] = form
        if form.is_valid():
            form.save()
    return render(request, 'concierge/engine/user_options.html', context)


def engine_create_pool(request, concierge_user_id, context=None):
    if context is None:
        context = {}
    concierge_user = ConciergeUserOption.objects.get(pk=concierge_user_id)
    if request.method == "POST":
        new_pool = ConciergeUserPool(user=concierge_user.user)
        new_pool.save()
    ConciergeUserPoolFormset = modelformset_factory(ConciergeUserPool, form=ConciergeUserPrivatePoolForm,
                                                    widgets={'user': forms.HiddenInput},
                                                    can_delete=True,
                                                    extra=0)
    context['pools'] = ConciergeUserPoolFormset(queryset=ConciergeUserPool.objects.filter(user=concierge_user.user))
    context['concierge_user_id'] = concierge_user_id
    return render(request, 'concierge/engine/user_pools.html', context)

@never_cache
def engine_get_pool(request, concierge_user_id, context=None):
    if context is None:
        context = {}
    concierge_user = ConciergeUserOption.objects.get(pk=concierge_user_id)
    ConciergeUserPoolFormset = modelformset_factory(ConciergeUserPool, form=ConciergeUserPrivatePoolForm,
                                                    widgets={'user': forms.HiddenInput},
                                                    can_delete=True,
                                                    extra=0)
    context['pools'] = ConciergeUserPoolFormset(queryset=ConciergeUserPool.objects.filter(user=concierge_user.user))
    context['concierge_user_id'] = concierge_user_id
    return render(request, 'concierge/engine/user_pools.html', context)


def engine_update_pool(request, user=None, context=None):
    if context is None:
        context = {}
    ConciergeUserPoolFormset = modelformset_factory(ConciergeUserPool, form=ConciergeUserPrivatePoolForm, widgets={'user': forms.HiddenInput},
                                                    can_delete=True, extra=0)
    if request.method == "POST":
        updated_formset = ConciergeUserPoolFormset(request.POST)
        if updated_formset.is_valid():
            for form in updated_formset:
                user = form.cleaned_data['user']
                break
            else:
                # No forms in formset!
                raise AssertionError('updated_formset must contain at least one form')
            updated_formset.save()
            updated_formset = ConciergeUserPoolFormset(queryset=ConciergeUserPool.objects.filter(
                user=user))
        context['pools'] = updated_formset
        try:
            concierge_user_id = ConciergeUserOption.objects.get_or_create(user=user)
            context['concierge_user_id'] = concierge_user_id[0].pk
        except (UnboundLocalError, ValueError):
            pass

        return render(request, 'concierge/engine/user_pools.html', context)


def engine_process_user(request, concierge_user_id, best_case=False, context=None):
    if context is None:
        context = {}
    context['concierge_user_id'] = concierge_user_id
    if request.method == 'POST':
        concierge_user = ConciergeUserOption.objects.get(pk=concierge_user_id)
        required_accounts = ConciergeUserRequiredProduct.objects.filter(concierge_user=concierge_user).values_list(
            'master_product_id', 'balance')
        removed_accounts = ConciergeUserRemovedProduct.objects.filter(concierge_user=concierge_user).values_list(
            'master_product_id', flat=True)
        engine_output = compare_existing_portfolio_to_generated(
            concierge_user.user.email,
            required_accounts=required_accounts,
            removed_accounts=removed_accounts,
            best_case=best_case)
        context['suggestions'] = engine_output['generated_portfolio']
        context['engine_log'] = engine_output['engine_log']
        context['naughty_list'] = engine_output['naughty_list']
        context['total_amount'] = engine_output['total_amount']
        context['total_interest'] = engine_output['generated_interest']
        try:
            context['total_rate'] = ((engine_output['generated_interest'] / engine_output['total_amount']) * 100)
        except InvalidOperation:
            context['total_rate'] = 0
        context['existing_amount'] = engine_output['existing_amount']
        context['existing_interest'] = engine_output['existing_interest']
        try:
            context['existing_rate'] = ((engine_output['existing_interest'] / engine_output['existing_amount']) * 100)
        except InvalidOperation:
            context['existing_rate'] = 0
        context['difference_rate'] = context['total_rate'] - context['existing_rate']
        context['difference_interest'] = context['total_interest'] - context['existing_interest']

    return render(request, 'concierge/engine/suggestions.html', context)


def engine_get_removed_products(request, context=None):
    if context is None:
        context = {}
    if request.method == 'GET' and 'concierge_user' in request.GET:
        concierge_user_id = request.GET['concierge_user']
        concierge_user = ConciergeUserOption.objects.get(pk=concierge_user_id)
        context['removed_products'] = ConciergeUserRemovedProduct.objects.filter(concierge_user=concierge_user)
        context['concierge_user_id'] = concierge_user_id
        return render(request, 'concierge/engine/removed.html', context)
    return HttpResponse(status=500)


def engine_remove_product(request, context=None):
    if context is None:
        context = {}
    if request.method == 'POST' and 'concierge_user' in request.POST and 'master_product' in request.POST:
        concierge_user_id = request.POST['concierge_user']
        master_product_id = request.POST['master_product']
        concierge_user = ConciergeUserOption.objects.get(pk=concierge_user_id)
        master_product = MasterProduct.objects.get(pk=master_product_id)
        ConciergeUserRemovedProduct.objects.get_or_create(concierge_user=concierge_user, master_product=master_product)
        ConciergeUserRequiredProduct.objects.filter(concierge_user=concierge_user,
                                                    master_product=master_product).delete()
        context['removed_products'] = ConciergeUserRemovedProduct.objects.filter(concierge_user=concierge_user)
        context['concierge_user_id'] = concierge_user_id
        return render(request, 'concierge/engine/removed.html', context)
    return HttpResponse(status=500)


def engine_restore_product(request, context=None):
    if context is None:
        context = {}
    if request.method == 'POST' and 'concierge_user' in request.POST and 'removed_product' in request.POST:
        concierge_user_id = request.POST['concierge_user']
        removed_product_id = request.POST['removed_product']
        concierge_user = ConciergeUserOption.objects.get(pk=concierge_user_id)
        removed_product = ConciergeUserRemovedProduct.objects.filter(pk=removed_product_id)
        removed_product.delete()
        context['removed_products'] = ConciergeUserRemovedProduct.objects.filter(concierge_user=concierge_user)
        context['concierge_user_id'] = concierge_user_id
        return render(request, 'concierge/engine/removed.html', context)
    return HttpResponse(status=500)


def engine_get_master_products_from_provider(request):
    if request.method == 'GET' and 'provider' in request.GET:
        provider_id = request.GET['provider']
        provider = Provider.objects.get(pk=provider_id)
        products = list(MasterProduct.objects.filter(provider=provider).values_list('pk', 'title'))
        return JsonResponse(products, safe=False)
    return HttpResponse(status=500)


def engine_get_required_products(request, context=None):
    if context is None:
        context = {}
    if request.method == 'GET' and 'concierge_user' in request.GET:
        concierge_user_id = request.GET['concierge_user']
        concierge_user = ConciergeUserOption.objects.get(pk=concierge_user_id)
        context['concierge_user_id'] = concierge_user_id
        context['required_accounts'] = ConciergeUserRequiredProduct.objects.filter(concierge_user_id=concierge_user_id)
        context['require_product_form'] = ConciergeUserRequiredProductForm(initial={'concierge_user': concierge_user})
        return render(request, 'concierge/engine/required.html', context)
    return HttpResponse(status=500)


def engine_require_product(request, context=None):
    if context is None:
        context = {}
    if request.method == 'POST' and 'concierge_user' in request.POST and 'master_product' in request.POST and 'balance' in request.POST:
        concierge_user_id = request.POST['concierge_user']
        master_product_id = request.POST['master_product']
        balance = request.POST['balance']
        concierge_user = ConciergeUserOption.objects.get(pk=concierge_user_id)
        master_product = MasterProduct.objects.get(pk=master_product_id)
        required_product = ConciergeUserRequiredProduct(concierge_user=concierge_user,
                                                        master_product=master_product)
        required_product.balance = balance
        required_product.save()
        context['concierge_user_id'] = concierge_user_id
        context['required_accounts'] = ConciergeUserRequiredProduct.objects.filter(concierge_user_id=concierge_user_id)
        context['require_product_form'] = ConciergeUserRequiredProductForm(initial={'concierge_user': concierge_user})
        return render(request, 'concierge/engine/required.html', context)
    elif request.method == 'POST':
        form = ConciergeUserRequiredProductForm(request.POST)
        if form.is_valid():
            saved_form = form.cleaned_data
            master_product = MasterProduct.objects.get(pk=saved_form['products'])
            ConciergeUserRequiredProduct(
                master_product=master_product,
                concierge_user=saved_form['concierge_user'],
                balance=saved_form['balance']).save()
            concierge_user = saved_form['concierge_user']
            concierge_user_id = concierge_user.pk
            context['concierge_user_id'] = concierge_user_id
            context['required_accounts'] = ConciergeUserRequiredProduct.objects.filter(
                concierge_user_id=concierge_user_id)
            context['require_product_form'] = ConciergeUserRequiredProductForm(
                initial={'concierge_user': concierge_user})
            return render(request, 'concierge/engine/required.html', context)
    return HttpResponse(status=500)


def engine_removed_required_product(request, context=None):
    if context is None:
        context = {}
    if request.method == "POST" and 'product' in request.POST:
        concierge_user_id = request.POST['concierge_user']
        if ConciergeUserRequiredProduct.objects.filter(pk=request.POST['product'],
                                                       concierge_user_id=concierge_user_id).exists():
            ConciergeUserRequiredProduct.objects.filter(pk=request.POST['product'],
                                                        concierge_user_id=concierge_user_id).delete()
            context['required_accounts'] = ConciergeUserRequiredProduct.objects.filter(
                concierge_user_id=concierge_user_id)

            context['concierge_user_id'] = concierge_user_id
            concierge_user = ConciergeUserOption.objects.get(pk=concierge_user_id)
            context['require_product_form'] = ConciergeUserRequiredProductForm(
                initial={'concierge_user': concierge_user})
            return render(request, 'concierge/engine/required.html', context)
    return HttpResponse(status=500)

# Todo:
def engine_get_allowed_products(request, context=None):
    if context is None:
        context = {}
    if request.method == 'GET' and 'concierge_user' in request.GET:
        concierge_user_id = request.GET['concierge_user']
        concierge_user = ConciergeUserOption.objects.get(pk=concierge_user_id)
        context['concierge_user_id'] = concierge_user_id
        context['allowed_accounts'] = ConciergeUserAcceptedProduct.objects.filter(concierge_user=concierge_user)
        return render(request, 'concierge/engine/allowed.html', context)
    return HttpResponse(status=500)


def engine_allow_product(request, context=None):
    if context is None:
        context = {}
    if request.method == 'POST' and 'concierge_user' in request.POST and 'product' in request.POST and 'restriction' in request.POST:
        concierge_user_id = request.POST['concierge_user']
        master_product_id = request.POST['product']
        restriction_post = request.POST['restriction']
        restrictions = restriction_post.split(' ')
        concierge_user = ConciergeUserOption.objects.get(pk=concierge_user_id)
        master_product = MasterProduct.objects.get(pk=master_product_id)
        for restriction in restrictions:
            if restriction != '':
                required_product = ConciergeUserAcceptedProduct.objects.get_or_create(concierge_user=concierge_user,
                                                                product=master_product,
                                                                restriction=restriction)
        context['concierge_user_id'] = concierge_user_id
        context['allowed_accounts'] = ConciergeUserAcceptedProduct.objects.filter(concierge_user_id=concierge_user_id)
        return render(request, 'concierge/engine/allowed.html', context)
    return HttpResponse(status=500)


def engine_remove_allowed_product(request, context=None):
    if context is None:
        context = {}
    if request.method == "POST" and 'allowed_product' in request.POST and 'concierge_user' in request.POST:
        concierge_user_id = request.POST['concierge_user']
        allowed_product = request.POST['allowed_product']
        if ConciergeUserAcceptedProduct.objects.filter(pk=allowed_product,
                                                       concierge_user_id=concierge_user_id).exists():
            ConciergeUserAcceptedProduct.objects.filter(pk=allowed_product,
                                                        concierge_user_id=concierge_user_id).delete()
            context['allowed_accounts'] = ConciergeUserAcceptedProduct.objects.filter(
                concierge_user_id=concierge_user_id)

            context['concierge_user_id'] = concierge_user_id
            return render(request, 'concierge/engine/allowed.html', context)
    return HttpResponse(status=500)


@never_cache
def engine_get_existing_products(request, context=None):
    if context is None:
        context = {}
    if 'concierge_user_id' in request.GET:
        concierge_user_id = request.GET['concierge_user_id']
        concierge_user = ConciergeUserOption.objects.get(pk=concierge_user_id)
        ratetracker_reminders = RatetrackerReminder.objects.filter(user=concierge_user.user, is_deleted=False)
        context['current_fixed_term_accounts'] = ratetracker_reminders
        products = ProductPortfolio.objects.filter(user=concierge_user.user, is_deleted=False)
        context['current_accounts'] = products
        context['concierge_user_id'] = concierge_user_id
        context['add_existing_product_form'] = ConciergeUserAddExistingProductForm(initial={'user': concierge_user.user})
        return render(request, 'concierge/engine/existing_products.html', context)
    return HttpResponse(status=500)


def engine_delete_existing_products(request, product_portfolio_id, context=None):
    if context is None:
        context = {}
    if request.method == 'POST':
        products = get_object_or_404(ProductPortfolio, pk=product_portfolio_id)
        concierge_user = ConciergeUserOption.objects.get(user=products.user)
        products.delete()
        concierge_user_id = concierge_user.pk
        ratetracker_reminders = RatetrackerReminder.objects.filter(user=concierge_user.user, is_deleted=False)
        context['current_fixed_term_accounts'] = ratetracker_reminders
        products = ProductPortfolio.objects.filter(user=concierge_user.user, is_deleted=False)
        context['current_accounts'] = products
        context['concierge_user_id'] = concierge_user_id
        context['add_existing_product_form'] = ConciergeUserAddExistingProductForm(initial={'user': concierge_user.user})
        return render(request, 'concierge/engine/existing_products.html', context)
    return HttpResponse(status=500)


def engine_get_products_from_provider(request):
    if request.method == 'GET' and 'provider' in request.GET:
        provider_id = request.GET['provider']
        provider = Provider.objects.get(pk=provider_id)
        products = list(Product.objects.filter(provider=provider).order_by('title').values_list('pk', 'title'))
        return JsonResponse(products, safe=False)
    return HttpResponse(status=500)


def engine_add_existing_product(request, context=None):
    def urldecode(query):
        d = {}
        a = query.split('&')
        for s in a:
            if s.find('='):
                k, v = map(urllib.unquote, s.split('='))
                try:
                    d[k].append(v)
                except KeyError:
                    d[k] = [v]
        return d

    if context is None:
        context = {}

    if request.method == "POST":
        form = ConciergeUserAddExistingProductForm(request.POST)
        if form.is_valid():
            product = Product.objects.get(pk=form.cleaned_data['product'])

            if product.master_product.bestbuy_type.filter(title__icontains='bond').exists():
                # If this product is a Bond then we need to accept that we can't advise on them until maturity
                RatetrackerReminder(provider=form.cleaned_data['provider'], user=form.cleaned_data['user'], balance=form.cleaned_data['balance'],
                                    maturity_date=form.cleaned_data['maturity_date'],
                                    account_type=product.bestbuy_type.all()[0], rate=form.cleaned_data['rate'], term=form.cleaned_data['term'],
                                    fee_exempt=form.cleaned_data['fee_exempt']).save()
            else:
                ProductPortfolio(provider=form.cleaned_data['provider'], user=form.cleaned_data['user'],
                                 master_product=product.master_product, balance=form.cleaned_data['balance'],
                                 account_type=product.bestbuy_type.all()[0], is_synched=False).save()
        user_id = form.data['user']
        User = get_user_model()
        user = User.objects.get(pk=user_id)
        concierge_user = ConciergeUserOption.objects.get(user=user)
        ratetracker_reminders = RatetrackerReminder.objects.filter(user=user, is_deleted=False)
        context['current_fixed_term_accounts'] = ratetracker_reminders
        products = ProductPortfolio.objects.filter(user=user, is_deleted=False)
        context['current_accounts'] = products
        context['concierge_user_id'] = concierge_user.pk
        context['add_existing_product_form'] = form
        return render(request, 'concierge/engine/existing_products.html', context)
    return HttpResponse(status=500)


def engine_delete_existing_fixed_term_products(request, product_portfolio_id, context=None):
    if context is None:
        context = {}
    if request.method == 'POST':
        products = get_object_or_404(RatetrackerReminder, pk=product_portfolio_id)
        concierge_user = ConciergeUserOption.objects.get(user=products.user)
        products.delete()
        concierge_user_id = concierge_user.pk
        ratetracker_reminders = RatetrackerReminder.objects.filter(user=concierge_user.user, is_deleted=False)
        context['current_fixed_term_accounts'] = ratetracker_reminders
        products = ProductPortfolio.objects.filter(user=concierge_user.user)
        context['current_accounts'] = products
        context['concierge_user_id'] = concierge_user_id
        context['add_existing_product_form'] = ConciergeUserAddExistingProductForm(initial={'user': concierge_user.user})
        return render(request, 'concierge/engine/existing_products.html', context)
    return HttpResponse(status=500)

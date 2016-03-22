from products.models import ProductPortfolio, RatetrackerReminder
from django.shortcuts import render_to_response
from django.template import RequestContext

def delete_portfolio(request, template_file="products/healthcheck/success/deletesuccess.html"):
    context = RequestContext(request)
    if request.is_ajax() and request.method == 'POST':
        fixed = request.POST.get('fixed', None)
        id = int(request.POST['id'])
        
        if not fixed:
            portfolio = ProductPortfolio.objects.get(id=id)
        else:
            portfolio = RatetrackerReminder.objects.get(id=id)
        if portfolio.user == request.user or request.user.is_staff:
            portfolio.is_deleted = True
            portfolio.is_synched = False
            portfolio.save()

        return render_to_response(template_file, context_instance=context)


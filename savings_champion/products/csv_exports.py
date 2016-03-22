import csv
from django.http import HttpResponse

def export_portfolio(description="Export selected objects as CSV file",
                         fields=None, exclude=None, header=True):
    """
    This function returns an export csv action
    'fields' and 'exclude' work like in django ModelForm
    'header' is whether or not to output the column names as the first row
    """
    def export_as_portfolio_csv(modeladmin, request, queryset):
        """
        Generic csv export admin action.
        based on http://djangosnippets.org/snippets/1697/
        """
        opts = modeladmin.model._meta
        field_names = set([field.name for field in opts.fields])
        if fields:
            fieldset = set(fields)
            field_names = field_names & fieldset
        elif exclude:
            excludeset = set(exclude)
            field_names = field_names - excludeset

        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=%s.csv' % unicode(opts).replace('.', '_')

        writer = csv.writer(response)
        if header:
            writer.writerow(['Email', 'First Name', 'Last Name', 'Provider', 'Account Type', 'Balance', 'Product', 'SC Code', 'Opening Date', 'Bonus Term', 'Bonus Amount', 'Notice', 'Created Date'])
        
        for portfolio in queryset:
            bonus_amount  = 0
            if portfolio.product.bonus_amount:
                bonus_amount = portfolio.product.bonus_amount * 100
                  
                  
            writer.writerow([portfolio.user.email, 
                               portfolio.user.first_name,
                               portfolio.user.last_name,
                               portfolio.provider.title,
                               portfolio.account_type, portfolio.balance, 
                               portfolio.product, 
                               portfolio.product.sc_code,
                               portfolio.opening_date,
                               portfolio.product.bonus_term,
                               bonus_amount,
                               portfolio.product.notice,
                               portfolio.created_date])
            
        return response
    export_as_portfolio_csv.short_description = description
    return export_as_portfolio_csv

def export_reminder(description="Export selected objects as CSV file",
                         fields=None, exclude=None, header=True):
    """
    This function returns an export csv action
    'fields' and 'exclude' work like in django ModelForm
    'header' is whether or not to output the column names as the first row
    """
    def export_as_reminder_csv(modeladmin, request, queryset):
        """
        Generic csv export admin action.
        based on http://djangosnippets.org/snippets/1697/
        """
        opts = modeladmin.model._meta
        field_names = set([field.name for field in opts.fields])
        if fields:
            fieldset = set(fields)
            field_names = field_names & fieldset
        elif exclude:
            excludeset = set(exclude)
            field_names = field_names - excludeset

        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=%s.csv' % unicode(opts).replace('.', '_')

        writer = csv.writer(response)
        if header:
            writer.writerow(['Email', 'First Name', 'Last Name', 'Provider', 'Account Type', 'Balance', 'Maturity Date', 'Created Date'])
        
        for reminder in queryset:
            writer.writerow([reminder.user.email, 
                          reminder.user.first_name, 
                          reminder.user.last_name, 
                          reminder.provider.title, 
                          reminder.account_type, 
                          reminder.balance, 
                          reminder.maturity_date,
                          reminder.created_date])

            
        return response
    export_as_reminder_csv.short_description = description
    return export_as_reminder_csv

def export_as_csv_action(description="Export selected objects as CSV file",
                         fields=None, exclude=None, header=True):
    """
    This function returns an export csv action
    'fields' and 'exclude' work like in django ModelForm
    'header' is whether or not to output the column names as the first row
    """
    def export_as_csv(modeladmin, request, queryset):
        """
        Generic csv export admin action.
        based on http://djangosnippets.org/snippets/1697/
        """
        opts = modeladmin.model._meta
        field_names = set([field.name for field in opts.fields])
        if fields:
            fieldset = set(fields)
            field_names = field_names & fieldset
        elif exclude:
            excludeset = set(exclude)
            field_names = field_names - excludeset

        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=%s.csv' % unicode(opts).replace('.', '_')

        writer = csv.writer(response)
        if header:
            writer.writerow(list(field_names))
        for obj in queryset:
            writer.writerow([unicode(getattr(obj, field)).encode("utf-8","replace") for field in field_names])
        return response
    export_as_csv.short_description = description
    return export_as_csv

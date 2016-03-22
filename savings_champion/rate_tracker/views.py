from django.shortcuts import render


def rate_tracker_portfolio(request, context=None):
    if context is None:
        context = {}
    return render(request, 'portfolio.html', context)
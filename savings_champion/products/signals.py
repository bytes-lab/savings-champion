import django.dispatch

update_portfolio = django.dispatch.Signal(providing_args=["user",])

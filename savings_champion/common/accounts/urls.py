"""
URLconf for registration and activation, using django-registration's
default backend.

If the default behavior of these views is acceptable to you, simply
use a line like this in your root URLconf to set up the default URLs
for registration::

    (r'^accounts/', include('registration.backends.default.urls')),

This will also automatically set up the views in
``django.contrib.auth`` at sensible default locations.

If you'd like to customize the behavior (e.g., by passing extra
arguments to the various views) or split up the URLs, feel free to set
up your own URL patterns for these views instead.

"""

from django.conf.urls import *
from django.views.generic import TemplateView
from common.accounts.forms import SCPasswordResetForm, SCSetPasswordForm

urlpatterns = patterns('',
                       url(r'^your-profile/$', 'common.accounts.views.your_account', name='your_account'),
                       url(r'^your-profile/update-subscriptions/$', 'common.accounts.views.update_subscriptions',
                           name='update_subscriptions'),
                       url(r'^your-profile/deleted-account/$', 'common.accounts.views.delete_account',
                           name='delete_account'),
                       url(r'^your-profile/update-details/$', 'common.accounts.views.update_details',
                           name='update_details'),
                       url(r'^your-profile/change-password/$', 'common.accounts.views.change_password',
                           name='change_password'),
                       url(r'^activate/complete/$', 'common.accounts.views.finish_activation',
                           name='activation_complete'),
                       url(r'^activate/resend/$', 'common.accounts.views.resend_activation', name='resend_activation'),
                       url(r'^activate/(?P<activation_key>\w+)/$', 'common.accounts.views.activate',
                           name='registration_activate'),

                       #url(r'^timregister/$', TIMRegister.as_view(), name='timregistration_register'),
                       url(r'^timregister/complete/$', TemplateView.as_view(template_name="thisismoney/registration_complete.html"),
                           name='timregistration_complete'),

                       #url(r'^register/complete/$', TemplateView.as_view(template_name="registration/registration_complete.html"), name='registration_complete'),

                       #url(r'^register/closed/$',TemplateView.as_view(template_name="registration/registration_closed.html"), name='registration_disallowed'),

                       url(r'^password/reset/$', 'django.contrib.auth.views.password_reset',
                           {'template_name': 'accounts/password_reset.html',
                            'password_reset_form': SCPasswordResetForm,
                            'email_template_name': 'accounts/sc_password_reset_email.txt',
                            'post_reset_redirect': 'sc_password_reset_done'}, name='sc_password_reset'),
                       url(r'^password/reset/done/$', 'django.contrib.auth.views.password_reset_done',
                           {'template_name': 'accounts/password_reset_done.html'}, name='sc_password_reset_done'),
                       url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$',
                           'django.contrib.auth.views.password_reset_confirm',
                           {'template_name': 'accounts/password_reset_confirm.html',
                            'post_reset_redirect': 'sc_password_reset_complete',
                            'set_password_form': SCSetPasswordForm},
                           name='sc_password_reset_confirm'),
                       url(r'^password/reset/complete/$', 'django.contrib.auth.views.password_reset_complete',
                           {'template_name': 'accounts/password_reset_complete.html'},
                           name='sc_password_reset_complete'),

                       url(r'^login/$', 'common.accounts.views.login', {'template_name': 'accounts/login.html'},
                           name='auth_login'),

                       url(r'^healthcheck-signup/$', 'common.accounts.views.healthcheck_signup',
                           name='healthcheck_signup'),
                       url(r'^healthcheck-signup/basket/$', 'common.accounts.views.healthcheck_basket_signup',
                           name='healthcheck_basket_signup'),
                       url(r'^healthcheck-signup/basket/initial/$', 'common.accounts.views.healthcheck_basket_initial',
                           name='healthcheck_basket_initial'),
                       url(r'^healthcheck-signup/basket/ratetracker/$',
                           'common.accounts.views.healthcheck_basket_ratetracker',
                           name='healthcheck_basket_ratetracker'),
                       url(r'^healthcheck-signup/initial/$', 'common.accounts.views.healthcheck_add_initial_products',
                           name='healthcheck_signup_initial'),
                       url(r'^healthcheck-signup/basket/thankyou/$', 'ifa.views.basket_landing',
                           name='healthcheck_thankyou'),
                       url(r'^healthcheck-signup/remind/$', 'common.accounts.views.healthcheck_remind',
                           name='healthcheck_remind'),
                       url(r'^healthcheck-signup/remind/thankyou/$',
                           'common.accounts.views.healthcheck_remind_finished', name='healthcheck_remind_finished'),
                       url(r'^healthcheck-signup/remind/thankyou/activated/$',
                           'common.accounts.views.healthcheck_remind_already_activated',
                           name='healthcheck_remind_already_activated'),
                       (r'', include('registration.backends.default.urls')),
)

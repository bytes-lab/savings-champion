from ckeditor.fields import RichTextField
from django.conf import settings
from django.db import models
from django_extensions.db.fields import UUIDField

from common.tasks import send_email


class RatetrackerAlert(models.Model):

    uuid = UUIDField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    alert_email = RichTextField(default='', config_name='readonly_html_display')
    authorised = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        super(RatetrackerAlert, self).save(*args, **kwargs)
        if self.authorised:
            send_email.delay('Your savings accounts require your attention',
                             message='',
                             html_message=self.alert_email,
                             from_email='ratetracker@savingschampion.co.uk',
                             recipient_list=[self.user.email],
                             )

            from rate_tracker.tasks import update_portfolio_alert_dates  # Fixes potential issues with Model imports later down the line
            update_portfolio_alert_dates.delay(self.pk)

from django.db import models
from products.models import Provider, ProviderBestBuy, BasePortfolio, ProductPortfolio, RatetrackerReminder, ProductManager, Product, BestBuy
# Create your models here.

class TiMSignups(models.Model):
    email = models.CharField(max_length=100)
    completed_signup = models.BooleanField(default=False)
    completed_activation = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "This is Money Signup"

    def __unicode__(self):
        return self.email
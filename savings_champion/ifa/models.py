from django.db import models
import datetime
# Create your models here.


class IFASignup(models.Model):
    name = models.CharField(max_length=100, verbose_name='first name')
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=100)
    postcode = models.CharField(max_length=10, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    signup_amount = models.CharField(max_length=25)
    last_updated = models.DateTimeField(auto_now=True)


class BJSignup(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=100)
    postcode = models.CharField(max_length=10, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

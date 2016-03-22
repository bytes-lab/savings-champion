from django.db import models

class FileImport(models.Model):
    csv_file = models.FileField(upload_to='imports/')
    is_processed = models.BooleanField(default=False, blank=True)
    process_date = models.DateTimeField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now=True)
    last_updated = models.DateTimeField(auto_now_add=True)
    has_bestbuys = models.BooleanField(default=False, blank=True)
    lines_processed = models.PositiveIntegerField(default=0)


class UserListImport(models.Model):
    csv_file = models.FileField(upload_to='imports/')
    has_been_run = models.BooleanField(default=False, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
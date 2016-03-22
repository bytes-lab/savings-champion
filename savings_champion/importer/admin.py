from importer.models import FileImport
from django.contrib import admin


    
class FileImportAdmin(admin.ModelAdmin):
    list_display = ('csv_file','is_processed', 'has_bestbuys', 'created_date', 'last_updated')

    
admin.site.register([FileImport, ], FileImportAdmin)

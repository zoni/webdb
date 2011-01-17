from django.contrib import admin
from webdb.models import Record

class RecordAdmin(admin.ModelAdmin):
    pass
admin.site.register(Record, RecordAdmin)


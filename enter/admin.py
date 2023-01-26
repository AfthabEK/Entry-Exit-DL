from django.contrib import admin
from .models import record

class recordAdmin(admin.ModelAdmin):
    list_display = ('rollno', 'entrytime', 'exittime', 'date')
    readonly_fields = ('entrytime','date')

# Register your models here.
admin.site.register(record,recordAdmin)

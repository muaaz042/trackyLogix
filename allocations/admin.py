from django.contrib import admin
from .models import Allocation

@admin.register(Allocation)
class AllocationAdmin(admin.ModelAdmin):
    list_display = ('id', 'rfid', 'location', 'level', 'bin', 'allocated_at')
    list_filter = ('location__zone__warehouse', 'allocated_at')
    search_fields = ('rfid__epc', 'location__name')
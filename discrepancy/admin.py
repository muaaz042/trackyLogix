from django.contrib import admin
from .models import Discrepancy

@admin.register(Discrepancy)
class DiscrepancyAdmin(admin.ModelAdmin):
    list_display = ('id', 'inbound_item', 'quantity_found', 'damage_found', 'photo', 'created_at')
    list_filter = ('damage_found', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
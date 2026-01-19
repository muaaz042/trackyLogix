from django.contrib import admin
from .models import InboundRequest, InboundItem

@admin.register(InboundRequest)
class InboundRequestAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'client', 
        'warehouse', 
        'expected_arrival_date', 
        'status', 
        'approved_by_user', 
        'created_at'
    )
    list_filter = ('status', 'expected_arrival_date', 'created_at', 'warehouse')
    search_fields = (
        'id',
        'client__user__email', 
        'warehouse__name'
    )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(InboundItem)
class InboundItemAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'name', 
        'sku', 
        'quantity', 
        'remaining_quantity',  # <--- ADDED HERE
        'unit_type',
        'temp_range',
        'expected_arrival_date',
        'item_status', 
        'total_inventory_value',
        'inbound_request'
    )
    list_filter = ('item_status', 'unit_type', 'fragile', 'hazardous', 'created_at')
    search_fields = (
        'name', 
        'sku', 
        'batch_or_lot_no',
    )
    fieldsets = (
        ('Basic Info', {
            # ADDED remaining_quantity HERE
            'fields': ('inbound_request', 'name', 'sku', 'quantity', 'remaining_quantity', 'item_status')
        }),
        ('Physical Specs', {
            'fields': ('weight', 'dimensions', 'unit_type', 'fragile', 'hazardous')
        }),
        ('Environment & Value', {
            'fields': ('temp_range', 'humidity_range', 'total_inventory_value')
        }),
        ('Dates & Batches', {
            'fields': ('expected_arrival_date', 'batch_or_lot_no', 'expiry_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        })
    )
    readonly_fields = ('created_at', 'updated_at')
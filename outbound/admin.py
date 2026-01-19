from django.contrib import admin
from outbound.models import OutboundRequest, OutboundItem

class OutboundItemInline(admin.TabularInline):
    model = OutboundItem
    extra = 0
    fields = ('sku', 'requested_quantity', 'dispatched_quantity', 'item_status')
    readonly_fields = ('dispatched_quantity', 'item_status')

@admin.register(OutboundRequest)
class OutboundRequestAdmin(admin.ModelAdmin):
    # Removed assigned_to_user
    list_display = (
        'id', 'client', 'warehouse', 'order_type', 
        'status' 
    )
    list_filter = ('status', 'order_type', 'warehouse', 'client')
    search_fields = ('external_order_number', 'destination_address', 'client__user__email')
    inlines = [OutboundItemInline]
    readonly_fields = ('created_at', 'updated_at', 'approved_by_user')
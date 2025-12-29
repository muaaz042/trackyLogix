from django.contrib import admin
from .models import InboundRequest, InboundItem

class InboundItemInline(admin.TabularInline):
    """
    Allows InboundItems to be edited directly inside the InboundRequest page.
    """
    model = InboundItem
    extra = 0  # Removes empty extra rows by default
    fields = ('name', 'sku', 'quantity', 'unit_type', 'item_status')
    readonly_fields = ('item_status',)  # Prevent accidental status changes here if needed
    show_change_link = True


@admin.register(InboundRequest)
class InboundRequestAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'get_client_email', 
        'warehouse', 
        'status',
        'transport_mode',
        'driver_name',
        'driver_contact',
        'vehicle_number',
        'additional_notes', 
        'approved_by_user', 
        'created_at'
    )
    list_filter = ('status', 'warehouse', 'created_at')
    search_fields = (
        'id', 
        'client__user__email',  # Search by client email
        'driver_name', 
        'vehicle_number'
    )
    readonly_fields = ('created_at', 'updated_at', 'approved_by_user')
    inlines = [InboundItemInline]
    
    # Helper to display email since 'client' is a profile object
    @admin.display(description='Client Email', ordering='client__user__email')
    def get_client_email(self, obj):
        return obj.client.user.email

    fieldsets = (
        ("Request Info", {
            "fields": ("warehouse", "client", "status", "approved_by_user")
        }),
        ("Transport Details", {
            "fields": ("transport_mode", "driver_name", "driver_contact", "vehicle_number", "additional_notes")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),  # Hide by default to save space
        }),
    )


@admin.register(InboundItem)
class InboundItemAdmin(admin.ModelAdmin):
    """
    Separate view for items if you need to search for a specific SKU across all requests.
    """
    list_display = (
        'id', 
        'name',
        'description', 
        'sku',
        'carton_weight',
        'carton_dimensions',
        'temperature_range',
        'fragile',
        'hazardous',
        'humidity', 
        'quantity', 
        'total_inventory_value',
        'unit_type', 
        'item_status', 
        'expected_arrival_date',
        'get_request_id'
    )
    list_filter = ('item_status', 'unit_type', 'sku')
    search_fields = ('name', 'sku', 'inbound_request__id')
    
    @admin.display(description='Request ID', ordering='inbound_request')
    def get_request_id(self, obj):
        return obj.inbound_request.id
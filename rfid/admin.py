from django.contrib import admin
from .models import RFIDTag

@admin.register(RFIDTag)
class RFIDTagAdmin(admin.ModelAdmin):
    # Use the custom method 'get_inbound_item_name' instead of the field 'inbound_item'
    list_display = ('id', 'epc', 'status', 'get_inbound_item_name', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('epc', 'inbound_item__name', 'inbound_item__sku')
    readonly_fields = ('created_at', 'updated_at')

    # Define the custom method to return only the name
    def get_inbound_item_name(self, obj):
        return obj.inbound_item.name if obj.inbound_item else "-"
    
    # Set the column header name in the admin panel
    get_inbound_item_name.short_description = 'Inbound Item'
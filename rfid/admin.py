from django.contrib import admin
from .models import RFIDTag

@admin.register(RFIDTag)
class RFIDTagAdmin(admin.ModelAdmin):
    list_display = ('id', 'epc', 'sku', 'status', 'client', 'warehouse', 'inbound_request', 'created_at')
    list_filter = ('status', 'warehouse', 'created_at')
    search_fields = ('epc', 'sku', 'batch_or_lot_no', 'client__user__email', 'inbound_request__id')
    
    # REMOVED: 'created_by_user'
    readonly_fields = ('created_at', 'updated_at')
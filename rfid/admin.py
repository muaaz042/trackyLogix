from django.contrib import admin
from .models import RFIDTag

@admin.register(RFIDTag)
class RFIDTagAdmin(admin.ModelAdmin):
    list_display = ('id','epc', 'status', 'inbound_item', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('epc', 'inbound_item__name', 'inbound_item__sku')
    readonly_fields = ('created_at', 'updated_at')
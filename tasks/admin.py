from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'name', 
        'status', # Task Status
        'get_inbound_request_info', # Custom column (ID - Email)
        'assigned_by_user', 
        'assigned_to_user', 
        'created_at'
    )
    list_filter = ('status', 'created_at')
    search_fields = (
        'name', 
        'assigned_to_user__email', 
        'assigned_by_user__email', 
        'inbound_request__id'
    )
    readonly_fields = ('created_at', 'updated_at')

    # Custom display to avoid showing the 'Request Status' which might be confusing
    @admin.display(description='Inbound Request', ordering='inbound_request')
    def get_inbound_request_info(self, obj):
        if not obj.inbound_request:
            return "-"
        # Shows: "Req #1 - user@email.com"
        return f"Req #{obj.inbound_request.id} - {obj.inbound_request.client.user.email} ({obj.status})"
from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'task_type',         # New field
        'status', 
        'assigned_to_user', 
        'inbound_request',   # Shows reference number via __str__
        'created_at'
    )
    list_filter = ('task_type', 'status', 'created_at')
    search_fields = (
        'description', 
        'assigned_to_user__email', 
        'assigned_by_user__email',
        'inbound_request__reference_number'  # Search by Request Ref ID
    )
    readonly_fields = ('created_at', 'updated_at')
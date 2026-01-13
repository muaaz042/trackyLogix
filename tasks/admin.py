from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'task_type',
        'status', 
        'assigned_to_user', 
        'inbound_request',
        'created_at'
    )
    list_filter = ('task_type', 'status', 'created_at')
    
    search_fields = (
        'description', 
        'assigned_to_user__email', 
        'assigned_by_user__email',
        'inbound_request__id', 
        'inbound_request__client__user__email'
    )
    readonly_fields = ('created_at', 'updated_at')
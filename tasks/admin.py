from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'task_type', 
        'request_id', 
        'status', 
        'assigned_to_deo', 
        'assigned_to_allocator', 
        'assigned_by_user'
    )
    list_filter = ('task_type', 'status', 'created_at')
    search_fields = ('description', 'request_id', 'assigned_to_deo__email')
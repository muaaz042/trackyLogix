from django.db import models
from django.conf import settings
# We import these models only for referencing in methods, not for ForeignKeys anymore
from inboundRequests.models import InboundRequest
from outbound.models import OutboundRequest

class Task(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed')
    ]

    TASK_TYPE_CHOICES = [
        ('inbound', 'Inbound'),
        ('outbound', 'Outbound'),
    ]

    task_type = models.CharField(max_length=20, choices=TASK_TYPE_CHOICES, default='inbound')
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # --- DYNAMIC LINKING ---
    # Stores the ID of either InboundRequest or OutboundRequest
    request_id = models.PositiveIntegerField(help_text="ID of the related Inbound or Outbound Request")

    # --- USER ASSIGNMENTS ---
    assigned_by_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='assigned_tasks',
        help_text="Manager who created the task"
    )

    # Changed: Specific field for DEO
    assigned_to_deo = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='deo_tasks',
        help_text="DEO assigned to this task"
    )

    # Added: Specific field for Allocator
    assigned_to_allocator = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='allocator_tasks',
        help_text="Allocator assigned to this task"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def related_object(self):
        """Helper to fetch the actual object based on type and ID"""
        if self.task_type == 'inbound':
            return InboundRequest.objects.filter(id=self.request_id).first()
        elif self.task_type == 'outbound':
            return OutboundRequest.objects.filter(id=self.request_id).first()
        return None

    def __str__(self):
        return f"{self.get_task_type_display()} Task #{self.id} (Req {self.request_id}) - {self.status}"
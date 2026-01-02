from django.db import models
from django.conf import settings
from inboundRequests.models import InboundRequest

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

    # CHANGED: Added task_type, Removed name
    task_type = models.CharField(max_length=20, choices=TASK_TYPE_CHOICES, default='inbound')
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Links
    inbound_request = models.ForeignKey(
        InboundRequest,
        on_delete=models.CASCADE,
        related_name='tasks',
        null=True, 
        blank=True,
        help_text="The Inbound Request this task is related to (if type is Inbound)"
    )
    
    # Placeholder for future Outbound Request:
    # outbound_request = models.ForeignKey(OutboundRequest, ..., null=True, blank=True)

    # Relationships
    assigned_by_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='assigned_tasks',
        help_text="Manager who created the task"
    )
    assigned_to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='my_tasks',
        help_text="DEO or Allocator assigned to the task"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # Dynamic string representation based on what request is attached
        ref = "N/A"
        if self.inbound_request:
            ref = self.inbound_request.reference_number
        
        return f"{self.get_task_type_display()} Task ({ref}) - {self.status}"
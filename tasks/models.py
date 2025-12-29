from django.db import models
from django.conf import settings
from inboundRequests.models import InboundRequest  # Import the model

class Task(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('blocked', 'Blocked'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Links
    inbound_request = models.ForeignKey(
        InboundRequest,
        on_delete=models.CASCADE,
        related_name='tasks',
        null=True, 
        blank=True,
        help_text="The Inbound Request this task is related to"
    )

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
        return f"{self.name} ({self.status})"
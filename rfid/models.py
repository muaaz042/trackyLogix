from django.db import models
from inboundRequests.models import InboundItem

class RFIDTag(models.Model):
    STATUS_CHOICES = [
        ('unencoded', 'Un-encoded'),
        ('encoded', 'Encoded'),
        ('allocated', 'Allocated'),
    ]

    # CHANGED: Added null=True, blank=True so it can be empty at creation
    epc = models.CharField(
        max_length=255, 
        unique=True, 
        null=True, 
        blank=True, 
        help_text="Electronic Product Code"
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unencoded')

    # Link to InboundItem
    inbound_item = models.ForeignKey(
        InboundItem, 
        on_delete=models.CASCADE, 
        related_name='rfid_tags'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.epc or 'Unencoded'} ({self.status})"
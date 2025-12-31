from django.db import models
from django.conf import settings
from inboundRequests.models import InboundRequest
from users.models import Warehouse, ClientProfile

class RFIDTag(models.Model):
    STATUS_CHOICES = [
        ('encoded', 'Encoded'),
        ('allocated', 'Allocated'),
    ]

    epc = models.CharField(max_length=255, unique=True, help_text="Electronic Product Code")
    sku = models.CharField(max_length=100)
    batch_or_lot_no = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='encoded')

    # Relationships
    client = models.ForeignKey(
        ClientProfile, 
        on_delete=models.CASCADE, 
        related_name='rfid_tags',
        help_text="Client who owns this inventory"
    )
    warehouse = models.ForeignKey(
        Warehouse, 
        on_delete=models.CASCADE, 
        related_name='rfid_tags',
        null=True, 
        blank=True
    )
    inbound_request = models.ForeignKey(
        InboundRequest, 
        on_delete=models.CASCADE, 
        related_name='rfid_tags',
        help_text="The inbound request this tag was generated for"
    )

    # REMOVED: created_by_user field
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.epc} ({self.sku})"
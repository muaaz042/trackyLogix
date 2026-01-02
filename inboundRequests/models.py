from django.db import models
from users.models import ClientProfile, Warehouse, User
from django.utils import timezone

class InboundRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    client = models.ForeignKey(ClientProfile, on_delete=models.CASCADE, related_name='inbound_requests')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='inbound_requests')
    
    # General date for the whole request
    expected_arrival_date = models.DateField(default=timezone.now)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    approved_by_user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='approved_inbound_requests'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Req #{self.id} - {self.client.user.email} ({self.status})"


class InboundItem(models.Model):
    # CHANGED: Only 2 statuses allowed now
    ITEM_STATUS_CHOICES = [
        ('not arrived yet', 'Not Arrived Yet'),
        ('arrived', 'Arrived'),
    ]

    UNIT_TYPE_CHOICES = [
        ('carton', 'Carton'),
        ('pallet', 'Pallet'),
        ('piece', 'Piece'),
        ('drum', 'Drum'),
    ]

    inbound_request = models.ForeignKey(InboundRequest, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    
    # --- PHYSICAL PROPERTIES ---
    weight = models.DecimalField(max_digits=10, decimal_places=2, help_text="Weight in KG")
    dimensions = models.CharField(max_length=100, help_text="L x W x H (cm)", default="0x0x0")
    
    # --- NEW FIELDS ---
    expected_arrival_date = models.DateField(default=timezone.now, help_text="Expected arrival for this specific item")
    
    temp_range = models.CharField(max_length=50, blank=True, null=True, help_text="e.g., '10-20 C'")
    unit_type = models.CharField(max_length=20, choices=UNIT_TYPE_CHOICES, default='carton')
    fragile = models.BooleanField(default=False)
    hazardous = models.BooleanField(default=False)
    total_inventory_value = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, help_text="Total value in currency")
    humidity_range = models.CharField(max_length=50, blank=True, null=True, help_text="e.g., '40-60%'")

    # --- EXISTING OPTIONAL FIELDS ---
    batch_or_lot_no = models.CharField(max_length=100, blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)
    
    # CHANGED: Default is now 'not arrived yet'
    item_status = models.CharField(max_length=30, choices=ITEM_STATUS_CHOICES, default='not arrived yet')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.sku})"
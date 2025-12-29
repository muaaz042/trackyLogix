from django.db import models
from django.conf import settings
from users.models import Warehouse, ClientProfile  # Import ClientProfile

class InboundRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    # Links
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='inbound_requests')
    
    # CHANGED: Now points to ClientProfile instead of User
    client = models.ForeignKey(
        ClientProfile, 
        on_delete=models.CASCADE, 
        related_name='inbound_requests'
    )
    
    # Request Details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transport_mode = models.CharField(max_length=50)
    driver_name = models.CharField(max_length=100, blank=True, null=True)
    driver_contact = models.CharField(max_length=20, blank=True, null=True)
    vehicle_number = models.CharField(max_length=50, blank=True, null=True)
    additional_notes = models.TextField(blank=True, null=True)

    # Manager Action (Remains User)
    approved_by_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='approved_inbound_requests',
        help_text="Manager who approved this request"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # Updated to access email via client.user
        return f"Req #{self.id} - {self.client.user.email} ({self.status})"


class InboundItem(models.Model):
    UNIT_TYPE_CHOICES = [
        ('carton', 'Carton'),
        ('pallet', 'Pallet'),
        ('drum', 'Drum'),
    ]

    ITEM_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('not arrived yet', 'Not Arrived Yet'),
        ('arrived', 'Arrived'),
    ]

    inbound_request = models.ForeignKey(
        InboundRequest, 
        on_delete=models.CASCADE, 
        related_name='items'
    )
    
    # Item Details
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    sku = models.CharField(max_length=100)
    
    # Specs
    carton_weight = models.DecimalField(max_digits=10, decimal_places=2, help_text="Weight in KG")
    carton_dimensions = models.CharField(max_length=100, help_text="L x W x H")
    
    # Conditions
    temperature_range = models.CharField(max_length=50, blank=True, null=True)
    fragile = models.BooleanField(default=False)
    hazardous = models.BooleanField(default=False)
    humidity = models.CharField(max_length=50, blank=True, null=True)
    
    # Quantity & Value
    quantity = models.PositiveIntegerField()
    unit_type = models.CharField(max_length=20, choices=UNIT_TYPE_CHOICES, default='carton')
    total_inventory_value = models.DecimalField(max_digits=15, decimal_places=2)
    expected_arrival_date = models.DateField(help_text="Expected arrival date of the item")
    item_status = models.CharField(max_length=20, choices=ITEM_STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.name} ({self.sku}) - {self.quantity} {self.unit_type}"
from django.db import models
from django.utils import timezone
from users.models import ClientProfile, Warehouse, User

class OutboundRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),        # Inventory reserved
        ('in_progress', 'In Progress'),  # Picking started
        ('dispatched', 'Dispatched'),    # Handed over to courier/truck
        ('rejected', 'Rejected'),
    ]

    ORDER_TYPE_CHOICES = [
        ('ecom', 'E-Commerce'),
        ('finished', 'Finished Goods'),
    ]

    # --- Core Links ---
    client = models.ForeignKey(ClientProfile, on_delete=models.CASCADE, related_name='outbound_requests')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='outbound_requests')
    
    # --- Classification & References ---
    order_type = models.CharField(max_length=20, choices=ORDER_TYPE_CHOICES, default='ecom')
    external_order_number = models.CharField(max_length=100, blank=True, null=True, help_text="Client's Order ID or PO Number")

    # --- Logistics & Customer Info ---
    customer_name = models.CharField(max_length=255, blank=True, null=True)
    customer_phone = models.CharField(max_length=50, blank=True, null=True)
    destination_address = models.TextField()
    
    expected_dispatch_date = models.DateField(default=timezone.now)

    # --- Shipping Details ---
    courier_name = models.CharField(max_length=100, blank=True, null=True, help_text="DHL, FedEx, or Trucking Co.")
    tracking_number = models.CharField(max_length=100, blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # --- User Assignments ---
    approved_by_user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='approved_outbound_requests'
    )
    # REMOVED: assigned_to_user (Now handled via Tasks app)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Outbound #{self.id} ({self.order_type}) - {self.external_order_number or 'No Ref'}"


class OutboundItem(models.Model):
    ITEM_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('dispatched', 'Dispatched'),
        ('missing', 'Missing'),
        ('damaged', 'Damaged'),
    ]

    request = models.ForeignKey(OutboundRequest, on_delete=models.CASCADE, related_name='items')
    sku = models.CharField(max_length=100)
    
    requested_quantity = models.PositiveIntegerField()
    dispatched_quantity = models.PositiveIntegerField(default=0)
    
    item_status = models.CharField(max_length=20, choices=ITEM_STATUS_CHOICES, default='pending')
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.sku} (Req: {self.requested_quantity}, Disp: {self.dispatched_quantity}) - {self.item_status}"
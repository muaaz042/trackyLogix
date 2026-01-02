from django.db import models
from django.conf import settings
from inboundRequests.models import InboundItem

class Discrepancy(models.Model):
    # Links
    inbound_item = models.ForeignKey(
        InboundItem,
        on_delete=models.CASCADE,
        related_name='discrepancies',
        help_text="The item where discrepancy was found"
    )
    reported_by_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reported_discrepancies'
    )

    # Discrepancy Details
    quantity_expected = models.PositiveIntegerField()
    quantity_found = models.PositiveIntegerField()
    damage_found = models.BooleanField(default=False)
    note = models.TextField(blank=True, null=True)
    
    # Stores only the URL path in DB (e.g., "uploads/photo.jpg")
    photo = models.ImageField(upload_to='uploads/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Discrepancy on {self.inbound_item} (Found: {self.quantity_found})"
from django.db import models
from rfid.models import RFIDTag
from locations.models import Location, Aisle, Rack, Level, Bin

class Allocation(models.Model):
    # RFID is strictly required and must be unique (OneToOne)
    rfid = models.OneToOneField(
        RFIDTag, 
        on_delete=models.CASCADE, 
        related_name='allocation',
        error_messages={'unique': 'This RFID tag is already allocated.'}
    )

    # Hierarchy Fields
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True)
    aisle = models.ForeignKey(Aisle, on_delete=models.CASCADE, null=True, blank=True)
    rack = models.ForeignKey(Rack, on_delete=models.CASCADE, null=True, blank=True)
    level = models.ForeignKey(Level, on_delete=models.CASCADE, null=True, blank=True)
    bin = models.ForeignKey(Bin, on_delete=models.CASCADE, null=True, blank=True)

    allocated_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Alloc: {self.rfid.epc} -> {self.location.name if self.location else 'Unknown'}"
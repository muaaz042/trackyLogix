from django.db import models
from users.models import Warehouse

class Zone(models.Model):
    ZONE_TYPE_CHOICES = [
        ('INBOUND', 'Inbound'),
        ('STORAGE', 'Storage'),
        ('PICK', 'Pick'),
        ('COLD', 'Cold Storage'),
        ('HAZMAT', 'Hazardous Materials'),
        ('DISPATCH', 'Dispatch'),
    ]
    CLIENT_TYPE_CHOICES = [
        ('ECOM', 'E-Commerce'),
        ('FINISHED', 'Finished Goods'),
        ('BOTH', 'Both'),
    ]

    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='zones')
    name = models.CharField(max_length=100)
    zone_type = models.CharField(max_length=20, choices=ZONE_TYPE_CHOICES)
    allowed_client_type = models.CharField(max_length=20, choices=CLIENT_TYPE_CHOICES, default='BOTH')
    min_temp = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    max_temp = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    hazard_allowed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.warehouse.name})"

class Aisle(models.Model):
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='aisles')
    name = models.CharField(max_length=50)
    epc = models.CharField(max_length=255, unique=True, null=True, blank=True)

    def __str__(self):
        return f"{self.zone.name} - {self.name}"

class Rack(models.Model):
    RACK_TYPE_CHOICES = [
        ('PALLET', 'Pallet Rack'),
        ('SHELF', 'Shelving Unit'),
    ]
    aisle = models.ForeignKey(Aisle, on_delete=models.CASCADE, related_name='racks')
    name = models.CharField(max_length=50)
    rack_type = models.CharField(max_length=20, choices=RACK_TYPE_CHOICES)
    max_weight = models.DecimalField(max_digits=10, decimal_places=2, help_text="Max weight in KG")
    epc = models.CharField(max_length=255, unique=True, null=True, blank=True)

    def __str__(self):
        return f"{self.aisle.name} - {self.name}"

class Level(models.Model):
    rack = models.ForeignKey(Rack, on_delete=models.CASCADE, related_name='levels')
    name = models.CharField(max_length=50)
    max_weight = models.DecimalField(max_digits=10, decimal_places=2, help_text="Max weight in KG")
    epc = models.CharField(max_length=255, unique=True, null=True, blank=True)

    def __str__(self):
        return f"{self.rack.name} - {self.name}"

class Bin(models.Model):
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='bins')
    name = models.CharField(max_length=50)
    max_units = models.PositiveIntegerField()
    max_weight = models.DecimalField(max_digits=10, decimal_places=2, help_text="Max weight in KG")
    epc = models.CharField(max_length=255, unique=True, null=True, blank=True)

    def __str__(self):
        return f"{self.level.name} - {self.name}"

class Location(models.Model):
    LOCATION_TYPE_CHOICES = [
        ('FLOOR', 'Floor'),
        ('PALLET', 'Pallet Position'),
        ('SHELF', 'Shelf'),
        ('BIN', 'Bin'),
        ('COLD', 'Cold Storage'),
        ('HAZMAT', 'Hazmat'),
    ]

    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='locations')
    
    # Hierarchy pointers (at least one required)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, null=True, blank=True, related_name='locations_as_zone')
    level = models.ForeignKey(Level, on_delete=models.CASCADE, null=True, blank=True, related_name='locations_as_level')
    bin = models.ForeignKey(Bin, on_delete=models.CASCADE, null=True, blank=True, related_name='locations_as_bin')

    location_code = models.CharField(max_length=255, unique=True, blank=True)
    location_type = models.CharField(max_length=20, choices=LOCATION_TYPE_CHOICES)

    def __str__(self):
        return self.location_code
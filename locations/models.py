from django.db import models
from users.models import Warehouse

# Shared choices for storage entities
STORAGE_STATUS_CHOICES = [
    ('EMPTY', 'Empty'),
    ('PARTIAL', 'Partially Filled'),
    ('FULL', 'Full'),
]

# 1. ZONE
class Zone(models.Model):
    ZONE_TYPE_CHOICES = [
        ('INBOUND', 'Inbound'),
        ('STORAGE', 'Storage'),
        ('PICK', 'Pick'),
        ('COLD', 'Cold Storage'),
        ('HAZMAT', 'Hazardous Materials'),
        ('DISPATCH', 'Dispatch'),
    ]
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='zones')
    name = models.CharField(max_length=100)
    zone_type = models.CharField(max_length=20, choices=ZONE_TYPE_CHOICES)

    def __str__(self):
        return f"{self.name} ({self.warehouse.name})"

# 2. LOCATION
class Location(models.Model):
    LOCATION_TYPE_CHOICES = [
        ('FLOOR', 'Floor'),
        ('PALLET', 'Pallet'),
        ('SHELF', 'Shelf'),
        ('BIN', 'Bin'),
        ('COLD', 'Cold Storage'),
        ('HAZMAT', 'Hazmat'),
    ]

    # REMOVED: allowed_client_type

    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='locations')
    name = models.CharField(max_length=100)
    location_type = models.CharField(max_length=20, choices=LOCATION_TYPE_CHOICES)
    min_temp = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    max_temp = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    hazard_allowed = models.BooleanField(default=False)

    # ADDED: Status field(In case of floor storage)
    status = models.CharField(max_length=20, choices=STORAGE_STATUS_CHOICES, default='EMPTY')

    def __str__(self):
        return f"{self.zone.name} - {self.name}"

# 3. AISLE
class Aisle(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='aisles')
    name = models.CharField(max_length=50)
    epc = models.CharField(max_length=255, unique=True, null=True, blank=True)

    # ADDED: Status field
    status = models.CharField(max_length=20, choices=STORAGE_STATUS_CHOICES, default='EMPTY')

    def __str__(self):
        return f"{self.location.name} - {self.name}"

# 4. RACK
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
    
    # ADDED: Status field
    status = models.CharField(max_length=20, choices=STORAGE_STATUS_CHOICES, default='EMPTY')

    def __str__(self):
        return f"{self.aisle.name} - {self.name}"

# 5. LEVEL
class Level(models.Model):
    rack = models.ForeignKey(Rack, on_delete=models.CASCADE, related_name='levels')
    name = models.CharField(max_length=50)
    max_weight = models.DecimalField(max_digits=10, decimal_places=2, help_text="Max weight in KG")
    epc = models.CharField(max_length=255, unique=True, null=True, blank=True)

    # ADDED: Status field
    status = models.CharField(max_length=20, choices=STORAGE_STATUS_CHOICES, default='EMPTY')

    def __str__(self):
        return f"{self.rack.name} - {self.name}"

# 6. BIN
class Bin(models.Model):
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='bins')
    name = models.CharField(max_length=50)
    max_units = models.PositiveIntegerField()
    max_weight = models.DecimalField(max_digits=10, decimal_places=2, help_text="Max weight in KG")
    epc = models.CharField(max_length=255, unique=True, null=True, blank=True)

    # ADDED: Status field
    status = models.CharField(max_length=20, choices=STORAGE_STATUS_CHOICES, default='EMPTY')

    def __str__(self):
        return f"{self.level.name} - {self.name}"
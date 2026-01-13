from django.core.exceptions import ValidationError
# FIX: Import local models from locations.models
from locations.models import Location, Zone 
# FIX: Import WarehouseUserManagement from users.models
from users.models import WarehouseUserManagement

def get_manager_warehouse(user):
    """
    Helper to get the warehouse ID for a manager.
    """
    link = WarehouseUserManagement.objects.filter(user=user).first()
    if not link:
        raise ValidationError("Manager is not assigned to any warehouse.")
    return link.warehouse

def generate_location_code(location_instance):
    """
    Generates code based on hierarchy:
    Zone: Z{id}
    Level: Z{id}-A{id}-R{id}-L{id}
    Bin: Z{id}-A{id}-R{id}-L{id}-B{id}
    """
    # 1. BIN Logic
    if location_instance.bin:
        # Force refresh of related objects from DB to ensure we get latest parents
        location_instance.refresh_from_db()
        b = location_instance.bin
        l = b.level
        r = l.rack
        a = r.aisle
        z = a.zone
        return f"Z{z.id}-A{a.id}-R{r.id}-L{l.id}-B{b.id}"

    # 2. LEVEL Logic
    if location_instance.level:
        location_instance.refresh_from_db()
        l = location_instance.level
        r = l.rack
        a = r.aisle
        z = a.zone
        return f"Z{z.id}-A{a.id}-R{r.id}-L{l.id}"
    
    # 3. ZONE Logic
    if location_instance.zone:
        location_instance.refresh_from_db()
        return f"Z{location_instance.zone.id}"
    
    return "UNKNOWN-LOC"

def create_or_update_location_service(instance, validated_data):
    """
    Service to handle saving a Location and updating its code.
    """
    # Update fields on instance
    for attr, value in validated_data.items():
        setattr(instance, attr, value)

    if not (instance.zone or instance.level or instance.bin):
        raise ValidationError("Location must map to at least a Zone, Level, or Bin.")

    # Generate and Save
    code = generate_location_code(instance)
    instance.location_code = code
    instance.save()
    return instance

def refresh_related_location_codes(locations_queryset):
    """
    Iterates over a queryset of locations and refreshes their codes.
    Used by signals when a parent (Aisle, Rack, etc.) changes.
    """
    for loc in locations_queryset:
        new_code = generate_location_code(loc)
        if loc.location_code != new_code:
            loc.location_code = new_code
            loc.save(update_fields=['location_code'])
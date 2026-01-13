from locations.models import Zone, Location, Aisle, Rack, Level, Bin
from users.models import WarehouseUserManagement

def get_user_warehouse_ids(user):
    if user.role == 'admin':
        # Admin sees all? Or specific ones? Usually Admins can see all.
        # But per your requirement "Admin can only view them", we assume all or attached.
        # Let's assume Admin sees all for now, or you can restrict to attached warehouses.
        return WarehouseUserManagement.objects.filter(user=user).values_list('warehouse_id', flat=True)
    
    # Managers and Allocators are restricted to their assigned warehouses
    return WarehouseUserManagement.objects.filter(user=user).values_list('warehouse_id', flat=True)

def get_zones_for_user(user):
    wh_ids = get_user_warehouse_ids(user)
    return Zone.objects.filter(warehouse_id__in=wh_ids)

def get_locations_for_user(user):
    wh_ids = get_user_warehouse_ids(user)
    return Location.objects.filter(warehouse_id__in=wh_ids)

# --- Hierarchical Selectors (Filtering parents by warehouse) ---

def get_aisles_for_user(user):
    wh_ids = get_user_warehouse_ids(user)
    return Aisle.objects.filter(zone__warehouse_id__in=wh_ids)

def get_racks_for_user(user):
    wh_ids = get_user_warehouse_ids(user)
    return Rack.objects.filter(aisle__zone__warehouse_id__in=wh_ids)

def get_levels_for_user(user):
    wh_ids = get_user_warehouse_ids(user)
    return Level.objects.filter(rack__aisle__zone__warehouse_id__in=wh_ids)

def get_bins_for_user(user):
    wh_ids = get_user_warehouse_ids(user)
    return Bin.objects.filter(level__rack__aisle__zone__warehouse_id__in=wh_ids)
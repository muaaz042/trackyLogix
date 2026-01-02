from rfid.models import RFIDTag
from users.models import WarehouseUserManagement

def get_allowed_warehouses(user):
    return WarehouseUserManagement.objects.filter(user=user).values_list('warehouse_id', flat=True)

def get_rfid_tags_for_user(user):
    """
    Returns the queryset of RFID tags visible to the user.
    """
    # 1. DEO: Can see tags in their assigned warehouse
    if user.role == "DEO":
        allowed_ids = get_allowed_warehouses(user)
        # Fix: Traverse through item -> request -> warehouse
        return RFIDTag.objects.filter(inbound_item__inbound_request__warehouse_id__in=allowed_ids)

    # 2. Manager / Allocator: Warehouse Specific
    if user.role in ["manager", "Allocator"]:
        allowed_ids = get_allowed_warehouses(user)
        # Fix: Traverse through item -> request -> warehouse
        return RFIDTag.objects.filter(inbound_item__inbound_request__warehouse_id__in=allowed_ids)

    # 3. Client: Own Tags
    if user.role == "client":
        # Fix: Traverse through item -> request -> client -> user
        return RFIDTag.objects.filter(inbound_item__inbound_request__client__user=user)

    # 4. Admin: All
    if user.role == "admin":
        return RFIDTag.objects.all()

    return RFIDTag.objects.none()
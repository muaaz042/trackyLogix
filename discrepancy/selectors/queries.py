from discrepancy.models import Discrepancy
from users.models import WarehouseUserManagement

def get_allowed_warehouses(user):
    return WarehouseUserManagement.objects.filter(user=user).values_list('warehouse_id', flat=True)

def get_discrepancies_for_user(user):
    """
    Returns discrepancies visible to the user.
    """
    # 1. DEO / Manager: Can see discrepancies in their warehouses
    if user.role in ["DEO", "manager"]:
        allowed_ids = get_allowed_warehouses(user)
        return Discrepancy.objects.filter(
            inbound_item__inbound_request__warehouse_id__in=allowed_ids
        )

    # 2. Admin: See All
    if user.role == "admin":
        return Discrepancy.objects.all()

    return Discrepancy.objects.none()
from allocations.models import Allocation
from users.models import WarehouseUserManagement

def get_allocations_for_user(user):
    """
    Returns allocations visible to the user.
    """
    if user.role == 'admin':
        return Allocation.objects.all()

    # Filter by user's assigned warehouse
    wh_ids = WarehouseUserManagement.objects.filter(user=user).values_list('warehouse_id', flat=True)
    return Allocation.objects.filter(location__zone__warehouse_id__in=wh_ids)
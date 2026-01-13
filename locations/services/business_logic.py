from django.core.exceptions import ValidationError
from users.models import WarehouseUserManagement

def get_manager_warehouse(user):
    """
    Helper to get the warehouse ID for a manager.
    """
    link = WarehouseUserManagement.objects.filter(user=user).first()
    if not link:
        raise ValidationError("Manager is not assigned to any warehouse.")
    return link.warehouse
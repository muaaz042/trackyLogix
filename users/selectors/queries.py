from users.models import User, Warehouse, WarehouseUserManagement, ClientProfile

def get_user_queryset(user):
    """
    Return the user object for the specific user (self-view).
    """
    return User.objects.filter(id=user.id)


def get_warehouses_for_user(user):
    """
    Return distinct warehouses linked to the user.
    """
    return Warehouse.objects.filter(
        warehouseusermanagement__user=user
    ).distinct()


def get_warehouse_user_links_for_user(user):
    """
    Return warehouse-user links based on role visibility.
    - Clients: See only their own link.
    - Admins/Managers: See all links for warehouses they belong to.
    """
    if user.role == "client":
        return WarehouseUserManagement.objects.filter(user=user)

    return WarehouseUserManagement.objects.filter(
        warehouse__warehouseusermanagement__user=user
    ).distinct()


def get_client_profile_queryset(user):
    """
    Return the client profile for the user.
    """
    return ClientProfile.objects.filter(user=user)
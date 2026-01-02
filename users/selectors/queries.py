from users.models import User, Warehouse, WarehouseUserManagement, ClientProfile

def get_user_queryset(user):
    return User.objects.filter(id=user.id)

def get_warehouses_for_user(user):
    return Warehouse.objects.filter(
        warehouseusermanagement__user=user
    ).distinct()

def get_warehouse_user_links_for_user(user):
    # 1. Admin: Sees ALL staff (Manager, DEO, Allocator, Self) in THEIR warehouses
    if user.role == "admin":
        # Step A: Find IDs of warehouses this Admin belongs to
        my_warehouse_ids = WarehouseUserManagement.objects.filter(
            user=user
        ).values_list('warehouse_id', flat=True)
        
        # Step B: Return all user links (including the admin themselves) for those warehouses
        return WarehouseUserManagement.objects.filter(
            warehouse_id__in=my_warehouse_ids
        )

    # 2. Manager: Sees DEOs and Allocators within their warehouses
    if user.role == "manager":
        my_warehouse_ids = WarehouseUserManagement.objects.filter(user=user).values_list('warehouse_id', flat=True)
        return WarehouseUserManagement.objects.filter(
            warehouse_id__in=my_warehouse_ids,
            user__role__in=['DEO', 'Allocator']
        )

    # 3. DEO / Allocator: Sees only their own attachment
    if user.role in ['DEO', 'Allocator']:
        return WarehouseUserManagement.objects.filter(user=user)

    return WarehouseUserManagement.objects.none()

def get_client_warehouse_links(user):
    if user.role == "client":
        return WarehouseUserManagement.objects.filter(user=user)
    return WarehouseUserManagement.objects.none()

def get_client_profile_queryset(user):
    return ClientProfile.objects.filter(user=user)
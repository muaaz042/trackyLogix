from rest_framework.exceptions import ValidationError
from django.db import transaction
from users.models import (
    WarehouseUserManagement,
    Subscription,
    User,
    Warehouse
)

# =====================================================
# ROLE RULES
# =====================================================

ROLE_CREATION_RULES = {
    "manager": ["admin"],
    "DEO": ["manager", "admin"],
    "Allocator": ["manager", "admin"],
}

def validate_user_creator(role: str, creator: User | None):
    """
    Ensure that only allowed roles can create other roles
    """
    if role in ROLE_CREATION_RULES:
        if not creator:
             raise ValidationError(f"A logged-in user (Manager/Admin) is required to create a {role}.")
        
        if creator.role not in ROLE_CREATION_RULES[role]:
            raise ValidationError(f"You ({creator.role}) are not allowed to create a {role}.")

def validate_subscription_limits(role: str, warehouse_id: int):
    """
    Enforce per-warehouse limits based on admin subscription
    """
    if role not in ["manager", "DEO", "Allocator"]:
        return

    # 1. Find the Admin responsible for this warehouse
    admin_link = (
        WarehouseUserManagement.objects
        .filter(warehouse_id=warehouse_id, user__role="admin")
        .select_related("user")
        .first()
    )
    
    if not admin_link:
        return 

    admin_user = admin_link.user

    # 2. Get Subscription
    try:
        subscription = Subscription.objects.get(user=admin_user)
    except Subscription.DoesNotExist:
        raise ValidationError(f"The Admin ({admin_user.email}) of this warehouse has no active subscription.")

    # 3. Define Limits
    limits = {
        "manager": subscription.max_managers_per_warehouse,
        "DEO": subscription.max_deos_per_warehouse,
        "Allocator": subscription.max_allocators_per_warehouse,
    }

    limit = limits.get(role, 0)

    # 4. Count EXISTING users of this role in this warehouse
    current_count = WarehouseUserManagement.objects.filter(
        warehouse_id=warehouse_id,
        user__role=role,
    ).count()

    if current_count >= limit:
        raise ValidationError(
            f"Cannot create {role}. Limit reached for this Warehouse"
            f"(Current: {current_count}, Max: {limit}). Please upgrade subscription."
        )

def validate_admin_can_add_warehouse(admin_user: User):
    try:
        subscription = Subscription.objects.get(user=admin_user)
    except Subscription.DoesNotExist:
        raise ValidationError("Admin has no subscription.")

    current_warehouse_count = WarehouseUserManagement.objects.filter(
        user=admin_user,
        warehouse__isnull=False
    ).values('warehouse').distinct().count()

    if current_warehouse_count >= subscription.max_warehouses:
        raise ValidationError(
            f"Admin has reached the maximum number of warehouses allowed ({subscription.max_warehouses})."
        )

# =====================================================
# CREATION SERVICES
# =====================================================

def create_user_with_validation(validated_data, creator=None, warehouse_data=None):
    """
    Handles user creation, enforces subscription limits, AND auto-links users to warehouses.
    """
    role = validated_data["role"]

    # 1. Permission Check
    validate_user_creator(role, creator)

    manager_warehouse_id = None

    # 2. PRE-CHECK: If Manager is creating, validate limits BEFORE writing to DB
    if creator and creator.role == 'manager' and role in ['DEO', 'Allocator']:
        # Find Manager's warehouse
        manager_link = WarehouseUserManagement.objects.filter(user=creator).first()
        
        if not manager_link:
            raise ValidationError("You (Manager) are not assigned to any warehouse, so you cannot add staff.")
        
        manager_warehouse_id = manager_link.warehouse.id
        
        # Check limits
        validate_subscription_limits(role, manager_warehouse_id)

    # 3. Create user and Auto-Link
    with transaction.atomic():
        # A. Create the User
        user = User.objects.create_user(**validated_data, created_by_user=creator)

        # B. If Created by Manager: Auto-link to Manager's Warehouse
        if manager_warehouse_id:
            warehouse = Warehouse.objects.get(id=manager_warehouse_id)
            WarehouseUserManagement.objects.create(warehouse=warehouse, user=user)

        # C. Admin Logic: Create Warehouse if needed
        if role == "admin" and warehouse_data:
            subscription = Subscription.objects.get(user=user)
            if subscription.max_warehouses < 1:
                 raise ValidationError("Subscription does not allow creating warehouses.")

            warehouse = Warehouse.objects.create(**warehouse_data)
            WarehouseUserManagement.objects.create(warehouse=warehouse, user=user)

    return user
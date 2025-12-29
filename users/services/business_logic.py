from django.core.exceptions import ValidationError
from users.models import (
    WarehouseUserManagement,
    Subscription,
    User,
    Warehouse, 
    ClientProfile
)

# =====================================================
# ROLE CREATION RULES
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
        if not creator or creator.role not in ROLE_CREATION_RULES[role]:
            raise ValidationError("You are not allowed to create this role.")

def get_admin_for_warehouse(warehouse_id: int) -> User:
    """
    Fetch the admin linked to a warehouse
    """
    link = (
        WarehouseUserManagement.objects
        .filter(warehouse_id=warehouse_id, user__role="admin")
        .select_related("user")
        .first()
    )
    if not link:
        raise ValidationError("Warehouse has no admin assigned, cannot verify limits.")
    return link.user

def validate_subscription_limits(role: str, warehouse_id: int):
    """
    Enforce per-warehouse limits based on admin subscription
    """
    if role not in ["manager", "DEO", "Allocator"]:
        return

    admin = get_admin_for_warehouse(warehouse_id)

    try:
        subscription = Subscription.objects.get(user=admin)
    except Subscription.DoesNotExist:
        raise ValidationError("Admin has no subscription.")

    limits = {
        "manager": subscription.max_managers_per_warehouse,
        "DEO": subscription.max_deos_per_warehouse,
        "Allocator": subscription.max_allocators_per_warehouse,
    }

    current_count = WarehouseUserManagement.objects.filter(
        warehouse_id=warehouse_id,
        user__role=role,
    ).count()

    if current_count >= limits.get(role, 0):
        raise ValidationError(f"Limit for {role} exceeded for this warehouse (Max: {limits.get(role)}).")

def validate_admin_can_add_warehouse(admin_user: User):
    """
    Enforce max_warehouses limit for admin
    """
    try:
        subscription = Subscription.objects.get(user=admin_user)
    except Subscription.DoesNotExist:
        raise ValidationError("Admin has no subscription.")

    current_warehouse_count = WarehouseUserManagement.objects.filter(
        user=admin_user
    ).count()

    if current_warehouse_count >= subscription.max_warehouses:
        raise ValidationError(
            f"Admin has reached the maximum number of warehouses allowed ({subscription.max_warehouses})."
        )

# =====================================================
# CREATION SERVICES
# =====================================================

def create_user_with_validation(validated_data, creator=None, warehouse_data=None):
    """
    Handles user creation and optional admin-warehouse creation.
    """
    role = validated_data["role"]

    # 1. Validate creator permission
    validate_user_creator(role, creator)

    # 2. Create user
    user = User.objects.create_user(**validated_data, created_by_user=creator)

    # 3. Admin: Logic for immediate warehouse creation
    if role == "admin" and warehouse_data:
        subscription = Subscription.objects.get(user=user)
        if subscription.max_warehouses < 1:
             raise ValidationError("Subscription does not allow creating warehouses.")

        warehouse = Warehouse.objects.create(**warehouse_data)
        WarehouseUserManagement.objects.create(warehouse=warehouse, user=user)

    return user


def create_warehouse_service(user, serializer):
    """
    Handles logic when an Admin manually creates a warehouse.
    Checks limits -> Saves Warehouse -> Links Admin.
    """
    if user.role != 'admin':
        raise ValidationError("Only admins can create warehouses.")

    # 1. Validate Limit
    validate_admin_can_add_warehouse(user)

    # 2. Save Warehouse
    warehouse = serializer.save()

    # 3. Create Link
    WarehouseUserManagement.objects.create(warehouse=warehouse, user=user)
    
    return warehouse
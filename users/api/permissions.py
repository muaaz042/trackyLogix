from rest_framework.permissions import BasePermission
from users.selectors.queries import get_warehouses_for_user


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user.role == "superadmin")


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user.role in ["admin"])


class IsManager(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user.role in ["manager"])


class IsClient(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user.role == "client")


class IsSelf(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.id == request.user.id


class IsSameWarehouse(BasePermission):
    """
    Checks if object belongs to one of the user's warehouses
    """
    def has_object_permission(self, request, view, obj):
        if request.user.role == "superadmin":
            return True
        user_warehouses = get_warehouses_for_user(request.user)
        return obj.warehouse_id in user_warehouses

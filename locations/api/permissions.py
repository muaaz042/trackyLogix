from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsLocationManager(BasePermission):
    """
    Manager: Full Access (Create, Update, Delete, Read)
    Allocator: Read Only
    Admin: Read Only
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Read permissions for Manager, Allocator, Admin
        if request.method in SAFE_METHODS:
            return request.user.role in ['manager', 'Allocator', 'admin']

        # Write permissions ONLY for Manager
        return request.user.role == 'manager'
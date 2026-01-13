from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsLocationManager(BasePermission):
    """
    Manager: Full Access
    Allocator/Admin: Read Only
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Read-only for Admin, Allocator
        if request.method in SAFE_METHODS:
            return request.user.role in ['manager', 'Allocator', 'admin']
        
        # Write for Manager
        return request.user.role == 'manager'
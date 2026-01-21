from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsLocationManager(BasePermission):
    """
    CRUD Permissions:
    Manager: Full Access (Create, Read, Update, Delete)
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

class IsLayoutViewer(BasePermission):
    """
    Strictly for the Warehouse Layout Visualization Endpoint.
    Allowed: Admin, Manager, Allocator
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Only these 3 roles can see the capacity map
        if request.user.role in ['admin', 'manager', 'Allocator']:
            return True
            
        return False
from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAllocator(BasePermission):
    """
    Allocator: Full Access
    Manager/Admin: Read Only
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.method in SAFE_METHODS:
            return request.user.role in ['Allocator', 'manager', 'admin']

        return request.user.role == 'Allocator'
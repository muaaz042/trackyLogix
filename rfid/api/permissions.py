from rest_framework.permissions import BasePermission, SAFE_METHODS

class RFIDPermission(BasePermission):
    """
    - DEO: Full Access (Create, Read, Update, Delete)
    - Manager: Read Only
    - Allocator: Read Only (Update Status handled via custom endpoint)
    - Client: Read Only
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
            
        # Write operations (POST, DELETE, PUT) -> DEO Only
        if request.method not in SAFE_METHODS:
             # Exception: Custom actions like 'update_status' handle their own permissions internally
             if view.action == 'update_status':
                 return True 
             return request.user.role == 'DEO'

        # Read operations -> All authenticated roles (filtered by queryset)
        return True
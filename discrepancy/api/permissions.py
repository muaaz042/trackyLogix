from rest_framework.permissions import BasePermission, SAFE_METHODS

class DiscrepancyPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Read permissions (GET) -> Manager, DEO, Admin
        if request.method in SAFE_METHODS:
            return request.user.role in ['DEO', 'manager', 'admin']

        # Write permissions (POST/Create) -> DEO Only
        return request.user.role == 'DEO'
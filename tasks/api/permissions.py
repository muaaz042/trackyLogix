from rest_framework.permissions import BasePermission

class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'manager'

class IsTaskParticipant(BasePermission):
    """
    Allows access to:
    1. Manager (who created it)
    2. DEO (assigned to it)
    3. Allocator (assigned to it)
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        if obj.assigned_by_user == user:
            return True
        if obj.assigned_to_deo == user:
            return True
        if obj.assigned_to_allocator == user:
            return True
        return False
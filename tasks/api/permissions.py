from rest_framework.permissions import BasePermission

class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'manager'

class IsTaskParticipant(BasePermission):
    """
    Allows access to Managers (creators) and Workers (assignees).
    """
    def has_object_permission(self, request, view, obj):
        # Manager who created it OR Worker assigned to it
        return obj.assigned_by_user == request.user or obj.assigned_to_user == request.user
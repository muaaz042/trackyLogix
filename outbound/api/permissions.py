from rest_framework.permissions import BasePermission, SAFE_METHODS
from tasks.models import Task

class IsClientOwner(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'client'

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'client':
            is_owner = obj.client.user == request.user
            if request.method not in SAFE_METHODS:
                return is_owner and obj.status == 'pending'
            return is_owner
        return False

class IsWarehouseManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'manager'
    def has_object_permission(self, request, view, obj):
        return request.user.role == 'manager'

class IsAssignedDEO(BasePermission):
    """
    Strictly for DEO actions (Scanning/Dispatching).
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'DEO'

    def has_object_permission(self, request, view, obj):
        # Check if there is an OUTBOUND task for this request assigned to this DEO
        return Task.objects.filter(
            task_type='outbound', 
            request_id=obj.id, 
            assigned_to_deo=request.user
        ).exists()

class IsAssignedAllocator(BasePermission):
    """
    Strictly for Allocator actions (Marking Exceptions).
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'Allocator'

    def has_object_permission(self, request, view, obj):
        # Check if there is an OUTBOUND task for this request assigned to this Allocator
        return Task.objects.filter(
            task_type='outbound', 
            request_id=obj.id, 
            assigned_to_allocator=request.user
        ).exists()
from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsClient(BasePermission):
    """
    Allows access only to users with role 'client'.
    For object-level actions, ensures the client owns the data.
    """
    def has_permission(self, request, view):
        # 1. Check if user is authenticated and is a client
        if not (request.user.is_authenticated and request.user.role == "client"):
            return False
        return True

    def has_object_permission(self, request, view, obj):
        # 2. Check ownership
        # If it's an InboundRequest, check client.user
        if hasattr(obj, 'client'): 
            return obj.client.user == request.user
        # If it's an InboundItem, check inbound_request.client.user
        elif hasattr(obj, 'inbound_request'): 
            return obj.inbound_request.client.user == request.user
        return False


class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "manager"


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "admin"


class ReadOnly(BasePermission):
    """
    Allows access only via safe methods (GET, HEAD, OPTIONS).
    """
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS
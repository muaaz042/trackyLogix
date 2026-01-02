from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsClient(BasePermission):
    def has_permission(self, request, view):
        if not (request.user.is_authenticated and request.user.role == "client"):
            return False
        return True

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'client'): 
            return obj.client.user == request.user
        elif hasattr(obj, 'inbound_request'): 
            return obj.inbound_request.client.user == request.user
        return False

class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "manager"

# ADDED: Permission for DEO
class IsDEO(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "DEO"
    
class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "admin"

class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS
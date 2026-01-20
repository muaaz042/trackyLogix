from rest_framework.permissions import BasePermission, SAFE_METHODS

class RFIDPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
            
        if request.method not in SAFE_METHODS:
             # Allow our custom actions
             if view.action in ['update_status', 'encode_item']:
                 return True 
             return request.user.role == 'DEO'

        return True
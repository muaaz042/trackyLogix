from inboundRequests.models import InboundRequest, InboundItem
from users.models import WarehouseUserManagement

def get_allowed_warehouses(user):
    return WarehouseUserManagement.objects.filter(user=user).values_list('warehouse_id', flat=True)


def get_inbound_requests_for_user(user, warehouse_filter=None):
    if user.role == "client":
        queryset = InboundRequest.objects.filter(client__user=user)
        if warehouse_filter:
            queryset = queryset.filter(warehouse_id=warehouse_filter)
        return queryset

    if user.role in ["manager", "admin", "DEO"]: # Added DEO if they need to see requests
        allowed_ids = get_allowed_warehouses(user)
        return InboundRequest.objects.filter(warehouse_id__in=allowed_ids)

    return InboundRequest.objects.none()


def get_inbound_items_for_user(user):
    if user.role == "client":
        return InboundItem.objects.filter(inbound_request__client__user=user)
    
    # CHANGED: Added DEO so they can see items to update
    if user.role in ["manager", "admin", "DEO"]:
        allowed_ids = get_allowed_warehouses(user)
        return InboundItem.objects.filter(inbound_request__warehouse_id__in=allowed_ids)
        
    return InboundItem.objects.none()
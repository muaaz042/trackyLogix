from outbound.models import OutboundRequest
from users.models import WarehouseUserManagement
from tasks.models import Task

def get_outbound_requests_for_user(user):
    """
    Returns the queryset of OutboundRequests visible to the specific user.
    """
    if user.role == 'admin':
        return OutboundRequest.objects.all()

    if user.role == 'client':
        return OutboundRequest.objects.filter(client__user=user)

    if user.role == 'manager':
        wh_ids = WarehouseUserManagement.objects.filter(user=user).values_list('warehouse_id', flat=True)
        return OutboundRequest.objects.filter(warehouse_id__in=wh_ids)

    if user.role == 'DEO':
        # Get request IDs where user is assigned as DEO in Tasks
        task_req_ids = Task.objects.filter(
            task_type='outbound', 
            assigned_to_deo=user
        ).values_list('request_id', flat=True)
        return OutboundRequest.objects.filter(id__in=task_req_ids)

    if user.role == 'Allocator':
        # Get request IDs where user is assigned as Allocator in Tasks
        task_req_ids = Task.objects.filter(
            task_type='outbound', 
            assigned_to_allocator=user
        ).values_list('request_id', flat=True)
        return OutboundRequest.objects.filter(id__in=task_req_ids)

    return OutboundRequest.objects.none()
from rest_framework.exceptions import ValidationError, PermissionDenied
from inboundRequests.models import InboundRequest, InboundItem
from users.models import ClientProfile

# --- VALIDATION & UTILS ---

def get_client_profile_or_fail(client_profile_id, user):
    try:
        profile = ClientProfile.objects.get(id=client_profile_id, user=user)
    except ClientProfile.DoesNotExist:
        raise ValidationError({"client_profile_id": "Invalid Client Profile ID or you do not own this profile."})
    return profile


def validate_request_modification(inbound_request: InboundRequest):
    """
    Clients cannot modify requests ONLY if they are approved.
    """
    if inbound_request.status == 'approved':
        raise PermissionDenied(detail="You cannot modify this request because it has already been approved.")


def get_and_validate_request_for_item_creation(request_id, user):
    """
    Retrieves the request and checks if the client owns it and if it's modifiable.
    """
    if not request_id:
        raise ValidationError({"inbound_request": "This field is required."})

    try:
        req = InboundRequest.objects.get(id=request_id)
        # Strict ownership check
        if req.client.user != user:
            raise PermissionDenied("You do not own this inbound request.")
        
        validate_request_modification(req)
        return req
    except InboundRequest.DoesNotExist:
        raise ValidationError("Invalid Request ID.")


# --- MANAGER ACTIONS ---

def manager_update_request_status(request_obj: InboundRequest, status: str, manager_user):
    if status not in ['pending', 'approved', 'rejected']:
        raise ValidationError(f"Invalid status: {status}")
    
    request_obj.status = status
    if status == 'approved':
        request_obj.approved_by_user = manager_user
    elif status == 'pending':
        request_obj.approved_by_user = None
        
    request_obj.save(update_fields=["status", "approved_by_user"])


def manager_update_item_status(item: InboundItem, status: str):
    allowed = ['pending', 'not arrived yet', 'arrived']
    if status not in allowed:
        raise ValidationError(f"Invalid item status: {status}")

    item.item_status = status
    item.save(update_fields=["item_status"])
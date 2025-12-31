from rest_framework.exceptions import ValidationError, PermissionDenied
from rfid.models import RFIDTag
from users.models import ClientProfile
from inboundRequests.models import InboundRequest

def validate_rfid_creation(user, data):
    """
    Validates that the user is a DEO and that the linked data matches.
    """
    if user.role != 'DEO':
        raise PermissionDenied("Only DEOs can create (encode) RFID tags.")
    
    inbound_request = data.get('inbound_request')
    client = data.get('client')

    if inbound_request.client != client:
        raise ValidationError("The Inbound Request does not belong to the specified Client.")

def create_rfid_tag_service(user, validated_data):
    """
    Service to create an RFID tag.
    """
    validate_rfid_creation(user, validated_data)
    
    # REMOVED: created_by_user=user from arguments
    tag = RFIDTag.objects.create(
        **validated_data
    )
    return tag

def update_rfid_status_service(tag, status, user):
    """
    Service to update RFID status.
    """
    if user.role not in ['Allocator', 'DEO', 'manager']:
        raise PermissionDenied("You do not have permission to update RFID status.")

    tag.status = status
    tag.save(update_fields=['status', 'updated_at'])
    return tag
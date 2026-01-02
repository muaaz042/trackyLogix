from rest_framework.exceptions import ValidationError, PermissionDenied
from rfid.models import RFIDTag

def validate_rfid_creation(user, data):
    """
    Validates that the user is a DEO.
    """
    if user.role != 'DEO':
        raise PermissionDenied("Only DEOs can create (encode) RFID tags.")

def create_rfid_tag_service(user, validated_data):
    """
    Service to create an RFID tag.
    """
    validate_rfid_creation(user, validated_data)
    
    # Just create it. The 'inbound_item' is already validated by the serializer.
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
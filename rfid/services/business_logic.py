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


def encode_rfid_tag_service(tag, new_epc):
    """
    Updates the EPC of a tag and automatically sets status to 'encoded'.
    """
    # 1. Check for Uniqueness manually to return clean error message
    if RFIDTag.objects.filter(epc=new_epc).exclude(id=tag.id).exists():
        raise ValidationError(f"The EPC '{new_epc}' is already assigned to another tag.")

    # 2. Update Fields
    tag.epc = new_epc
    tag.status = 'encoded' # Automagical update
    
    tag.save()
    return tag
from django.db import transaction
from django.core.exceptions import ValidationError
from allocations.models import Allocation

def create_allocation_service(validated_data):
    """
    Handles hierarchy calculation and atomic creation of allocation + RFID status update.
    """
    rfid = validated_data.get('rfid')
    
    # 1. Validation: Ensure RFID isn't already allocated (Double check outside serializer)
    if hasattr(rfid, 'allocation'):
        raise ValidationError(f"RFID {rfid.epc} is already allocated.")

    # 2. Extract inputs
    bin_obj = validated_data.get('bin')
    level_obj = validated_data.get('level')
    location_obj = validated_data.get('location')

    # 3. Hierarchy Auto-Fill Logic
    if bin_obj:
        # Bin Storage: Auto-fill everything upwards
        validated_data['level'] = bin_obj.level
        validated_data['rack'] = bin_obj.level.rack
        validated_data['aisle'] = bin_obj.level.rack.aisle
        validated_data['location'] = bin_obj.level.rack.aisle.location
    
    elif level_obj:
        # Level Storage (e.g., Pallet on Rack): Auto-fill upwards, clear bin
        validated_data['rack'] = level_obj.rack
        validated_data['aisle'] = level_obj.rack.aisle
        validated_data['location'] = level_obj.rack.aisle.location
        validated_data['bin'] = None
    
    elif location_obj:
        # Floor Storage: Only location exists, clear deeper hierarchy
        validated_data['aisle'] = None
        validated_data['rack'] = None
        validated_data['level'] = None
        validated_data['bin'] = None
    
    else:
        # Failsafe if serializer didn't catch it
        raise ValidationError("An allocation must specify at least a Location, Level, or Bin.")

    # 4. Atomic Save & Status Update
    with transaction.atomic():
        allocation = Allocation.objects.create(**validated_data)
        
        # Update RFID status
        rfid.status = 'allocated'
        rfid.save(update_fields=['status'])

    return allocation

def delete_allocation_service(allocation_instance):
    """
    Deletes allocation and reverts RFID status.
    """
    rfid = allocation_instance.rfid
    
    with transaction.atomic():
        # Revert RFID Status
        rfid.status = 'encoded' 
        rfid.save(update_fields=['status'])
        
        # Delete Record
        allocation_instance.delete()
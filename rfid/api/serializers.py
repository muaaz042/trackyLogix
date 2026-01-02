from rest_framework import serializers
from rfid.models import RFIDTag
from inboundRequests.models import InboundItem

class RFIDTagSerializer(serializers.ModelSerializer):
    # Input: ID of the Inbound Item
    inbound_item_id = serializers.PrimaryKeyRelatedField(
        queryset=InboundItem.objects.all(), 
        source='inbound_item', 
        write_only=True
    )

    # Output: String representation of the item
    inbound_item_details = serializers.StringRelatedField(source='inbound_item', read_only=True)
    
    # Output: Fetch SKU from the related InboundItem
    sku = serializers.CharField(source='inbound_item.sku', read_only=True)

    class Meta:
        model = RFIDTag
        fields = [
            'id', 
            'epc', 
            'status', 
            'inbound_item_id', 
            'inbound_item_details', 
            'sku', 
            'created_at', 
            'updated_at'
        ]
        # CHANGE: Removed 'epc' from here so you can update/encode it.
        # Only system timestamps and derived fields should be read-only.
        read_only_fields = ['created_at', 'updated_at', 'sku', 'inbound_item_details']


class RFIDStatusSerializer(serializers.Serializer):
    """
    Serializer specifically for updating the status of an RFID tag.
    """
    status = serializers.ChoiceField(choices=RFIDTag.STATUS_CHOICES)
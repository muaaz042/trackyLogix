from rest_framework import serializers
from rfid.models import RFIDTag
from inboundRequests.models import InboundItem

class RFIDTagSerializer(serializers.ModelSerializer):
    inbound_item_id = serializers.PrimaryKeyRelatedField(
        queryset=InboundItem.objects.all(), 
        source='inbound_item', 
        write_only=True
    )
    inbound_item_details = serializers.StringRelatedField(source='inbound_item', read_only=True)
    sku = serializers.CharField(source='inbound_item.sku', read_only=True)

    class Meta:
        model = RFIDTag
        fields = [
            'id', 'epc', 'status', 'inbound_item_id', 
            'inbound_item_details', 'sku', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'sku', 'inbound_item_details']


class RFIDStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=RFIDTag.STATUS_CHOICES)


# --- NEW SERIALIZER ---
class RFIDEncodeSerializer(serializers.Serializer):
    epc = serializers.CharField(max_length=255, required=True)

    def validate_epc(self, value):
        # Optional: Add custom format validation here (e.g., length check)
        if len(value) < 3:
            raise serializers.ValidationError("EPC is too short.")
        return value    
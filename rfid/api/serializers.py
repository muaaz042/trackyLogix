from rest_framework import serializers
from rfid.models import RFIDTag
from inboundRequests.models import InboundRequest
from users.models import ClientProfile, Warehouse

class RFIDTagSerializer(serializers.ModelSerializer):
    # Inputs (IDs)
    client_id = serializers.PrimaryKeyRelatedField(
        queryset=ClientProfile.objects.all(), 
        source='client'
    )
    warehouse_id = serializers.PrimaryKeyRelatedField(
        queryset=Warehouse.objects.all(), 
        source='warehouse',
        required=False,
        allow_null=True
    )
    inbound_request_id = serializers.PrimaryKeyRelatedField(
        queryset=InboundRequest.objects.all(), 
        source='inbound_request'
    )

    # Outputs
    client_email = serializers.EmailField(source='client.user.email', read_only=True)
    inbound_request_details = serializers.SerializerMethodField()
    # REMOVED: created_by field

    class Meta:
        model = RFIDTag
        fields = [
            'id', 'epc', 'sku', 'batch_or_lot_no', 'status',
            'client_id', 'client_email',
            'warehouse_id',
            'inbound_request_id', 'inbound_request_details',
            'created_at', 'updated_at' # Removed 'created_by'
        ]
        read_only_fields = ['status', 'created_at', 'updated_at', 'inbound_request_details', 'client_email']

    def get_inbound_request_details(self, obj):
        return f"Req #{obj.inbound_request.id}"


class RFIDStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=RFIDTag.STATUS_CHOICES)
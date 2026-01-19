from rest_framework import serializers
from outbound.models import OutboundRequest, OutboundItem
from users.models import Warehouse, User

class OutboundItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OutboundItem
        fields = [
            'id', 'sku', 'requested_quantity', 
            'dispatched_quantity', 'item_status', 'remarks'
        ]
        read_only_fields = ['dispatched_quantity', 'item_status']

class OutboundRequestSerializer(serializers.ModelSerializer):
    items = OutboundItemSerializer(many=True)
    client_name = serializers.CharField(source='client.user.email', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    warehouse_id = serializers.PrimaryKeyRelatedField(
        queryset=Warehouse.objects.all(), source='warehouse', write_only=True
    )

    class Meta:
        model = OutboundRequest
        fields = [
            'id', 'client_name', 'warehouse_id', 'warehouse_name',
            'order_type', 'external_order_number',
            'customer_name', 'customer_phone', 'destination_address',
            'expected_dispatch_date', 'courier_name', 'tracking_number',
            'status', 'items', 'created_at'
        ]
        read_only_fields = ['status', 'approved_by_user', 'created_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        user = self.context['request'].user
        from outbound.services.business_logic import create_outbound_request_service
        return create_outbound_request_service(user, validated_data, items_data)

class ManagerApprovalSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=['approved', 'rejected'])

class DEODispatchScanSerializer(serializers.Serializer):
    epc = serializers.CharField(required=True)

# CHANGED: Renamed and added item_id
class AllocatorExceptionSerializer(serializers.Serializer):
    item_id = serializers.IntegerField(required=True)
    item_status = serializers.ChoiceField(choices=['missing', 'damaged'])
    remarks = serializers.CharField(required=True)
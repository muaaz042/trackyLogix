from rest_framework import serializers
from inboundRequests.models import InboundRequest, InboundItem
from users.models import Warehouse

class InboundItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InboundItem
        fields = [
            'id', 
            'inbound_request', 
            'name', 
            'sku', 
            'quantity', 
            'remaining_quantity', # <--- ADDED HERE
            'weight', 
            'dimensions',
            'expected_arrival_date',
            'temp_range',
            'unit_type',
            'fragile',
            'hazardous',
            'total_inventory_value',
            'humidity_range',
            'batch_or_lot_no',
            'expiry_date',
            'item_status', 
            'created_at', 
            'updated_at'
        ]
        # It's read-only because it's auto-calculated/managed by the system
        read_only_fields = ['remaining_quantity', 'item_status', 'created_at', 'updated_at']


class InboundRequestSerializer(serializers.ModelSerializer):
    items = InboundItemSerializer(many=True, read_only=True)
    client_email = serializers.EmailField(source='client.user.email', read_only=True)
    warehouse_id = serializers.PrimaryKeyRelatedField(
        queryset=Warehouse.objects.all(), source='warehouse', write_only=True
    )
    warehouse_details = serializers.StringRelatedField(source='warehouse', read_only=True)

    class Meta:
        model = InboundRequest
        fields = [
            'id', 
            'client_email',
            'warehouse_id', 
            'warehouse_details',
            'expected_arrival_date', 
            'status', 
            'items', 
            'created_at', 
            'updated_at'
        ]
        read_only_fields = ['status', 'client_email', 'warehouse_details', 'created_at', 'updated_at']

# Manager Status serializers
class ManagerRequestStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=InboundRequest.STATUS_CHOICES)

# DEO Status Serializer
class DEOItemStatusSerializer(serializers.Serializer):
    item_status = serializers.ChoiceField(choices=InboundItem.ITEM_STATUS_CHOICES)
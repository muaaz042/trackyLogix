from rest_framework import serializers
from discrepancy.models import Discrepancy
from inboundRequests.models import InboundItem

class DiscrepancySerializer(serializers.ModelSerializer):
    inbound_item_id = serializers.PrimaryKeyRelatedField(
        queryset=InboundItem.objects.all(),
        source='inbound_item'
    )

    inbound_item_details = serializers.StringRelatedField(source='inbound_item', read_only=True)
    reported_by = serializers.StringRelatedField(source='reported_by_user', read_only=True)

    class Meta:
        model = Discrepancy
        fields = [
            'id', 
            'inbound_item_id', 
            'inbound_item_details',
            'quantity_expected', 
            'quantity_found', 
            'damage_found', 
            'note', 
            'photo',    
            'reported_by', 
            'created_at', 
            'updated_at'
        ]
        read_only_fields = ['reported_by', 'created_at', 'updated_at', 'inbound_item_details']
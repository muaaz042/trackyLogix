from rest_framework import serializers
from allocations.models import Allocation
from rfid.models import RFIDTag
from locations.models import Location, Level, Bin


class AllocationSerializer(serializers.ModelSerializer):
    rfid_id = serializers.PrimaryKeyRelatedField(
        queryset=RFIDTag.objects.all(), source='rfid', write_only=True
    )
    location_id = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(), source='location', required=False, allow_null=True, write_only=True
    )
    bin_id = serializers.PrimaryKeyRelatedField(
        queryset=Bin.objects.all(), source='bin', required=False, allow_null=True, write_only=True
    )
    level_id = serializers.PrimaryKeyRelatedField(
        queryset=Level.objects.all(), source='level', required=False, allow_null=True, write_only=True
    )

    rfid_epc = serializers.CharField(source='rfid.epc', read_only=True)
    location_code = serializers.CharField(source='location.name', read_only=True)
    full_path = serializers.SerializerMethodField()

    class Meta:
        model = Allocation
        fields = [
            'id', 'rfid_id', 'rfid_epc',
            'location_id', 'location_code', 'bin_id', 'level_id',
            'full_path', 'allocated_at'
        ]
        read_only_fields = ['allocated_at', 'full_path', 'rfid_epc', 'location_code']

    def validate(self, data):
        if not (data.get('location') or data.get('level') or data.get('bin')):
            raise serializers.ValidationError("You must select a Location, Level, or Bin.")
        return data

    def get_full_path(self, obj):
        # This is for the CRUD endpoint simple display
        parts = []
        if obj.location: parts.append(obj.location.name)
        if obj.aisle: parts.append(obj.aisle.name)
        if obj.rack: parts.append(obj.rack.name)
        if obj.level: parts.append(obj.level.name)
        if obj.bin: parts.append(obj.bin.name)
        return " > ".join(parts)


class EPCLookupRequestSerializer(serializers.Serializer):
    epcs = serializers.ListField(
        child=serializers.CharField(),
        allow_empty=False,
        help_text="List of EPC strings to search for."
    )

class SKULookupRequestSerializer(serializers.Serializer):
    skus = serializers.ListField(
        child=serializers.CharField(),
        allow_empty=False,
        help_text="List of SKUs to search for."
    )


class AllocationDetailsSerializer(serializers.ModelSerializer):
    """
    Rich serializer for Lookup Endpoints.
    """
    # 1. Basic Identifiers
    epc = serializers.CharField(source='rfid.epc')
    sku = serializers.CharField(source='rfid.inbound_item.sku', default="N/A")
    item_name = serializers.CharField(source='rfid.inbound_item.name', default="N/A")

    # 2. Detailed Inbound Item Data
    quantity = serializers.IntegerField(source='rfid.inbound_item.quantity', default=0)
    remaining_quantity = serializers.IntegerField(source='rfid.inbound_item.remaining_quantity', default=0)
    weight = serializers.DecimalField(source='rfid.inbound_item.weight', max_digits=10, decimal_places=2, default=0.00)
    dimensions = serializers.CharField(source='rfid.inbound_item.dimensions', default="N/A")
    unit_type = serializers.CharField(source='rfid.inbound_item.unit_type', default="N/A")
    temp_range = serializers.CharField(source='rfid.inbound_item.temp_range', default="N/A")
    humidity_range = serializers.CharField(source='rfid.inbound_item.humidity_range', default="N/A")
    fragile = serializers.BooleanField(source='rfid.inbound_item.fragile', default=False)
    hazardous = serializers.BooleanField(source='rfid.inbound_item.hazardous', default=False)
    batch_no = serializers.CharField(source='rfid.inbound_item.batch_or_lot_no', default="N/A")
    expiry_date = serializers.DateField(source='rfid.inbound_item.expiry_date', allow_null=True)
    inbound_status = serializers.CharField(source='rfid.inbound_item.item_status', default="N/A")
    
    # 3. Consolidated Location Field
    full_location = serializers.SerializerMethodField()

    class Meta:
        model = Allocation
        fields = [
            'id', 
            'epc', 'sku', 'item_name',
            'quantity', 'remaining_quantity', 'weight', 'dimensions',
            'unit_type', 'temp_range', 'humidity_range',
            'fragile', 'hazardous', 'batch_no', 'expiry_date', 'inbound_status',
            'full_location',
            'allocated_at'
        ]

    def get_full_location(self, obj):
        # Reuse this logic in the new serializer or duplicate it
        return self._build_location_string(obj)

    def _build_location_string(self, obj):
        parts = []
        if obj.location:
            if obj.location.zone:
                if obj.location.zone.warehouse:
                    parts.append(obj.location.zone.warehouse.name)
                parts.append(obj.location.zone.name)
            parts.append(obj.location.name)
            
        if obj.aisle: parts.append(obj.aisle.name)
        if obj.rack: parts.append(obj.rack.name)
        if obj.level: parts.append(obj.level.name)
        if obj.bin: parts.append(obj.bin.name)
            
        return " > ".join(parts) if parts else "Unassigned Location"

# --- NEW: SIMPLIFIED SERIALIZER (For SKU Lookup) ---
class SKULocationSerializer(serializers.ModelSerializer):
    """
    Returns ONLY SKU, EPC, and Full Location.
    """
    epc = serializers.CharField(source='rfid.epc')
    sku = serializers.CharField(source='rfid.inbound_item.sku')
    full_location = serializers.SerializerMethodField()

    class Meta:
        model = Allocation
        fields = ['sku', 'epc', 'full_location']

    def get_full_location(self, obj):
        parts = []
        if obj.location:
            if obj.location.zone:
                if obj.location.zone.warehouse:
                    parts.append(obj.location.zone.warehouse.name)
                parts.append(obj.location.zone.name)
            parts.append(obj.location.name)
            
        if obj.aisle: parts.append(obj.aisle.name)
        if obj.rack: parts.append(obj.rack.name)
        if obj.level: parts.append(obj.level.name)
        if obj.bin: parts.append(obj.bin.name)
            
        return " > ".join(parts) if parts else "Unassigned Location"
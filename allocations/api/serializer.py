from rest_framework import serializers
from allocations.models import Allocation
from rfid.models import RFIDTag
from locations.models import Location, Level, Bin

# --- Standard CRUD Serializer (Keep as is) ---
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

# --- EPC LOOKUP SERIALIZERS ---

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

# --- FULL DETAILS (For EPC Lookup) ---
class AllocationDetailsSerializer(serializers.ModelSerializer):
    # ... [Keep existing implementation for EPC lookup] ...
    # (This one keeps all the details like weight, dimensions, etc.)
    epc = serializers.CharField(source='rfid.epc')
    sku = serializers.CharField(source='rfid.inbound_item.sku', default="N/A")
    # ... (other fields omitted for brevity, keep your existing code here) ...
    full_location = serializers.SerializerMethodField()

    class Meta:
        model = Allocation
        fields = [
            'id', 'epc', 'sku', 'item_name', 
            'quantity', 'remaining_quantity', 'full_location', 'allocated_at' 
            # ... add back all fields you had before for EPC lookup ...
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
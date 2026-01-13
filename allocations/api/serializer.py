from rest_framework import serializers
from allocations.models import Allocation
from rfid.models import RFIDTag
from locations.models import Location, Level, Bin

class AllocationSerializer(serializers.ModelSerializer):
    # Inputs: IDs (Write Only)
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

    # Outputs: Details (Read Only)
    rfid_epc = serializers.CharField(source='rfid.epc', read_only=True)
    location_code = serializers.CharField(source='location.name', read_only=True)
    full_path = serializers.SerializerMethodField()

    class Meta:
        model = Allocation
        fields = [
            'id', 
            'rfid_id', 'rfid_epc',
            'location_id', 'location_code',
            'bin_id', 'level_id',
            'full_path',
            'allocated_at'
        ]
        read_only_fields = ['allocated_at', 'full_path', 'rfid_epc', 'location_code']

    def validate(self, data):
        """
        Ensure at least one storage target is provided.
        """
        if not (data.get('location') or data.get('level') or data.get('bin')):
            raise serializers.ValidationError("You must select a Location, Level, or Bin.")
        return data

    def get_full_path(self, obj):
        parts = []
        if obj.location: parts.append(obj.location.name)
        if obj.aisle: parts.append(obj.aisle.name)
        if obj.rack: parts.append(obj.rack.name)
        if obj.level: parts.append(obj.level.name)
        if obj.bin: parts.append(obj.bin.name)
        return " > ".join(parts)
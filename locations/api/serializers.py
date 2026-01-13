from rest_framework import serializers
from locations.models import Zone, Aisle, Rack, Level, Bin, Location

class ZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zone
        fields = '__all__'
        read_only_fields = ['warehouse'] # Warehouse is set automatically

class AisleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aisle
        fields = '__all__'

class RackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rack
        fields = '__all__'

class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = '__all__'

class BinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bin
        fields = '__all__'

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = [
            'id', 'warehouse', 'zone', 'level', 'bin', 
            'location_code', 'location_type'
        ]
        read_only_fields = ['warehouse', 'location_code'] # Auto-generated

    def validate(self, data):
        """
        Check that at least one of zone, level, or bin is provided.
        """
        has_zone = data.get('zone') is not None
        has_level = data.get('level') is not None
        has_bin = data.get('bin') is not None
        
        # Also check instance values if doing a partial update
        if self.instance:
            has_zone = has_zone or self.instance.zone is not None
            has_level = has_level or self.instance.level is not None
            has_bin = has_bin or self.instance.bin is not None

        if not (has_zone or has_level or has_bin):
            raise serializers.ValidationError("A location must be linked to a Zone, Level, or Bin.")
        return data
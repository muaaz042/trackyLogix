from rest_framework import serializers
from locations.models import Zone, Location, Aisle, Rack, Level, Bin

# --- Standard CRUD Serializers ---

class ZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zone
        fields = '__all__'
        read_only_fields = ['warehouse']

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'

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


# --- NESTED LAYOUT SERIALIZERS (For Visualization) ---

class BinLayoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bin
        fields = ['id', 'name', 'status', 'max_units', 'max_weight']

class LevelLayoutSerializer(serializers.ModelSerializer):
    bins = BinLayoutSerializer(many=True, read_only=True)
    class Meta:
        model = Level
        fields = ['id', 'name', 'status', 'max_weight', 'bins']

class RackLayoutSerializer(serializers.ModelSerializer):
    levels = LevelLayoutSerializer(many=True, read_only=True)
    class Meta:
        model = Rack
        fields = ['id', 'name', 'status', 'rack_type', 'max_weight', 'levels']

class AisleLayoutSerializer(serializers.ModelSerializer):
    racks = RackLayoutSerializer(many=True, read_only=True)
    class Meta:
        model = Aisle
        fields = ['id', 'name', 'status', 'racks']

class LocationLayoutSerializer(serializers.ModelSerializer):
    aisles = AisleLayoutSerializer(many=True, read_only=True)
    class Meta:
        model = Location
        fields = ['id', 'name', 'status', 'location_type', 'min_temp', 'max_temp', 'aisles']

class ZoneLayoutSerializer(serializers.ModelSerializer):
    locations = LocationLayoutSerializer(many=True, read_only=True)
    class Meta:
        model = Zone
        fields = ['id', 'name', 'zone_type', 'locations']
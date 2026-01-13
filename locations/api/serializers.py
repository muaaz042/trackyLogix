from rest_framework import serializers
from locations.models import Zone, Location, Aisle, Rack, Level, Bin

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
from rest_framework.viewsets import ModelViewSet
from locations.models import Zone, Location, Aisle, Rack, Level, Bin
from .serializers import (
    ZoneSerializer, LocationSerializer, AisleSerializer, 
    RackSerializer, LevelSerializer, BinSerializer
)
from .permissions import IsLocationManager
from locations.selectors.queries import (
    get_zones_for_user, get_locations_for_user,
    get_aisles_for_user, get_racks_for_user, 
    get_levels_for_user, get_bins_for_user
)
from locations.services.business_logic import get_manager_warehouse

class BaseLocationViewSet(ModelViewSet):
    permission_classes = [IsLocationManager]

class ZoneViewSet(BaseLocationViewSet):
    serializer_class = ZoneSerializer
    def get_queryset(self): 
        return get_zones_for_user(self.request.user)
    
    def perform_create(self, serializer):
        # Auto-link warehouse for Zones
        warehouse = get_manager_warehouse(self.request.user)
        serializer.save(warehouse=warehouse)

class LocationViewSet(BaseLocationViewSet):
    serializer_class = LocationSerializer
    def get_queryset(self): 
        return get_locations_for_user(self.request.user)

class AisleViewSet(BaseLocationViewSet):
    serializer_class = AisleSerializer
    def get_queryset(self): 
        return get_aisles_for_user(self.request.user)

class RackViewSet(BaseLocationViewSet):
    serializer_class = RackSerializer
    def get_queryset(self): 
        return get_racks_for_user(self.request.user)

class LevelViewSet(BaseLocationViewSet):
    serializer_class = LevelSerializer
    def get_queryset(self): 
        return get_levels_for_user(self.request.user)

class BinViewSet(BaseLocationViewSet):
    serializer_class = BinSerializer
    def get_queryset(self): 
        return get_bins_for_user(self.request.user)
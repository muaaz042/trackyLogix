from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import ValidationError
from locations.models import Zone, Aisle, Rack, Level, Bin, Location
from .serializers import (
    ZoneSerializer, AisleSerializer, RackSerializer, 
    LevelSerializer, BinSerializer, LocationSerializer
)
from .permissions import IsLocationManager
from locations.selectors.queries import (
    get_zones_for_user, get_locations_for_user,
    get_aisles_for_user, get_racks_for_user, 
    get_levels_for_user, get_bins_for_user
)
from locations.services.business_logic import (
    get_manager_warehouse, 
    create_or_update_location_service
)

class BaseLocationViewSet(ModelViewSet):
    permission_classes = [IsLocationManager]

class ZoneViewSet(BaseLocationViewSet):
    serializer_class = ZoneSerializer

    def get_queryset(self):
        return get_zones_for_user(self.request.user)

    def perform_create(self, serializer):
        # Auto-assign warehouse from manager
        warehouse = get_manager_warehouse(self.request.user)
        serializer.save(warehouse=warehouse)

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

class LocationViewSet(BaseLocationViewSet):
    serializer_class = LocationSerializer

    def get_queryset(self):
        return get_locations_for_user(self.request.user)

    def perform_create(self, serializer):
        warehouse = get_manager_warehouse(self.request.user)
        # We pass the warehouse to save, but actual logic is in service
        # We use serializer.save() to create the instance first but incomplete
        # Actually, simpler to use the service pattern:
        
        instance = serializer.save(warehouse=warehouse)
        # Recalculate code
        create_or_update_location_service(instance, {})

    def perform_update(self, serializer):
        instance = serializer.save()
        # Recalculate code if hierarchy changed
        create_or_update_location_service(instance, {})
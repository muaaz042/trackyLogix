from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated

from locations.models import Zone, Location, Aisle, Rack, Level, Bin
from .serializers import (
    ZoneSerializer, LocationSerializer, AisleSerializer, 
    RackSerializer, LevelSerializer, BinSerializer,
    ZoneLayoutSerializer # Import the new layout serializer
)
from .permissions import IsLocationManager, IsLayoutViewer
from locations.selectors.queries import (
    get_zones_for_user, get_locations_for_user,
    get_aisles_for_user, get_racks_for_user, 
    get_levels_for_user, get_bins_for_user
)
from locations.services.business_logic import get_manager_warehouse

# --- Standard CRUD ViewSets ---

class BaseLocationViewSet(ModelViewSet):
    permission_classes = [IsLocationManager]

class ZoneViewSet(BaseLocationViewSet):
    serializer_class = ZoneSerializer
    def get_queryset(self): 
        return get_zones_for_user(self.request.user)
    
    def perform_create(self, serializer):
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

# --- VISUALIZATION ENDPOINT ---

class WarehouseLayoutViewSet(ReadOnlyModelViewSet):
    """
    Returns a deeply nested structure of the warehouse for visualization.
    Only accessible by Admin, Manager, and Allocator.
    """
    serializer_class = ZoneLayoutSerializer
    permission_classes = [IsLayoutViewer]

    def get_queryset(self):
        # reuse the selector logic to respect warehouse permissions
        queryset = get_zones_for_user(self.request.user)
        
        # Optimization: Fetch the whole tree in 1-2 queries instead of hundreds
        return queryset.prefetch_related(
            'locations',
            'locations__aisles',
            'locations__aisles__racks',
            'locations__aisles__racks__levels',
            'locations__aisles__racks__levels__bins'
        )
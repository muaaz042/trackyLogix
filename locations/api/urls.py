from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ZoneViewSet, LocationViewSet, AisleViewSet, 
    RackViewSet, LevelViewSet, BinViewSet,
    WarehouseLayoutViewSet
)

router = DefaultRouter()
router.register('zones', ZoneViewSet, basename='zones')
router.register('locations', LocationViewSet, basename='locations')
router.register('aisles', AisleViewSet, basename='aisles')
router.register('racks', RackViewSet, basename='racks')
router.register('levels', LevelViewSet, basename='levels')
router.register('bins', BinViewSet, basename='bins')

# The visualization endpoint
router.register('warehouse-layout', WarehouseLayoutViewSet, basename='warehouse-layout')

urlpatterns = [
    path('', include(router.urls)),
]
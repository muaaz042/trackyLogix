from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ZoneViewSet, AisleViewSet, RackViewSet, 
    LevelViewSet, BinViewSet, LocationViewSet
)

router = DefaultRouter()
router.register('zones', ZoneViewSet, basename='zones')
router.register('aisles', AisleViewSet, basename='aisles')
router.register('racks', RackViewSet, basename='racks')
router.register('levels', LevelViewSet, basename='levels')
router.register('bins', BinViewSet, basename='bins')
router.register('locations', LocationViewSet, basename='locations')

urlpatterns = [
    path('', include(router.urls)),
]
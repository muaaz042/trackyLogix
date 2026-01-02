from rest_framework.routers import DefaultRouter
from django.urls import path, include
from discrepancy.api.views import DiscrepancyViewSet

router = DefaultRouter()
router.register('discrepancy', DiscrepancyViewSet, basename='discrepancy-reports')

urlpatterns = [
    path('', include(router.urls)),
]
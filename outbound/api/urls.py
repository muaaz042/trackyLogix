from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OutboundRequestViewSet

router = DefaultRouter()
router.register('outbound-requests', OutboundRequestViewSet, basename='outbound-requests')

urlpatterns = [
    path('', include(router.urls)),
]
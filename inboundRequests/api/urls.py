from rest_framework.routers import DefaultRouter
from django.urls import path, include
from inboundRequests.api.views import (
    InboundRequestViewSet,
    InboundItemViewSet
)

router = DefaultRouter()
router.register("inbound-requests", InboundRequestViewSet, basename="inbound-requests")
router.register("inbound-items", InboundItemViewSet, basename="inbound-items")

urlpatterns = [
    path('', include(router.urls)),
]
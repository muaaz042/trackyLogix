from rest_framework.routers import DefaultRouter
from django.urls import path, include
from rfid.api.views import RFIDTagViewSet

router = DefaultRouter()
router.register('rfid-tags', RFIDTagViewSet, basename='rfid-tags')

urlpatterns = [
    path('', include(router.urls)),
]
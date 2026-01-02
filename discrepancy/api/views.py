from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser

from discrepancy.api.serializers import DiscrepancySerializer
from discrepancy.api.permissions import DiscrepancyPermission
from discrepancy.selectors.queries import get_discrepancies_for_user
from discrepancy.services.business_logic import create_discrepancy_service

class DiscrepancyViewSet(ModelViewSet):
    serializer_class = DiscrepancySerializer
    permission_classes = [IsAuthenticated, DiscrepancyPermission]
    
    # Required for uploading files via Swagger/API
    # parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        return get_discrepancies_for_user(self.request.user)

    def perform_create(self, serializer):
        # 1. Call Service
        instance = create_discrepancy_service(self.request.user, serializer.validated_data)
        
        # 2. Fix for "AttributeError": Set instance on serializer
        serializer.instance = instance
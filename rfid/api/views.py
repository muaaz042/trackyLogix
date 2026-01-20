from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError as DRFValidationError
from rest_framework import status

from rfid.api.serializers import (
    RFIDTagSerializer, 
    RFIDStatusSerializer,
    RFIDEncodeSerializer  # New Serializer
)
from rfid.api.permissions import RFIDPermission
from rfid.selectors.queries import get_rfid_tags_for_user
from rfid.services.business_logic import (
    create_rfid_tag_service, 
    update_rfid_status_service,
    encode_rfid_tag_service # New Service
)

class RFIDTagViewSet(ModelViewSet):
    serializer_class = RFIDTagSerializer
    permission_classes = [IsAuthenticated, RFIDPermission]

    def get_queryset(self):
        return get_rfid_tags_for_user(self.request.user)

    def perform_create(self, serializer):
        instance = create_rfid_tag_service(self.request.user, serializer.validated_data)
        serializer.instance = instance

    def perform_update(self, serializer):
        if self.request.user.role != 'DEO':
            raise PermissionDenied("Only DEOs can modify RFID details directly.")
        super().perform_update(serializer)

    def perform_destroy(self, instance):
        if self.request.user.role != 'DEO':
             raise PermissionDenied("Only DEOs can delete RFID tags.")
        super().perform_destroy(instance)

    @action(detail=True, methods=['patch'], url_path='update-status')
    def update_status(self, request, pk=None):
        if request.user.role not in ['Allocator', 'DEO']:
             raise PermissionDenied("You are not authorized to update status.")

        tag = self.get_object()
        serializer = RFIDStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        updated_tag = update_rfid_status_service(
            tag, 
            serializer.validated_data['status'], 
            request.user
        )
        return Response({"status": updated_tag.status, "message": "Status updated successfully"})

    # --- NEW ENDPOINT: Encode Item ---
    @action(detail=True, methods=['post'], url_path='encode-item')
    def encode_item(self, request, pk=None):
        """
        URL: /api/rfid-tags/{id}/encode-item/
        Body: { "epc": "TAG-12345" }
        Action: Updates EPC and auto-sets status to 'encoded'
        """
        # 1. Strict Permission Check
        if request.user.role != 'DEO':
            raise PermissionDenied("Only DEOs can encode items.")

        tag = self.get_object()
        serializer = RFIDEncodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            updated_tag = encode_rfid_tag_service(
                tag=tag,
                new_epc=serializer.validated_data['epc']
            )
            return Response({
                "message": "Item encoded successfully",
                "epc": updated_tag.epc,
                "status": updated_tag.status
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            # Catch duplicate EPC errors or logic errors
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
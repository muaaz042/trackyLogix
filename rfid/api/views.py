from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from rfid.api.serializers import RFIDTagSerializer, RFIDStatusSerializer
from rfid.api.permissions import RFIDPermission
from rfid.selectors.queries import get_rfid_tags_for_user
from rfid.services.business_logic import create_rfid_tag_service, update_rfid_status_service

class RFIDTagViewSet(ModelViewSet):
    serializer_class = RFIDTagSerializer
    permission_classes = [IsAuthenticated, RFIDPermission]

    def get_queryset(self):
        return get_rfid_tags_for_user(self.request.user)

    def perform_create(self, serializer):
        # 1. Call the service and CAPTURE the created instance
        instance = create_rfid_tag_service(self.request.user, serializer.validated_data)
        
        # 2. IMPORTANT: Manually set the instance on the serializer.
        # This tells DRF: "Use this object to generate the JSON response"
        # instead of using the raw dict.
        serializer.instance = instance

    def perform_update(self, serializer):
        # Prevent standard PUT/PATCH for Allocators (they must use update-status)
        if self.request.user.role != 'DEO':
            raise PermissionDenied("Only DEOs can modify RFID details directly.")
        super().perform_update(serializer)

    def perform_destroy(self, instance):
        if self.request.user.role != 'DEO':
             raise PermissionDenied("Only DEOs can delete RFID tags.")
        super().perform_destroy(instance)

    @action(detail=True, methods=['patch'], url_path='update-status')
    def update_status(self, request, pk=None):
        """
        Endpoint for Allocator (and DEO) to update status only.
        """
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
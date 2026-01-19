from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from outbound.models import OutboundRequest
from outbound.selectors.queries import get_outbound_requests_for_user
from outbound.services.business_logic import (
    manager_approve_request_service,
    manager_reject_request_service,
    deo_dispatch_item_by_epc,
    allocator_mark_item_exception # Renamed import
)
from .serializers import (
    OutboundRequestSerializer, 
    ManagerApprovalSerializer,
    DEODispatchScanSerializer,
    AllocatorExceptionSerializer # Renamed import
)
from .permissions import (
    IsClientOwner, 
    IsWarehouseManager, 
    IsAssignedDEO, 
    IsAssignedAllocator # New permission
)

class OutboundRequestViewSet(ModelViewSet):
    serializer_class = OutboundRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return get_outbound_requests_for_user(self.request.user)

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), IsClientOwner()]
        if self.action == 'manager_status_update':
            return [IsAuthenticated(), IsWarehouseManager()]
        
        # Split permissions based on action
        if self.action == 'dispatch_scan':
            return [IsAuthenticated(), IsAssignedDEO()]
        if self.action == 'mark_exception':
            return [IsAuthenticated(), IsAssignedAllocator()]
            
        return [IsAuthenticated()]

    @action(detail=True, methods=['post'], url_path='update-status')
    def manager_status_update(self, request, pk=None):
        serializer = ManagerApprovalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        status_value = serializer.validated_data['status']
        try:
            if status_value == 'approved':
                req = manager_approve_request_service(pk, request.user)
            else:
                req = manager_reject_request_service(pk, request.user)
            return Response(OutboundRequestSerializer(req).data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # --- DEO ENDPOINT ---
    @action(detail=True, methods=['post'], url_path='dispatch-scan')
    def dispatch_scan(self, request, pk=None):
        """
        Only for DEO. Scans valid items.
        """
        serializer = DEODispatchScanSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            item = deo_dispatch_item_by_epc(
                request_id=pk,
                user=request.user,
                epc_code=serializer.validated_data['epc']
            )
            return Response({
                "message": "Item dispatched successfully",
                "sku": item.sku,
                "progress": f"{item.dispatched_quantity}/{item.requested_quantity}",
                "status": item.item_status
            })
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # --- ALLOCATOR ENDPOINT ---
    @action(detail=True, methods=['post'], url_path='mark-exception')
    def mark_exception(self, request, pk=None):
        """
        Only for Allocator. Marks missing/damaged items.
        Payload: { "item_id": 123, "item_status": "missing", "remarks": "..." }
        """
        serializer = AllocatorExceptionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            allocator_mark_item_exception(
                request_id=pk,
                item_id=serializer.validated_data['item_id'],
                user=request.user,
                status=serializer.validated_data['item_status'],
                remarks=serializer.validated_data['remarks']
            )
            return Response({"message": "Item marked as exception"})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
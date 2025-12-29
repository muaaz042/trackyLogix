from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from inboundRequests.models import InboundRequest, InboundItem
from .serializer import (
    InboundRequestSerializer, 
    InboundItemSerializer,
    ManagerRequestStatusSerializer,
    ManagerItemStatusSerializer
)
from .permissions import IsClient, IsManager
from inboundRequests.services.business_logic import (
    manager_update_request_status,
    manager_update_item_status,
    validate_request_modification,
    get_and_validate_request_for_item_creation
)
from inboundRequests.selectors.queries import (
    get_inbound_requests_for_user,
    get_inbound_items_for_user
)

class InboundRequestViewSet(ModelViewSet):
    serializer_class = InboundRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsClient()]
        if self.action == 'update_status':
            return [IsAuthenticated(), IsManager()]
        return [IsAuthenticated()]

    def get_queryset(self):
        return get_inbound_requests_for_user(
            self.request.user, 
            warehouse_filter=self.request.query_params.get('warehouse_id')
        )

    def perform_destroy(self, instance):
        validate_request_modification(instance)
        super().perform_destroy(instance)

    @action(detail=True, methods=["post"]) 
    def update_status(self, request, pk=None):
        inbound_request = self.get_object()
        serializer = ManagerRequestStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            manager_update_request_status(inbound_request, serializer.validated_data['status'], request.user)
            return Response({"message": "Status updated successfully"})
        except ValidationError as e:
            return Response({"error": str(e)}, status=400)


class InboundItemViewSet(ModelViewSet):
    serializer_class = InboundItemSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsClient()]
        if self.action == 'update_status':
            return [IsAuthenticated(), IsManager()]
        return [IsAuthenticated()]

    def get_queryset(self):
        return get_inbound_items_for_user(self.request.user)

    def perform_create(self, serializer):
        # 1. Logic extracted to business_logic.py
        request_id = self.kwargs.get('request_pk') or self.request.data.get('inbound_request')
        
        # 2. Validate and Get Request
        req = get_and_validate_request_for_item_creation(request_id, self.request.user)
        
        # 3. Save
        serializer.save(inbound_request=req)

    def perform_update(self, serializer):
        validate_request_modification(serializer.instance.inbound_request)
        super().perform_update(serializer)

    def perform_destroy(self, instance):
        validate_request_modification(instance.inbound_request)
        super().perform_destroy(instance)

    @action(detail=True, methods=["post"])
    def update_status(self, request, pk=None):
        item = self.get_object()
        serializer = ManagerItemStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            manager_update_item_status(item, serializer.validated_data['item_status'])
            return Response({"message": "Item status updated"})
        except ValidationError as e:
            return Response({"error": str(e)}, status=400)
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from inboundRequests.models import InboundRequest, InboundItem
from users.models import ClientProfile
from .serializer import (
    InboundRequestSerializer, 
    InboundItemSerializer,
    ManagerRequestStatusSerializer,
    DEOItemStatusSerializer # Renamed from ManagerItemStatusSerializer
)
from .permissions import IsClient, IsManager, IsDEO
from inboundRequests.services.business_logic import (
    manager_update_request_status,
    deo_update_item_status, # Renamed
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

    def perform_create(self, serializer):
        try:
            client_profile = ClientProfile.objects.get(user=self.request.user)
        except ClientProfile.DoesNotExist:
            raise ValidationError({"detail": "You do not have a Client Profile associated with this account."})
        serializer.save(client=client_profile)

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
        
        # CHANGED: update_status is now for DEO
        if self.action == 'update_status':
            return [IsAuthenticated(), IsDEO()]
            
        return [IsAuthenticated()]

    def get_queryset(self):
        return get_inbound_items_for_user(self.request.user)

    def perform_create(self, serializer):
        request_id = self.kwargs.get('request_pk') or self.request.data.get('inbound_request')
        req = get_and_validate_request_for_item_creation(request_id, self.request.user)
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
        # CHANGED: Using DEO serializer
        serializer = DEOItemStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            # CHANGED: Calling DEO logic
            deo_update_item_status(item, serializer.validated_data['item_status'])
            return Response({"message": "Item status updated"})
        except ValidationError as e:
            return Response({"error": str(e)}, status=400)
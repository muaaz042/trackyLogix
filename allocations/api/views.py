from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from allocations.models import Allocation
from .serializer import AllocationSerializer
from .permissions import IsAllocator
from allocations.selectors.queries import get_allocations_for_user
from allocations.services.business_logic import create_allocation_service, delete_allocation_service

class AllocationViewSet(ModelViewSet):
    serializer_class = AllocationSerializer
    permission_classes = [IsAllocator]

    def get_queryset(self):
        return get_allocations_for_user(self.request.user)

    def create(self, request, *args, **kwargs):
        # 1. Validate Data via Serializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 2. Pass to Business Logic (Handles Hierarchy & Status)
        allocation = create_allocation_service(serializer.validated_data)
        
        # 3. Return Response
        output_serializer = self.get_serializer(allocation)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        # Use business logic to revert status before deleting
        delete_allocation_service(instance)
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from allocations.models import Allocation
from .serializer import (
    AllocationSerializer, 
    EPCLookupRequestSerializer, 
    SKULookupRequestSerializer,
    AllocationDetailsSerializer,
    SKULocationSerializer # Import the new simplified serializer
)
from .permissions import IsAllocator
from allocations.selectors.queries import get_allocations_for_user
from allocations.services.business_logic import create_allocation_service, delete_allocation_service

class AllocationViewSet(ModelViewSet):
    serializer_class = AllocationSerializer
    permission_classes = [IsAllocator]

    def get_queryset(self):
        return get_allocations_for_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        allocation = create_allocation_service(serializer.validated_data)
        output_serializer = self.get_serializer(allocation)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        delete_allocation_service(instance)

    @action(detail=False, methods=['post'], url_path='lookup-by-epc')
    def lookup_by_epc(self, request):
        """
        Returns FULL details for specific EPCs.
        """
        input_serializer = EPCLookupRequestSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        epc_list = input_serializer.validated_data['epcs']

        queryset = self.get_queryset().filter(rfid__epc__in=epc_list)
        queryset = self._eager_load_queryset(queryset)

        # Use the Detailed Serializer here
        output_serializer = AllocationDetailsSerializer(queryset, many=True)
        
        found_epcs = set(queryset.values_list('rfid__epc', flat=True))
        missing_epcs = list(set(epc_list) - found_epcs)

        return Response({
            "results": output_serializer.data,
            "missing_epcs": missing_epcs,
            "count": len(output_serializer.data)
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='lookup-by-sku')
    def lookup_by_sku(self, request):
        """
        Returns ONLY location info and EPC for the given SKUs.
        """
        input_serializer = SKULookupRequestSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        sku_list = input_serializer.validated_data['skus']

        queryset = self.get_queryset().filter(rfid__inbound_item__sku__in=sku_list)
        queryset = self._eager_load_queryset(queryset)

        # CHANGED: Use the Simplified Serializer here
        output_serializer = SKULocationSerializer(queryset, many=True)
        
        found_skus = set(queryset.values_list('rfid__inbound_item__sku', flat=True))
        missing_skus = list(set(sku_list) - found_skus)

        return Response({
            "results": output_serializer.data,
            "missing_skus": missing_skus,
            "count": len(output_serializer.data)
        }, status=status.HTTP_200_OK)

    def _eager_load_queryset(self, queryset):
        return queryset.select_related(
            'rfid', 
            'rfid__inbound_item', 
            'location', 
            'location__zone', 
            'location__zone__warehouse',
            'aisle', 
            'rack', 
            'level', 
            'bin'
        )
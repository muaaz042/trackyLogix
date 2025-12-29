from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError

from users.models import User, Warehouse, WarehouseUserManagement, ClientProfile
from .serializers import (
    RegisterSerializer,
    UserSerializer,
    WarehouseSerializer,
    WarehouseUserManagementSerializer,
    ClientProfileSerializer,
)
from .permissions import IsSameWarehouse, IsClient, IsAdmin

# Import separated logic
from users.services.business_logic import create_warehouse_service
from users.selectors.queries import (
    get_user_queryset,
    get_warehouses_for_user,
    get_warehouse_user_links_for_user,
    get_client_profile_queryset
)

class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer

    def perform_create(self, serializer):
        # 1. Prepare Data
        creator = self.request.user if self.request.user.is_authenticated else None
        role = serializer.validated_data.get("role")

        warehouse_data = None
        if role == "admin":
            warehouse_data = {
                "name": self.request.data.get("warehouse_name"),
                "address": self.request.data.get("warehouse_address"),
                "contact_number": self.request.data.get("warehouse_contact_number"),
            }

        # 2. Delegate to Serializer (which calls business_logic.create_user_with_validation)
        serializer.save(creator=creator, warehouse_data=warehouse_data)


class LoginView(TokenObtainPairView):
    pass


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return get_user_queryset(self.request.user)


class WarehouseViewSet(ModelViewSet):
    serializer_class = WarehouseSerializer
    permission_classes = [IsAuthenticated, IsSameWarehouse, IsAdmin]

    def get_queryset(self):
        return get_warehouses_for_user(self.request.user)

    def perform_create(self, serializer):
        try:
            create_warehouse_service(self.request.user, serializer)
        except Exception as e:
            raise ValidationError(str(e))


class WarehouseUserManagementViewSet(ModelViewSet):
    serializer_class = WarehouseUserManagementSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return get_warehouse_user_links_for_user(self.request.user)


class ClientProfileViewSet(ModelViewSet):
    serializer_class = ClientProfileSerializer
    permission_classes = [IsAuthenticated, IsClient]

    def get_queryset(self):
        return get_client_profile_queryset(self.request.user)

    def get_object(self):
        return self.get_queryset().first()

    def destroy(self, request, *args, **kwargs):
        return Response({"detail": "Deletion not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
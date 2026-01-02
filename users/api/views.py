from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError

from users.models import User, Warehouse, WarehouseUserManagement, ClientProfile
from .serializers import (
    RegisterSerializer, UserSerializer, WarehouseSerializer,
    WarehouseUserManagementSerializer, ClientProfileSerializer,
)
from .permissions import IsSameWarehouse, IsClient, IsAdmin
from users.services.business_logic import validate_admin_can_add_warehouse, validate_subscription_limits
from users.selectors.queries import (
    get_warehouse_user_links_for_user, 
    get_client_warehouse_links,
    get_warehouses_for_user,
    get_user_queryset,
    get_client_profile_queryset
)

class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer

    def perform_create(self, serializer):
        creator = self.request.user if self.request.user.is_authenticated else None
        role = serializer.validated_data.get("role")

        warehouse_data = None
        if role == "admin":
            warehouse_data = {
                "name": self.request.data.get("warehouse_name"),
                "address": self.request.data.get("warehouse_address"),
                "contact_number": self.request.data.get("warehouse_contact_number"),
            }

        serializer.save(creator=creator, warehouse_data=warehouse_data)


class LoginView(TokenObtainPairView):
    pass


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    lookup_value_regex = r'\d+'

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return User.objects.none()
        return get_user_queryset(self.request.user)


class WarehouseViewSet(ModelViewSet):
    """
    Endpoint for managing Warehouses.
    """
    serializer_class = WarehouseSerializer
    permission_classes = [IsAuthenticated]
    lookup_value_regex = r'\d+'

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Warehouse.objects.none()
        return get_warehouses_for_user(self.request.user)

    def get_permissions(self):
        if self.action in ['create', 'destroy', 'update', 'partial_update']:
            return [IsAuthenticated(), IsAdmin()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        user = self.request.user
        
        if user.role != 'admin':
            raise ValidationError("Only admins can create warehouses.")

        validate_admin_can_add_warehouse(user)

        warehouse = serializer.save()
        WarehouseUserManagement.objects.create(warehouse=warehouse, user=user)


class WarehouseUserManagementViewSet(ModelViewSet):
    """
    Endpoint for Admin, Manager, DEO, Allocator to see staff assignments.
    Clients are NOT allowed here.
    """
    serializer_class = WarehouseUserManagementSerializer
    permission_classes = [IsAuthenticated]
    lookup_value_regex = r'\d+'

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return WarehouseUserManagement.objects.none()
            
        if self.request.user.role == 'client':
             return WarehouseUserManagement.objects.none()

        return get_warehouse_user_links_for_user(self.request.user)

    def get_permissions(self):
        if not self.request.user.is_authenticated:
            return super().get_permissions()

        if self.request.user.role in ['DEO', 'Allocator']:
            if self.action not in ['list', 'retrieve']:
                self.permission_classes = [IsAdmin] 
        
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        """
        Custom create to handle:
        1. Auto-lookup User ID from Email.
        2. Auto-assignment of Warehouse for Managers AND Admins.
        3. Subscription Limit Validation.
        """
        data = request.data.copy()
        
        # --- 1. Email Lookup Logic ---
        # If 'email' provided instead of 'user_id', find the user automatically.
        if 'email' in data and not data.get('user_id'):
            email = data.get('email')
            try:
                user_obj = User.objects.get(email=email)
                data['user_id'] = user_obj.id
            except User.DoesNotExist:
                raise ValidationError({"email": f"User with email '{email}' does not exist."})

        # --- 2. Warehouse Auto-Assignment (Admin & Manager) ---
        # Logic: If Admin/Manager has exactly one warehouse, auto-fill it.
        if request.user.role in ['admin', 'manager']:
            # Get warehouses linked to this user
            user_links = WarehouseUserManagement.objects.filter(user=request.user)
            
            if not user_links.exists():
                raise ValidationError({"detail": f"You ({request.user.role}) are not assigned to any warehouse."})

            # Check if ID was manually provided
            req_warehouse_id = data.get('warehouse_id')

            if req_warehouse_id:
                # Security: Ensure they own/manage the one they requested
                if int(req_warehouse_id) not in user_links.values_list('warehouse_id', flat=True):
                    raise ValidationError({"warehouse_id": "You do not have permission for this warehouse."})
            else:
                # Auto-fill if only 1 exists
                if user_links.count() == 1:
                    data['warehouse_id'] = user_links.first().warehouse.id
                else:
                    raise ValidationError({"warehouse_id": "You manage multiple warehouses. Please specify which one."})

        # --- 3. Subscription & Validation ---
        user_id = data.get('user_id')
        warehouse_id = data.get('warehouse_id')

        if user_id and warehouse_id:
            try:
                user_to_link = User.objects.get(id=user_id)
                validate_subscription_limits(user_to_link.role, warehouse_id)
            except User.DoesNotExist:
                # Serializer will raise the specific "Invalid pk" error later
                pass 
            except ValidationError as e:
                raise ValidationError({"detail": str(e.detail[0] if isinstance(e.detail, list) else e.detail)})

        # --- 4. Standard Create ---
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ClientWarehouseViewSet(ReadOnlyModelViewSet):
    """
    Separate endpoint specifically for Clients to see their attached warehouses.
    """
    serializer_class = WarehouseUserManagementSerializer
    permission_classes = [IsAuthenticated, IsClient]
    lookup_value_regex = r'\d+'

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return WarehouseUserManagement.objects.none()
            
        return get_client_warehouse_links(self.request.user)


class ClientProfileViewSet(ModelViewSet):
    serializer_class = ClientProfileSerializer
    permission_classes = [IsAuthenticated, IsClient]
    lookup_value_regex = r'\d+'

    def get_queryset(self):
        return get_client_profile_queryset(self.request.user)

    def get_object(self):
        return self.get_queryset().first()

    def destroy(self, request, *args, **kwargs):
        return Response({"detail": "Deletion not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
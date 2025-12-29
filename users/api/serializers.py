from rest_framework import serializers
from users.models import User, Warehouse, WarehouseUserManagement, ClientProfile
from users.services.business_logic import (
    validate_user_creator, 
    validate_subscription_limits, 
    create_user_with_validation,
    validate_admin_can_add_warehouse
)

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "password", "first_name", "last_name", "role")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        # 1. EXTRACT EXTRA DATA
        # These are passed from the View's perform_create via serializer.save()
        # We must .pop() them so they don't cause errors when creating the User model
        creator = validated_data.pop('creator', None)
        warehouse_data = validated_data.pop('warehouse_data', None)

        # 2. DELEGATE TO BUSINESS LOGIC
        return create_user_with_validation(
            validated_data=validated_data, 
            creator=creator, 
            warehouse_data=warehouse_data
        )


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = "__all__"


class WarehouseUserManagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = WarehouseUserManagement
        fields = ("id", "warehouse", "user")

    def validate(self, attrs):
        user = attrs['user']
        warehouse = attrs['warehouse']
        
        # Case 1: Linking an Admin (Admin -> Warehouse Limit)
        if user.role == 'admin':
            try:
                validate_admin_can_add_warehouse(user)
            except Exception as e:
                raise serializers.ValidationError(str(e))

        # Case 2: Linking Staff (Manager/DEO/Allocator -> Role Limit)
        elif user.role in ['manager', 'DEO', 'Allocator']:
            try:
                validate_subscription_limits(user.role, warehouse.id)
            except Exception as e:
                raise serializers.ValidationError(str(e))

        return attrs


class ClientProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientProfile
        fields = ("company_name", "contact_number", "address", "emergency_contact")


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ("password",)
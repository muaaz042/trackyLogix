from rest_framework import serializers
from django.contrib.auth import get_user_model
from users.models import Warehouse, WarehouseUserManagement, ClientProfile

# Import the business logic function
from users.services.business_logic import create_user_with_validation

User = get_user_model()

# --- Nested Serializers for Detailed Responses ---
class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'role']

class SimpleWarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = ['id', 'name', 'address', 'contact_number']

# --- Main Serializers ---

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name', 'role']

    def create(self, validated_data):
        """
        Overriding create to handle 'creator' and 'warehouse_data' 
        which are passed via serializer.save() in the view.
        """
        # Extract the extra arguments passed from the View
        creator = validated_data.pop('creator', None)
        warehouse_data = validated_data.pop('warehouse_data', None)

        # Delegate the actual creation to the business logic service
        return create_user_with_validation(
            validated_data, 
            creator=creator, 
            warehouse_data=warehouse_data
        )

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'role', 'is_active']

class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = '__all__'

class WarehouseUserManagementSerializer(serializers.ModelSerializer):
    # INPUTS: Accept IDs when creating/writing
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='user', write_only=True
    )
    warehouse_id = serializers.PrimaryKeyRelatedField(
        queryset=Warehouse.objects.all(), source='warehouse', write_only=True
    )

    # OUTPUTS: Return full Objects when reading
    user = SimpleUserSerializer(read_only=True)
    warehouse = SimpleWarehouseSerializer(read_only=True)

    class Meta:
        model = WarehouseUserManagement
        # Removed 'created_at' to fix the previous error
        fields = ['id', 'warehouse_id', 'user_id', 'warehouse', 'user']

class ClientProfileSerializer(serializers.ModelSerializer):
    user = SimpleUserSerializer(read_only=True)
    class Meta:
        model = ClientProfile
        fields = ['id', 'user', 'company_name', 'contact_number', 'address']
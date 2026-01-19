from rest_framework import serializers
from tasks.models import Task
from users.models import User

class TaskSerializer(serializers.ModelSerializer):
    assigned_by_name = serializers.CharField(source='assigned_by_user.email', read_only=True)
    deo_name = serializers.CharField(source='assigned_to_deo.email', read_only=True)
    allocator_name = serializers.CharField(source='assigned_to_allocator.email', read_only=True)

    assigned_to_deo = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='DEO'),
        required=False,
        allow_null=True
    )
    assigned_to_allocator = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='Allocator'),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Task
        fields = [
            'id', 
            'task_type', 
            'request_id',
            'description', 
            'deo_status',        # Changed
            'allocator_status',  # Changed
            'assigned_by_user', 'assigned_by_name',
            'assigned_to_deo', 'deo_name',
            'assigned_to_allocator', 'allocator_name',
            'created_at', 
            'updated_at'
        ]
        read_only_fields = ['assigned_by_user', 'created_at', 'updated_at']

    def validate(self, data):
        """
        Custom validation to enforce role-based status updates.
        """
        request = self.context.get('request')
        instance = self.instance # Available on Update operations
        user = request.user if request else None

        # 1. Assignment Validation (At least one assignee)
        deo = data.get('assigned_to_deo') or (instance.assigned_to_deo if instance else None)
        allocator = data.get('assigned_to_allocator') or (instance.assigned_to_allocator if instance else None)
        
        if not deo and not allocator:
            raise serializers.ValidationError("Task must be assigned to at least a DEO or an Allocator.")

        # 2. Status Update Permission Check
        if instance and user: # If updating an existing task
            # If user is DEO, they cannot change allocator_status
            if user.role == 'DEO' and 'allocator_status' in data:
                if data['allocator_status'] != instance.allocator_status:
                     raise serializers.ValidationError({"allocator_status": "DEOs cannot update Allocator status."})
            
            # If user is Allocator, they cannot change deo_status
            if user.role == 'Allocator' and 'deo_status' in data:
                if data['deo_status'] != instance.deo_status:
                     raise serializers.ValidationError({"deo_status": "Allocators cannot update DEO status."})

        return data
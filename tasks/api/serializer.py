from rest_framework import serializers
from tasks.models import Task
from users.models import User

class TaskSerializer(serializers.ModelSerializer):
    assigned_by_name = serializers.CharField(source='assigned_by_user.email', read_only=True)
    deo_name = serializers.CharField(source='assigned_to_deo.email', read_only=True)
    allocator_name = serializers.CharField(source='assigned_to_allocator.email', read_only=True)

    # Inputs for IDs
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
            'status', 
            'assigned_by_user', 'assigned_by_name',
            'assigned_to_deo', 'deo_name',
            'assigned_to_allocator', 'allocator_name',
            'created_at', 
            'updated_at'
        ]
        read_only_fields = ['assigned_by_user', 'created_at', 'updated_at']

    def validate(self, data):
        """
        Optional: Custom validation logic
        e.g., Ensure at least one person is assigned.
        """
        deo = data.get('assigned_to_deo')
        allocator = data.get('assigned_to_allocator')
        
        if not deo and not allocator:
            raise serializers.ValidationError("Task must be assigned to at least a DEO or an Allocator.")
            
        return data
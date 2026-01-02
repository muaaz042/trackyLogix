from rest_framework import serializers
from django.contrib.auth import get_user_model
from tasks.models import Task
from inboundRequests.models import InboundRequest

User = get_user_model()

class TaskSerializer(serializers.ModelSerializer):
    # INPUT: Accept ID for Inbound Request
    inbound_request_id = serializers.PrimaryKeyRelatedField(
        queryset=InboundRequest.objects.all(), 
        source='inbound_request', 
        write_only=True,
        required=False,
        allow_null=True
    )

    # OUTPUT: Show details of Inbound Request (Reference Number)
    inbound_request_details = serializers.CharField(
        source='inbound_request.reference_number', 
        read_only=True,
        default=None
    )

    # INPUT: Assign to User (ID)
    assigned_to_user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='assigned_to_user',
        write_only=True
    )

    # OUTPUT: User Details
    assigned_to_user_email = serializers.EmailField(source='assigned_to_user.email', read_only=True)
    assigned_by_user_email = serializers.EmailField(source='assigned_by_user.email', read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 
            'task_type',
            'description', 
            'status', 
            'inbound_request_id', 
            'inbound_request_details',
            'assigned_to_user_id', 
            'assigned_to_user_email',
            'assigned_by_user_email',
            'created_at', 
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'assigned_by_user_email']

class TaskStatusUpdateSerializer(serializers.Serializer):
    """
    Serializer specifically for updating the status of a Task.
    Used by custom actions in the viewset.
    """
    status = serializers.ChoiceField(choices=Task.STATUS_CHOICES)
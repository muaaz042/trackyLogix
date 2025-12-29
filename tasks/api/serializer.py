from rest_framework import serializers
from tasks.models import Task
from inboundRequests.models import InboundRequest

class TaskSerializer(serializers.ModelSerializer):
    assigned_by_user = serializers.StringRelatedField(read_only=True)
    assigned_to_email = serializers.EmailField(source='assigned_to_user.email', read_only=True)
    
    # 1. Input ID
    inbound_request = serializers.PrimaryKeyRelatedField(
        queryset=InboundRequest.objects.all(),
        required=False,
        allow_null=True
    )

    # 2. Output Custom String (Without the confusing status)
    inbound_request_details = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 
            'name', 
            'description', 
            'status', 
            'inbound_request',
            'inbound_request_details', 
            'assigned_by_user', 
            'assigned_to_user', 
            'assigned_to_email',
            'created_at', 
            'updated_at'
        ]
        read_only_fields = ['assigned_by_user', 'created_at', 'updated_at', 'inbound_request_details']

    def get_inbound_request_details(self, obj):
        if not obj.inbound_request:
            return None
        # Custom format: "Req #1 - email@example.com" (Removed the status part)
        return f"Req #{obj.inbound_request.id} - {obj.inbound_request.client.user.email} ({obj.status})"


class TaskStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['status']
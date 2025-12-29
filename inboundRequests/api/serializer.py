from rest_framework import serializers
from inboundRequests.models import InboundRequest, InboundItem
from users.models import ClientProfile
from inboundRequests.services.business_logic import validate_request_modification

# --- STATUS SERIALIZERS (For Managers) ---

class ManagerRequestStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=InboundRequest.STATUS_CHOICES)

class ManagerItemStatusSerializer(serializers.Serializer):
    item_status = serializers.ChoiceField(choices=InboundItem.ITEM_STATUS_CHOICES)


# --- STANDARD SERIALIZERS ---

class InboundItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InboundItem
        fields = "__all__"
        read_only_fields = ("id", "item_status", "inbound_request")


class InboundRequestSerializer(serializers.ModelSerializer):
    items = InboundItemSerializer(many=True, read_only=True)
    
    # Optional: Display client email for readability in responses
    client_email = serializers.EmailField(source='client.user.email', read_only=True)
    
    status = serializers.CharField(read_only=True)
    approved_by_user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = InboundRequest
        fields = "__all__"
        # CRITICAL FIX: 'client' MUST be here so DRF doesn't demand it in the POST body
        read_only_fields = ("client", "status", "approved_by_user", "created_at", "updated_at", "client_email")

    def create(self, validated_data):
        user = self.context["request"].user
        
        # 1. Get the ClientProfile associated with the logged-in User
        try:
            profile = ClientProfile.objects.get(user=user)
        except ClientProfile.DoesNotExist:
            raise serializers.ValidationError({"detail": "No Client Profile found for this user."})

        # 2. Assign the profile to the 'client' field
        validated_data["client"] = profile
        
        return super().create(validated_data)

    def update(self, instance, validated_data):
        user = self.context["request"].user
        
        # 1. Validation Check (Your new logic)
        if user.role == 'client':
            validate_request_modification(instance)

            # 2. AUTO-RESET LOGIC:
            # If the client edits a 'rejected' request, move it back to 'pending'
            # so the Manager knows to review it again.
            if instance.status == 'rejected':
                instance.status = 'pending'
                # Optional: Clear the previous approver since it's pending again
                instance.approved_by_user = None 
                instance.save()

        return super().update(instance, validated_data)
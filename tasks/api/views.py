from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError

from tasks.api.serializer import TaskSerializer, TaskStatusUpdateSerializer
from tasks.api.permissions import IsManager, IsTaskParticipant
from tasks.selectors.queries import get_tasks_for_user
from tasks.services.business_logic import create_task_service, update_task_status_service

class TaskViewSet(ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsTaskParticipant]

    def get_queryset(self):
        return get_tasks_for_user(self.request.user)

    def get_permissions(self):
        # Only Manager can Create or Delete
        if self.action in ['create', 'destroy']:
            return [IsAuthenticated(), IsManager()]
        return super().get_permissions()

    def perform_create(self, serializer):
        # Delegate creation to business logic service
        create_task_service(self.request.user, serializer.validated_data)

    def perform_update(self, serializer):
        user = self.request.user
        
        # If user is NOT a manager, they can't change details (name/desc), only status via custom endpoint
        if user.role in ['DEO', 'Allocator']:
             raise PermissionDenied("DEO/Allocators can only update status using the 'update-status' endpoint.")
        
        super().perform_update(serializer)

    @action(detail=True, methods=['patch'], url_path='update-status')
    def update_status(self, request, pk=None):
        """
        Specific endpoint for DEO/Allocator to update task status.
        """
        task = self.get_object()
        serializer = TaskStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            updated_task = update_task_status_service(
                task, 
                serializer.validated_data['status'], 
                request.user
            )
            return Response({"status": updated_task.status, "message": "Status updated successfully."})
        except Exception as e:
            return Response({"error": str(e)}, status=400)
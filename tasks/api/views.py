from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from tasks.models import Task
from .serializer import TaskSerializer
from tasks.selectors.queries import get_tasks_for_user
from .permissions import IsTaskParticipant

class TaskViewSet(ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsTaskParticipant]

    def get_queryset(self):
        return get_tasks_for_user(self.request.user)

    def perform_create(self, serializer):
        # Auto-assign the creator
        serializer.save(assigned_by_user=self.request.user)
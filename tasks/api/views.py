from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q

from tasks.models import Task
from .serializer import TaskSerializer
from users.models import WarehouseUserManagement

class TaskViewSet(ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        
        # Admin: See all
        if user.role == 'admin':
            return Task.objects.all()

        # Manager: See tasks they created OR tasks related to their warehouse
        if user.role == 'manager':
            # Option A: Only created by them
            # return Task.objects.filter(assigned_by_user=user)
            
            # Option B: All tasks in their warehouse scope (More complex logic needed if tasks link to warehouse)
            # For simplicity, returning tasks created by them:
            return Task.objects.filter(assigned_by_user=user)

        # DEO: See tasks assigned to them
        if user.role == 'DEO':
            return Task.objects.filter(assigned_to_deo=user)

        # Allocator: See tasks assigned to them
        if user.role == 'Allocator':
            return Task.objects.filter(assigned_to_allocator=user)

        return Task.objects.none()

    def perform_create(self, serializer):
        # Auto-assign the creator
        serializer.save(assigned_by_user=self.request.user)
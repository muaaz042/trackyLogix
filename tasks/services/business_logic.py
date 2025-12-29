from rest_framework.exceptions import ValidationError, PermissionDenied
from tasks.models import Task
from django.contrib.auth import get_user_model

User = get_user_model()

def validate_task_assignee(assigned_to_user):
    """
    Ensure the assignee has the correct role (DEO or Allocator).
    """
    if assigned_to_user.role not in ['DEO', 'Allocator']:
        raise ValidationError({"assigned_to_user": "Tasks can only be assigned to a DEO or Allocator."})

def create_task_service(user, validated_data):
    """
    Handles task creation logic.
    """
    # 1. Ensure User is a Manager
    if user.role != 'manager':
        raise PermissionDenied("Only Managers can create tasks.")

    assigned_to = validated_data.get('assigned_to_user')
    
    # 2. Validate Assignee Role
    validate_task_assignee(assigned_to)

    # 3. Create Task
    task = Task.objects.create(
        assigned_by_user=user,
        **validated_data
    )
    return task

def update_task_status_service(task, status, user):
    """
    Allows DEO/Allocator to update status only.
    """
    # Ensure the user is actually the assignee
    if task.assigned_to_user != user and user.role != 'manager':
        raise PermissionDenied("You do not have permission to update this task.")

    task.status = status
    task.save(update_fields=['status', 'updated_at'])
    return task
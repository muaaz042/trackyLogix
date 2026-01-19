from rest_framework.exceptions import ValidationError, PermissionDenied
from tasks.models import Task
from django.contrib.auth import get_user_model

User = get_user_model()

def validate_task_assignee(assigned_to_user, required_role):
    """
    Helper to validate role.
    """
    if assigned_to_user and assigned_to_user.role != required_role:
        raise ValidationError(f"User must have role '{required_role}'.")

def create_task_service(user, validated_data):
    """
    Handles task creation logic.
    """
    if user.role != 'manager':
        raise PermissionDenied("Only Managers can create tasks.")

    deo = validated_data.get('assigned_to_deo')
    allocator = validated_data.get('assigned_to_allocator')
    
    validate_task_assignee(deo, 'DEO')
    validate_task_assignee(allocator, 'Allocator')

    task = Task.objects.create(
        assigned_by_user=user,
        **validated_data
    )
    return task

def update_task_status_service(task, status_data, user):
    """
    Updates the specific status field based on user role.
    Expects status_data to be a dict like {'status': 'completed'} 
    mapped to the correct field.
    """
    # Logic is largely handled in Serializer validation now, 
    # but strictly in business logic:
    
    new_status = status_data.get('status')
    if not new_status:
        return task

    updated_fields = ['updated_at']

    if user == task.assigned_to_deo:
        task.deo_status = new_status
        updated_fields.append('deo_status')
    
    elif user == task.assigned_to_allocator:
        task.allocator_status = new_status
        updated_fields.append('allocator_status')
    
    elif user.role == 'manager':
        # Manager might want to force update both? 
        # For now, let's assume they pass specific keys in validated_data via serializer
        pass
    else:
        raise PermissionDenied("You are not assigned to this task.")

    task.save(update_fields=updated_fields)
    return task
from tasks.models import Task
from django.db.models import Q

def get_tasks_for_user(user):
    """
    Returns tasks based on user role.
    """
    if user.role == "manager":
        return Task.objects.filter(assigned_by_user=user)
    
    if user.role == "DEO":
        return Task.objects.filter(assigned_to_deo=user)
        
    if user.role == "Allocator":
        return Task.objects.filter(assigned_to_allocator=user)
    
    if user.role == "admin":
        return Task.objects.all()

    return Task.objects.none()
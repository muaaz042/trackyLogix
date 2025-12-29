from tasks.models import Task

def get_tasks_for_user(user):
    """
    Returns tasks based on user role:
    - Manager: Tasks they assigned.
    - DEO/Allocator: Tasks assigned to them.
    - Admin: All tasks.
    """
    if user.role == "manager":
        return Task.objects.filter(assigned_by_user=user)
    
    if user.role in ["DEO", "Allocator"]:
        return Task.objects.filter(assigned_to_user=user)
    
    if user.role == "admin":
        return Task.objects.all()

    return Task.objects.none()
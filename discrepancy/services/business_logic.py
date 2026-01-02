from rest_framework.exceptions import PermissionDenied
from discrepancy.models import Discrepancy

def create_discrepancy_service(user, validated_data):
    """
    Service to create a discrepancy report.
    Only DEOs are allowed to create.
    """
    if user.role != 'DEO':
        raise PermissionDenied("Only DEOs can report discrepancies.")
    
    # The 'photo' file is inside validated_data. 
    # Django handles the upload to the folder and saving the URL to DB automatically.
    discrepancy = Discrepancy.objects.create(
        reported_by_user=user,
        **validated_data
    )
    return discrepancy
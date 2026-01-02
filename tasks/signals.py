from django.db.models.signals import post_save
from django.dispatch import receiver
from tasks.models import Task
from rfid.models import RFIDTag

@receiver(post_save, sender=Task)
def auto_generate_rfid_tags(sender, instance, created, **kwargs):
    """
    Signal to automatically generate 'Un-encoded' RFID tags when a Manager 
    assigns a task linked to an Inbound Request to a DEO.
    """
    # 1. Only run on creation
    if not created:
        return

    # 2. Ensure task is linked to an Inbound Request
    if not instance.inbound_request:
        return

    # 3. Ensure the task is assigned to a DEO
    if not instance.assigned_to_user or instance.assigned_to_user.role != 'DEO':
        return

    inbound_request = instance.inbound_request
    items = inbound_request.items.all()
    
    tags_to_create = []

    # 4. Generate Tags based on quantity
    for item in items:
        # Create 'N' tags for 'N' quantity
        for _ in range(item.quantity):
            tag = RFIDTag(
                inbound_item=item,     # Linked to the specific Item now
                epc=None,              # Null as requested
                status='unencoded'     # Default status
            )
            tags_to_create.append(tag)

    # 5. Bulk create for performance
    if tags_to_create:
        RFIDTag.objects.bulk_create(tags_to_create)
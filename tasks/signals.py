from django.db.models.signals import post_save
from django.dispatch import receiver
from tasks.models import Task
from rfid.models import RFIDTag
from inboundRequests.models import InboundRequest

@receiver(post_save, sender=Task)
def auto_generate_rfid_tags(sender, instance, created, **kwargs):
    """
    Signal to automatically generate 'Un-encoded' RFID tags when a Manager 
    assigns an INBOUND task to a DEO.
    """
    # 1. Only run on creation
    if not created:
        return

    # 2. Check if this is an Inbound Task
    if instance.task_type != 'inbound':
        return

    # 3. Check if assigned to a DEO (New Field Name)
    if not instance.assigned_to_deo:
        return

    # 4. Fetch the actual Inbound Request using the ID
    try:
        inbound_request = InboundRequest.objects.get(id=instance.request_id)
    except InboundRequest.DoesNotExist:
        # Safety check in case the ID is invalid
        return

    items = inbound_request.items.all()
    tags_to_create = []

    # 5. Generate Tags based on quantity
    for item in items:
        # Create 'N' tags for 'N' quantity
        for _ in range(item.quantity):
            tag = RFIDTag(
                inbound_item=item,     
                epc=None,              
                status='unencoded'     
            )
            tags_to_create.append(tag)

    # 6. Bulk create for performance
    if tags_to_create:
        RFIDTag.objects.bulk_create(tags_to_create)
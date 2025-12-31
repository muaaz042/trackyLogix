import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver
from tasks.models import Task
from rfid.models import RFIDTag

@receiver(post_save, sender=Task)
def auto_generate_rfid_tags(sender, instance, created, **kwargs):
    """
    Signal to automatically generate RFID tags when a Manager assigns a task 
    linked to an Inbound Request to a DEO.
    """
    if not created:
        return

    if not instance.inbound_request:
        return

    if instance.assigned_to_user.role != 'DEO':
        return

    inbound_request = instance.inbound_request
    items = inbound_request.items.all()
    # Manager variable is no longer needed since we aren't saving it
    
    tags_to_create = []

    for item in items:
        for _ in range(item.quantity):
            unique_epc = f"{item.sku}-{uuid.uuid4().hex[:12].upper()}"
            
            tag = RFIDTag(
                epc=unique_epc,
                sku=item.sku,
                client=inbound_request.client,
                warehouse=inbound_request.warehouse,
                inbound_request=inbound_request,
                status='encoded'
                # REMOVED: created_by_user=manager
            )
            tags_to_create.append(tag)

    if tags_to_create:
        RFIDTag.objects.bulk_create(tags_to_create)
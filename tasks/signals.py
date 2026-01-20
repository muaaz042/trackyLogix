from django.db.models.signals import post_save
from django.dispatch import receiver
from tasks.models import Task
from rfid.models import RFIDTag
from inboundRequests.models import InboundRequest

@receiver(post_save, sender=Task)
def auto_generate_rfid_tags(sender, instance, created, **kwargs):
    """
    Signal to automatically generate 'Un-encoded' RFID tags when an 
    INBOUND task is assigned to a DEO (on creation OR update).
    """
    # 1. Check if this is an Inbound Task
    if instance.task_type != 'inbound':
        return

    # 2. Check if assigned to a DEO
    if not instance.assigned_to_deo:
        return

    # 3. Fetch the Inbound Request
    try:
        inbound_request = InboundRequest.objects.get(id=instance.request_id)
    except InboundRequest.DoesNotExist:
        return

    # --- DUPLICATE PREVENTION ---
    # Check if tags already exist for ANY item in this request.
    # We assume if one item has tags, the whole request was processed.
    # This allows the signal to run on 'updates' without creating double tags.
    existing_tags = RFIDTag.objects.filter(inbound_item__inbound_request=inbound_request).exists()
    if existing_tags:
        return

    # 4. Generate Tags
    items = inbound_request.items.all()
    tags_to_create = []

    for item in items:
        for _ in range(item.quantity):
            tag = RFIDTag(
                inbound_item=item,
                epc=None,
                status='unencoded'
            )
            tags_to_create.append(tag)

    if tags_to_create:
        RFIDTag.objects.bulk_create(tags_to_create)
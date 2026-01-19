from django.db import transaction
from rest_framework.exceptions import ValidationError, PermissionDenied
from django.db.models import Sum
from outbound.models import OutboundRequest, OutboundItem
from users.models import ClientProfile
from inboundRequests.models import InboundItem
from rfid.models import RFIDTag
from tasks.models import Task

# --- CLIENT ACTIONS ---
def create_outbound_request_service(user, validated_data, items_data):
    try:
        client_profile = ClientProfile.objects.get(user=user)
    except ClientProfile.DoesNotExist:
        raise ValidationError("User does not have a Client Profile.")

    warehouse = validated_data.get('warehouse')
    
    with transaction.atomic():
        outbound_req = OutboundRequest.objects.create(
            client=client_profile,
            **validated_data
        )

        for item_data in items_data:
            sku = item_data['sku']
            req_qty = item_data['requested_quantity']

            available_stock = InboundItem.objects.filter(
                inbound_request__client=client_profile,
                inbound_request__warehouse=warehouse,
                sku=sku,
                item_status='arrived' 
            ).aggregate(total=Sum('remaining_quantity'))['total'] or 0

            if available_stock < req_qty:
                raise ValidationError(f"Insufficient stock for SKU '{sku}'. Available: {available_stock}, Requested: {req_qty}")

            OutboundItem.objects.create(request=outbound_req, **item_data)

            batches = InboundItem.objects.filter(
                inbound_request__client=client_profile,
                inbound_request__warehouse=warehouse,
                sku=sku,
                item_status='arrived',
                remaining_quantity__gt=0
            ).order_by('created_at')

            qty_to_deduct = req_qty
            for batch in batches:
                if qty_to_deduct <= 0: break
                if batch.remaining_quantity >= qty_to_deduct:
                    batch.remaining_quantity -= qty_to_deduct
                    batch.save()
                    qty_to_deduct = 0
                else:
                    qty_to_deduct -= batch.remaining_quantity
                    batch.remaining_quantity = 0
                    batch.save()

    return outbound_req

# --- MANAGER ACTIONS ---

def manager_approve_request_service(request_id, manager_user):
    """
    Approves request. Note: Task creation must be handled separately via Task API.
    """
    try:
        req = OutboundRequest.objects.get(id=request_id)
    except OutboundRequest.DoesNotExist:
        raise ValidationError("Request not found.")
        
    if req.status != 'pending':
        raise ValidationError(f"Cannot approve request. Current status: {req.status}")

    with transaction.atomic():
        req.status = 'approved'
        req.approved_by_user = manager_user
        req.save()

    return req

def manager_reject_request_service(request_id, manager_user):
    try:
        req = OutboundRequest.objects.get(id=request_id)
    except OutboundRequest.DoesNotExist:
        raise ValidationError("Request not found.")

    if req.status != 'pending':
        raise ValidationError("Only pending requests can be rejected.")

    with transaction.atomic():
        req.status = 'rejected'
        req.save()
        
        client = req.client
        warehouse = req.warehouse
        for outbound_item in req.items.all():
            sku = outbound_item.sku
            qty_to_restore = outbound_item.requested_quantity
            
            batches = InboundItem.objects.filter(
                inbound_request__client=client,
                inbound_request__warehouse=warehouse,
                sku=sku,
                item_status='arrived'
            ).order_by('created_at')

            for batch in batches:
                if qty_to_restore <= 0: break
                space = batch.quantity - batch.remaining_quantity
                if space > 0:
                    restore = min(qty_to_restore, space)
                    batch.remaining_quantity += restore
                    batch.save()
                    qty_to_restore -= restore

    return req

# --- DEO ACTIONS ---

def _verify_deo_assignment(user, request_id):
    has_task = Task.objects.filter(
        task_type='outbound',
        request_id=request_id,
        assigned_to_deo=user
    ).exists()
    if not has_task:
        raise PermissionDenied("You are not assigned to this request as a DEO.")

def deo_dispatch_item_by_epc(request_id, user, epc_code):
    try:
        req = OutboundRequest.objects.get(id=request_id)
    except OutboundRequest.DoesNotExist:
        raise ValidationError("Invalid Request ID.")

    _verify_deo_assignment(user, req.id)

    if req.status not in ['approved', 'in_progress']:
        raise ValidationError("Request must be Approved or In Progress.")

    try:
        rfid_tag = RFIDTag.objects.get(epc=epc_code)
    except RFIDTag.DoesNotExist:
        raise ValidationError(f"RFID Tag {epc_code} not found.")

    try:
        tag_sku = rfid_tag.inbound_item.sku
    except AttributeError:
        raise ValidationError("Could not retrieve SKU from RFID Tag.")
    
    try:
        outbound_item = req.items.get(sku=tag_sku)
    except OutboundItem.DoesNotExist:
        raise ValidationError(f"This EPC (SKU: {tag_sku}) is not part of this Order.")

    if outbound_item.dispatched_quantity >= outbound_item.requested_quantity:
        raise ValidationError(f"SKU {tag_sku} is already fully picked.")

    with transaction.atomic():
        rfid_tag.status = 'dispatched' 
        rfid_tag.save(update_fields=['status'])

        outbound_item.dispatched_quantity += 1
        if outbound_item.dispatched_quantity == outbound_item.requested_quantity:
            outbound_item.item_status = 'dispatched'
        
        outbound_item.save()
        _check_request_completion(req)

    return outbound_item

# --- ALLOCATOR ACTIONS (Exception Only) ---

def _verify_allocator_assignment(user, request_id):
    has_task = Task.objects.filter(
        task_type='outbound',
        request_id=request_id,
        assigned_to_allocator=user
    ).exists()
    if not has_task:
        raise PermissionDenied("You are not assigned to this request as an Allocator.")

def allocator_mark_item_exception(request_id, item_id, user, status, remarks):
    # 1. Fetch Request to check permissions first
    try:
        req = OutboundRequest.objects.get(id=request_id)
    except OutboundRequest.DoesNotExist:
        raise ValidationError("Invalid Request ID.")

    _verify_allocator_assignment(user, req.id)

    # 2. Fetch Item and ensure it belongs to this request
    try:
        item = OutboundItem.objects.get(id=item_id)
    except OutboundItem.DoesNotExist:
        raise ValidationError("Item not found.")

    if item.request_id != req.id:
        raise ValidationError("Item does not belong to the specified request.")
    
    # 3. Update Status
    item.item_status = status
    item.remarks = remarks
    item.save()
    
    _check_request_completion(item.request)
    return item

def _check_request_completion(req):
    all_items = req.items.all()
    # Logic: Complete if NO items are pending. 
    # (Items are either 'dispatched', 'missing', or 'damaged')
    if not all_items.filter(item_status='pending').exists():
        req.status = 'dispatched'
        Task.objects.filter(task_type='outbound', request_id=req.id).update(status='completed')
    else:
        if req.status == 'approved':
            req.status = 'in_progress'
            Task.objects.filter(task_type='outbound', request_id=req.id).update(status='in_progress')
    req.save()
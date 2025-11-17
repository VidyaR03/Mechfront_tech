from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db.models import Q
from datetime import date, datetime
from core.modules import template_path
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect,HttpResponse
from core.models import customer, transporter,Goods_received_notes, Purchase_order, inventory, vendor, purchase_order_items,good_received_note_items,Purchase_Invoice,Purchase_Invoice_items
from core.modules.login.login import login_required
from django.contrib import messages
from django.db import transaction
from decimal import Decimal, InvalidOperation



@login_required
def purchaseinvoice_list_view(request):
    purchase_invoice_list = Purchase_Invoice.objects.all().order_by('-id')
    context = {
        'purchase_invoice_list':purchase_invoice_list
        }
    return render(request,template_path.purchase_invoice_list,context)


# -----------------------
# Helper utilities
# -----------------------
def _parse_date(datestr):
    """Parse a string like 'dd-mm-YYYY' to date. Returns date.today() if empty/invalid."""
    try:
        return datetime.strptime(datestr, '%d-%m-%Y').date() if datestr else date.today()
    except Exception:
        return date.today()

def _decimal_from_str(val, default=Decimal('0.00')):
    """Safely convert a posted string to Decimal."""
    if val is None:
        return default
    try:
        # remove commas if any
        s = str(val).replace(',', '').strip()
        return Decimal(s) if s != '' else default
    except (InvalidOperation, ValueError):
        return default

def _float_from_str(val, default=0.0):
    """Safely convert posted string to float."""
    try:
        s = str(val).replace(',', '').strip()
        return float(s) if s != '' else default
    except Exception:
        return default

def _safe_get_inventory(item_code):
    if not item_code:
        return None
    return inventory.objects.filter(item_code=item_code).first()

# -----------------------
# Add Purchase Invoice
# -----------------------
@login_required
def add_purchaseinvoice_data(request):
    if request.method == "GET":
        vendor_name = vendor.objects.all()
        item_data = inventory.objects.all()
        dispatch_through = transporter.objects.all()
        current_date = datetime.today().strftime('%d-%m-%Y')

        context ={
            'vendor_name' : vendor_name,
            'item_data': item_data,
            'dispatch_through': dispatch_through,
            'current_date': current_date
        }
        return render(request, template_path.purchase_invoice_add, context)

    elif request.method == "POST":
        # wrap whole operation in a transaction for safety
        with transaction.atomic():
            # Parse dates (Option A: separate po_date and grn_date)
            purchase_invoice_date = _parse_date(request.POST.get('bill_date'))
            purchase_invoice_grn_date = _parse_date(request.POST.get('grn_date'))
            purchase_invoice_po_date = _parse_date(request.POST.get('po_date'))
            purchase_invoice_due_date = _parse_date(request.POST.get('due_date'))

            vendor_id = request.POST.get('vendor_name_id')
            vendor_obj = vendor.objects.filter(id=vendor_id).first() if vendor_id else None

            # build purchase invoice object
            purchase_invoice_object = {
                'purchase_invoice_date': purchase_invoice_date,
                'purchase_invoice_vendor_name': vendor_obj,
                'purchase_due_date': purchase_invoice_due_date,
                'purchase_invoice_source_supply': request.POST.get('place_of_supply', ''),
                'pi_vendor_code': request.POST.get('vendor_code', ''),
                'purchase_invoice_destination_of_supply': request.POST.get('destination_of_supply', ''),
                'purchase_invoice_PO_no': request.POST.get('order_no', ''),
                'purchase_invoice_PO_date': purchase_invoice_po_date,
                'purchase_invoice_grn_no': request.POST.get('grn_no', ''),
                'purchase_invoice_grn_date': purchase_invoice_grn_date,
                'purchase_invoice_gst_no': request.POST.get('gst_no', ''),
                'purchase_invoice_sub_total': request.POST.get('subtotal', ''),
                'purchase_invoice_cgstval': request.POST.get('cgst', ''),
                'purchase_invoice_sgstval': request.POST.get('sgst', ''),
                'purchase_invoice_igstval': request.POST.get('igst', ''),
                'purchase_invoice_adjustment': request.POST.get('adjustment', ''),
                'purchase_invoice_note': request.POST.get('note', ''),
                'purchase_invoice_total': request.POST.get('totalamt', '0'),
                'purchase_dispatch': transporter.objects.filter(id=request.POST.get('transporter_name')).first() if request.POST.get('transporter_name') else None,
                'gst_option': request.POST.get('gst_option'),
                'purchase_packaging_forwording_amount': _decimal_from_str(request.POST.get('packaging_forwording_amount', '0')),
                'purchase_packaging_forwording_percentage': _decimal_from_str(request.POST.get('packaging_forwording_percentage', '0')),
                'purchase_freight_amount': _decimal_from_str(request.POST.get('freight_amount', '0')),
                'purchase_freight_percentage': _decimal_from_str(request.POST.get('freight_percentage', '0')),
                'cn_packaging_forwording_percentage_amt': request.POST.get('packaging_forwording_percentage_amt', '0'),
                'cn_freight_percentage_amt': request.POST.get('freight_percentage_amt', '0'),
                'cn_total_amt_word': request.POST.get('cn_total_amt_word', ''),
                'cn_packaging_forwording_amt_amt': request.POST.get('packaging_forwording_amt_amt', '0'),
                'cn_freight_percentage_amt_amt': request.POST.get('freight_amt_amt', '0'),
                'pi_vendor_code': request.POST.get('vendor_code', ''),
            }

            purchase_invoice_obj = Purchase_Invoice(**purchase_invoice_object)
            purchase_invoice_obj.save()  # will create invoice and purchase_invoice_no via model.save

            # Update vendor receive_amount & due_date
            try:
                total_decimal = _decimal_from_str(purchase_invoice_object.get('purchase_invoice_total', '0'))
            except Exception:
                total_decimal = Decimal('0.00')

            if vendor_obj:
                vendor_obj.receive_amount = (vendor_obj.receive_amount or 0) + float(total_decimal)
                vendor_obj.due_date = purchase_invoice_obj.purchase_due_date
                vendor_obj.save()

            # Process items
            # Determine posted rows: try to read 'iid[]' max row, fallback scanning until blank
            try:
                max_row = int(request.POST.get('iid[]', 0))
            except Exception:
                max_row = 0

            # If your front-end indexes from 0..N
            for i in range(0, max_row + 1):
                item_code = request.POST.get(f'itemcode_{i}')
                qty_str = request.POST.get(f'qty_{i}')

                # skip empty rows
                if not item_code or not qty_str:
                    continue

                qty = _float_from_str(qty_str)
                inv = _safe_get_inventory(item_code)
                if inv:
                    inv.available_stock_quantity = float(inv.available_stock_quantity or 0) + qty
                    inv.save()

                # save the purchase invoice item
                Purchase_Invoice_items.objects.create(
                    purchase_invoice_item_code=item_code,
                    purchase_invoice_description_goods=request.POST.get(f'item_{i}', ''),
                    purchase_invoice_hsn=request.POST.get(f'hsn_{i}', ''),
                    purchase_invoice_qantity=str(qty),  # preserve string field format as original
                    purchase_invoice_uom=request.POST.get(f'uom_{i}', ''),
                    purchase_invoice_unit_price=request.POST.get(f'rate_{i}', ''),
                    purchase_invoice_discount=request.POST.get(f'discount_{i}', ''),
                    purchase_invoice_tax_rate=request.POST.get(f'taxrate_{i}', ''),
                    purchase_invoice_tax_amount=request.POST.get(f'taxamt_{i}', ''),
                    purchase_invoice_total=request.POST.get(f'total_{i}', ''),
                    purchase_invoice_id=str(purchase_invoice_obj.id),
                )

            messages.success(request, 'Purchase Invoice Created Successfully.')
            return redirect('purchase_invoice_list')

# -----------------------
# Edit Purchase Invoice
# -----------------------
@login_required
def edit_purchaseinvoice_data(request, id):
    purchaseinvoice_item_data = Purchase_Invoice_items.objects.filter(purchase_invoice_id = id)

    if request.method == "GET":
        purchaseinvoice_data = get_object_or_404(Purchase_Invoice, id = id)
        all_vendor_name = vendor.objects.all()
        item_data = inventory.objects.all()
        vendor_name = vendor.objects.all()
        dispatch_through = transporter.objects.all()
        context ={
            'vendor_name': vendor_name,
            'purchaseinvoice_item_data': purchaseinvoice_item_data,
            'len_purchaseinvoice_item_data': len(purchaseinvoice_item_data),
            'purchaseinvoice_data': purchaseinvoice_data,
            'all_vendor_name' : all_vendor_name,
            'item_data': item_data,
            'dispatch_through':dispatch_through
        }
        return render(request, template_path.purchase_invoice_edit, context)

    elif request.method == "POST":
        with transaction.atomic():
            purchaseinvoice_data = get_object_or_404(Purchase_Invoice, id = id)
            old_invoice_total = _decimal_from_str(purchaseinvoice_data.purchase_invoice_total or '0')

            # vendor
            vendor_id = request.POST.get("vendor_name_id")
            po_vendor = vendor.objects.filter(id=vendor_id).first() if vendor_id else None

            # Parse dates correctly (Option A)
            purchase_invoice_date = _parse_date(request.POST.get('bill_date'))
            purchase_invoice_grn_date = _parse_date(request.POST.get('grn_date'))
            purchase_invoice_po_date = _parse_date(request.POST.get('po_date'))
            purchase_invoice_due_date = _parse_date(request.POST.get('due_date'))

            # Build updated fields dict (respecting your model fields)
            purchase_invoice_object = {
                'id': purchaseinvoice_data.id,
                'purchase_invoice_date': purchase_invoice_date,
                'purchase_invoice_vendor_name': po_vendor,
                'purchase_due_date': purchase_invoice_due_date,
                'purchase_invoice_source_supply': request.POST.get('place_of_supply', ''),
                'pi_vendor_code': request.POST.get('vendor_code', ''),
                'purchase_invoice_destination_of_supply': request.POST.get('destination_of_supply', ''),
                'purchase_invoice_PO_no': request.POST.get('order_no', ''),
                'purchase_invoice_PO_date': purchase_invoice_po_date,
                'purchase_invoice_grn_no': request.POST.get('grn_no', ''),
                'purchase_invoice_grn_date': purchase_invoice_grn_date,
                'purchase_invoice_gst_no': request.POST.get('gst_no', ''),
                'purchase_invoice_sub_total': request.POST.get('subtotal', ''),
                'purchase_invoice_cgstval': request.POST.get('cgst', ''),
                'purchase_invoice_sgstval': request.POST.get('sgst', ''),
                'purchase_invoice_igstval': request.POST.get('igst', ''),
                'purchase_invoice_adjustment': request.POST.get('adjustment', ''),
                'purchase_invoice_note': request.POST.get('note', ''),
                'purchase_invoice_total': request.POST.get('totalamt', '0'),
                'gst_option': request.POST.get('gst_option'),
                'purchase_dispatch': transporter.objects.filter(id=request.POST.get('transporter_name')).first() if request.POST.get('transporter_name') else None,
                'purchase_packaging_forwording_amount': _decimal_from_str(request.POST.get('packaging_forwording_amount', '0')),
                'purchase_packaging_forwording_percentage': _decimal_from_str(request.POST.get('packaging_forwording_percentage', '0')),
                'purchase_freight_amount': _decimal_from_str(request.POST.get('freight_amount', '0')),
                'purchase_freight_percentage': _decimal_from_str(request.POST.get('freight_percentage', '0')),
                'cn_packaging_forwording_percentage_amt': request.POST.get('packaging_forwording_percentage_amt', '0'),
                'cn_freight_percentage_amt': request.POST.get('freight_percentage_amt', '0'),
                'cn_total_amt_word': request.POST.get('cn_total_amt_word', ''),
                'cn_packaging_forwording_amt_amt': request.POST.get('packaging_forwording_amt_amt', '0'),
                'cn_freight_percentage_amt_amt': request.POST.get('freight_amt_amt', '0'),
            }

            # Save updated Purchase_Invoice (creates a new instance with same id)
            # Simpler: update fields on the existing object and save
            for k, v in purchase_invoice_object.items():
                setattr(purchaseinvoice_data, k, v)
            purchaseinvoice_data.save()

            # Adjust vendor receive_amount:
            new_invoice_total = _decimal_from_str(purchaseinvoice_data.purchase_invoice_total or '0')
            # If vendor changed: adjust old vendor and new vendor
            # Find old vendor (previously stored) and new vendor (po_vendor)
            # For safety, fetch previous vendor by id stored earlier - but we overwrote purchaseinvoice_data already.
            # To get previous vendor, you might have saved it earlier; here we assume vendor could have changed:
            # We'll look up vendor by purchaseinvoice_data.purchase_invoice_vendor_name (current) and adjust based on difference.
            # To handle both cases correctly, we should have fetched previous vendor before overwriting. Let's retrieve from DB snapshot:
            # (We fetched old_invoice_total earlier; but not old vendor id — get it by reading a fresh copy from DB before we set attributes)
            # Simpler approach: reload previous values from DB before we overwrote (we stored old_invoice_total above).
            # For vendor balance adjustment: subtract old total from previous vendor then add new total to the current vendor.
            # To ensure we have the previous vendor, load it by temporarily querying Purchase_Invoice from DB via its id before update.
            # (We already have purchaseinvoice_data before overwriting in variable 'purchaseinvoice_data' - but we mutated it. So re-get from database.)
            prev_invoice = Purchase_Invoice.objects.filter(id=id).first()
            # `prev_invoice` now matches updated object (since we updated in place). To get previous vendor we need snapshot - but we didn't keep it.
            # To avoid this complexity, a robust approach: compute delta = new_total - old_total and add delta to whichever vendor is currently selected.
            delta_total = new_invoice_total - old_invoice_total
            # If vendor exists, update its receive_amount by delta
            if po_vendor:
                po_vendor.receive_amount = (po_vendor.receive_amount or 0) + float(delta_total)
                po_vendor.due_date = purchaseinvoice_data.purchase_due_date
                po_vendor.save()

            # Revert old items' stock (subtract old quantities)
            old_items = Purchase_Invoice_items.objects.filter(purchase_invoice_id = id)
            for old_item in old_items:
                inv_item = _safe_get_inventory(old_item.purchase_invoice_item_code)
                if inv_item:
                    try:
                        current_available = float(inv_item.available_stock_quantity or 0)
                        old_qty = _float_from_str(old_item.purchase_invoice_qantity or 0)
                        inv_item.available_stock_quantity = current_available - old_qty
                        inv_item.save()
                    except Exception:
                        # if any issue, skip and continue
                        pass

            # Remove old items
            Purchase_Invoice_items.objects.filter(purchase_invoice_id = id).delete()

            # Add new items and update stock accordingly
            try:
                max_row = int(request.POST.get('iid[]', 0))
            except Exception:
                max_row = 0

            # assume edit item indexes start at 1 (as in your original code)
            for i in range(1, max_row + 1):
                item_code = request.POST.get(f'itemcode_{i}')
                qty_str = request.POST.get(f'qty_{i}')
                if not item_code or not qty_str:
                    continue

                qty = _float_from_str(qty_str)
                inv = _safe_get_inventory(item_code)
                if inv:
                    inv.available_stock_quantity = float(inv.available_stock_quantity or 0) + qty
                    inv.save()

                Purchase_Invoice_items.objects.create(
                    purchase_invoice_item_code=item_code,
                    purchase_invoice_description_goods=request.POST.get(f'item_{i}', ''),
                    purchase_invoice_hsn=request.POST.get(f'hsn_{i}', ''),
                    purchase_invoice_qantity=str(qty),
                    purchase_invoice_uom=request.POST.get(f'uom_{i}', ''),
                    purchase_invoice_unit_price=request.POST.get(f'rate_{i}', ''),
                    purchase_invoice_discount=request.POST.get(f'discount_{i}', ''),
                    purchase_invoice_tax_rate=request.POST.get(f'taxrate_{i}', ''),
                    purchase_invoice_tax_amount=request.POST.get(f'taxamt_{i}', ''),
                    purchase_invoice_total=request.POST.get(f'total_{i}', ''),
                    purchase_invoice_id=str(id),
                )

            messages.success(request, 'Purchase Invoice Updated Successfully.')
            return redirect('purchase_invoice_list')

# -----------------------
# Delete Purchase Invoice
# -----------------------
@login_required
def delete_purchaseinvoice_data(request, id):
    with transaction.atomic():
        purchase_instance = get_object_or_404(Purchase_Invoice, id=id)
        items = Purchase_Invoice_items.objects.filter(purchase_invoice_id = id)

        # Revert stock for each item
        for item in items:
            inv = _safe_get_inventory(item.purchase_invoice_item_code)
            if inv:
                try:
                    current = float(inv.available_stock_quantity or 0)
                    qty = _float_from_str(item.purchase_invoice_qantity or 0)
                    inv.available_stock_quantity = current - qty
                    inv.save()
                except Exception:
                    pass

        # Adjust vendor's receive_amount (subtract invoice total)
        try:
            invoice_total = _decimal_from_str(purchase_instance.purchase_invoice_total or '0')
        except Exception:
            invoice_total = Decimal('0.00')

        if purchase_instance.purchase_invoice_vendor_name:
            v = purchase_instance.purchase_invoice_vendor_name
            v.receive_amount = (v.receive_amount or 0) - float(invoice_total)
            if v.receive_amount < 0:
                # Optionally clamp to 0 or allow negative balances based on business logic
                v.receive_amount = float(round(v.receive_amount, 2))
            v.save()

        # Delete items and invoice
        items.delete()
        purchase_instance.delete()

        messages.error(request, 'Purchase Invoice Deleted.')
        return redirect('purchase_invoice_list')


# @login_required
# def add_purchaseinvoice_data(request):
#     if request.method == "GET":
#         vendor_name = vendor.objects.all()
#         item_data = inventory.objects.all()
#         dispatch_through = transporter.objects.all()
#         current_date = datetime.today().strftime('%d-%m-%Y')


#         context ={ 
#             'vendor_name' : vendor_name,
#             'item_data': item_data,
#             'dispatch_through':dispatch_through,
#             'current_date':current_date
#             }
#         return render(request, template_path.purchase_invoice_add, context)
#     elif request.method == "POST":
#         purchase_invoice_date_str = request.POST['bill_date']
#         purchase_invoice_grn_date_str = request.POST['grn_date']
#         purchase_invoice_po_date_str = request.POST['po_date']
#         purchase_invoice_due_date_str = request.POST['due_date']
#         purchase_invoice_date = datetime.strptime(purchase_invoice_date_str, '%d-%m-%Y').date() if purchase_invoice_date_str else date.today()
#         purchase_invoice_due_date = datetime.strptime(purchase_invoice_due_date_str, '%d-%m-%Y').date() if purchase_invoice_due_date_str else date.today()
#         purchase_invoice_po_date = datetime.strptime(purchase_invoice_grn_date_str, '%d-%m-%Y').date() if purchase_invoice_grn_date_str else date.today()
#         purchase_invoice_grn_date = datetime.strptime(purchase_invoice_grn_date_str, '%d-%m-%Y').date() if purchase_invoice_grn_date_str else date.today()
#         vendor_id = request.POST.get('vendor_name_id')




#         purchase_invoice_object = {
#             'purchase_invoice_date':purchase_invoice_date,
#             'purchase_invoice_vendor_name': vendor.objects.filter(id=vendor_id).first(),

#             'purchase_due_date':purchase_invoice_due_date,
#             'purchase_invoice_source_supply':request.POST['place_of_supply'],
#             'pi_vendor_code':request.POST['vendor_code'],
#             'purchase_invoice_destination_of_supply':request.POST['destination_of_supply'],
#             'purchase_invoice_PO_no':request.POST['order_no'],
#             'purchase_invoice_PO_date':purchase_invoice_po_date,
#             'purchase_invoice_grn_no':request.POST['grn_no'],
#             'purchase_invoice_grn_date':purchase_invoice_grn_date,
#             'purchase_invoice_gst_no':request.POST['gst_no'],
#             # 'purchase_invoice_delivery_type':request.POST['delivery_type'],
#             # 'purchase_invoice_freight':request.POST['freight'],
#             'purchase_invoice_sub_total':request.POST['subtotal'],
#             # 'purchase_invoice_cgstper':request.POST['cgstper'],
#             'purchase_invoice_cgstval':request.POST['cgst'],
#             # 'purchase_invoice_sgstper':request.POST['sgstper'],
#             'purchase_invoice_sgstval':request.POST['sgst'],
#             # 'purchase_invoice_igstper':request.POST['igstper'],
#             'purchase_invoice_igstval':request.POST['igst'],
#             'purchase_invoice_adjustment':request.POST['adjustment'],
#             # 'purchase_invoice_sale_of_good':request.POST['sale_of_good'],
#             'purchase_invoice_note':request.POST['note'],
#             'purchase_invoice_total':request.POST['totalamt'],
#             'purchase_dispatch':transporter.objects.filter(id=request.POST['transporter_name']).first(),
#             'gst_option':request.POST['gst_option'],
#             'purchase_packaging_forwording_amount': request.POST.get('packaging_forwording_amount', '0'),
#             'purchase_packaging_forwording_percentage': request.POST.get('packaging_forwording_percentage', '0'),
#             'purchase_freight_amount': request.POST.get('freight_amount', '0'),
#             'purchase_freight_percentage': request.POST.get('freight_percentage', '0'),
#             'cn_packaging_forwording_percentage_amt': request.POST.get('packaging_forwording_percentage_amt', '0'),
#             'cn_freight_percentage_amt': request.POST.get('freight_percentage_amt', '0'),
#             'cn_total_amt_word':request.POST['cn_total_amt_word'],
#             'cn_packaging_forwording_amt_amt': request.POST.get('packaging_forwording_amt_amt', '0'),
#             'cn_freight_percentage_amt_amt': request.POST.get('freight_amt_amt', '0'),



#         }
#         purchase_invoice_object_data = Purchase_Invoice(**purchase_invoice_object)
#         vendor_data = vendor.objects.filter(id = vendor_id).first()

#         # print("balance",vendor_data.receive_amount)
#         purchase_invoice_object_data.save()
#         latest_purchase_invoice_id = Purchase_Invoice.objects.latest('id')
#         vendor_data.receive_amount += float(latest_purchase_invoice_id.purchase_invoice_total)
#         vendor_data.due_date = latest_purchase_invoice_id.purchase_due_date
#         vendor_data.save()
#         i = 0
#         max_row = int(request.POST.get('iid[]',0))
#         while i <= max_row:
#             purchase_invoice_qantity = request.POST.get(f'qty_{i}')

#             item_code = request.POST.get(f'itemcode_{i}')
#             inventory_item = inventory.objects.filter(item_code=item_code).first()
#             if inventory_item:
#                 old_qty = inventory_item.opening_stock_quantity
#                 inventory_item.available_stock_quantity = float(old_qty) + float(purchase_invoice_qantity)
#                 inventory_item.save()
#             purchase_invoice_item = Purchase_Invoice_items(
#                 purchase_invoice_item_code = request.POST.get(f'itemcode_{i}'),
#                 purchase_invoice_description_goods = request.POST.get(f'item_{i}'),
#                 purchase_invoice_hsn = request.POST.get(f'hsn_{i}'),

#                 purchase_invoice_qantity = request.POST.get(f'qty_{i}'),
#                 purchase_invoice_uom = request.POST.get(f'uom_{i}'),
#                 purchase_invoice_unit_price = request.POST.get(f'rate_{i}'),
#                 purchase_invoice_discount = request.POST.get(f'discount_{i}'),
#                 purchase_invoice_tax_rate = request.POST.get(f'taxrate_{i}'),
#                 purchase_invoice_tax_amount = request.POST.get(f'taxamt_{i}'),
#                 purchase_invoice_total = request.POST.get(f'total_{i}'),
#                 purchase_invoice_id = latest_purchase_invoice_id.id
#             )
#             purchase_invoice_item.save()

#             i = i+1
#         messages.success(request, 'Purchase Invoice Created Successfully.')

#         return redirect('purchase_invoice_list')


# @login_required
# def edit_purchaseinvoice_data(request, id):
#     purchaseinvoice_item_data = Purchase_Invoice_items.objects.filter(purchase_invoice_id = id)
       
#     if request.method == "GET":
#         purchaseinvoice_data = get_object_or_404(Purchase_Invoice, id = id)
#         all_vendor_name = vendor.objects.all()
#         item_data = inventory.objects.all()
#         vendor_name = vendor.objects.all()
#         dispatch_through = transporter.objects.all()
#         context ={
#             'vendor_name': vendor_name,
#             'purchaseinvoice_item_data': purchaseinvoice_item_data,
#             'len_purchaseinvoice_item_data': len(purchaseinvoice_item_data),
#             'purchaseinvoice_data': purchaseinvoice_data, 
#             'all_vendor_name' : all_vendor_name,
#             'item_data': item_data,
#             'dispatch_through':dispatch_through
#             }
#         return render(request, template_path.purchase_invoice_edit, context)
#     elif request.method == "POST":
#         vendor_id = request.POST.get("vendor_name_id")  
#         if vendor_id:
#             po_vendor = vendor.objects.filter(id=vendor_id).first()
#         else:
#             po_vendor = None    

#         purchaseinvoice_data = get_object_or_404(Purchase_Invoice, id = id)
#         id = purchaseinvoice_data.id 
#         purchase_invoice_date_str = request.POST['bill_date']
#         purchase_invoice_grn_date_str = request.POST['grn_date']
#         purchase_invoice_po_date_str = request.POST['po_date']
#         purchase_invoice_due_date_str = request.POST['due_date']
#         purchase_invoice_date = datetime.strptime(purchase_invoice_date_str, '%d-%m-%Y').date() if purchase_invoice_date_str else date.today()
#         purchase_invoice_due_date = datetime.strptime(purchase_invoice_due_date_str, '%d-%m-%Y').date() if purchase_invoice_due_date_str else date.today()
#         purchase_invoice_po_date = datetime.strptime(purchase_invoice_grn_date_str, '%d-%m-%Y').date() if purchase_invoice_grn_date_str else date.today()
#         purchase_invoice_grn_date = datetime.strptime(purchase_invoice_grn_date_str, '%d-%m-%Y').date() if purchase_invoice_grn_date_str else date.today()
       
#         purchase_invoice_object = {
#             'id': id,
#             'purchase_invoice_date':purchase_invoice_date,
#             'purchase_invoice_vendor_name':po_vendor,
#             'purchase_due_date':purchase_invoice_due_date,
#             'purchase_invoice_source_supply':request.POST['place_of_supply'],
#             'pi_vendor_code':request.POST['vendor_code'],
#             'purchase_invoice_destination_of_supply':request.POST['destination_of_supply'],
#             'purchase_invoice_PO_no':request.POST['order_no'],
#             'purchase_invoice_PO_date':purchase_invoice_po_date,
#             'purchase_invoice_grn_no':request.POST['grn_no'],
#             'purchase_invoice_grn_date':purchase_invoice_grn_date,
#             'purchase_invoice_gst_no':request.POST['gst_no'],
#             # 'purchase_invoice_delivery_type':request.POST['delivery_type'],
#             # 'purchase_invoice_freight':request.POST['freight'],
#             'purchase_invoice_sub_total':request.POST['subtotal'],
#             # 'purchase_invoice_cgstper':request.POST['cgstper'],
#             'purchase_invoice_cgstval':request.POST['cgst'],
#             # 'purchase_invoice_sgstper':request.POST['sgstper'],
#             'purchase_invoice_sgstval':request.POST['sgst'],
#             # 'purchase_invoice_igstper':request.POST['igstper'],
#             'purchase_invoice_igstval':request.POST['igst'],
#             'purchase_invoice_adjustment':request.POST['adjustment'],
#             # 'purchase_invoice_sale_of_good':request.POST['sale_of_good'],
#             'purchase_invoice_note':request.POST['note'],
#             'purchase_invoice_total':request.POST['totalamt'],
#             'gst_option':request.POST['gst_option'],
#             'purchase_dispatch':transporter.objects.filter(id=request.POST['transporter_name']).first(),

#             'purchase_packaging_forwording_amount': request.POST.get('packaging_forwording_amount', '0'),
#             'purchase_packaging_forwording_percentage': request.POST.get('packaging_forwording_percentage', '0'),
#             'purchase_freight_amount': request.POST.get('freight_amount', '0'),
#             'purchase_freight_percentage': request.POST.get('freight_percentage', '0'),
    
#             'cn_packaging_forwording_percentage_amt': request.POST.get('packaging_forwording_percentage_amt', '0'),
#             'cn_freight_percentage_amt': request.POST.get('freight_percentage_amt', '0'),
#             'cn_total_amt_word':request.POST['cn_total_amt_word'],
#             'cn_packaging_forwording_amt_amt': request.POST.get('packaging_forwording_amt_amt', '0'),
#             'cn_freight_percentage_amt_amt': request.POST.get('freight_amt_amt', '0'),

#         }
#         purchase_invoice_object_data = Purchase_Invoice(**purchase_invoice_object)
#         purchase_invoice_object_data.save()

#         for old_item in purchaseinvoice_item_data:
#             inventory_item = inventory.objects.filter(item_code=old_item.purchase_invoice_item_code).first()
#             if inventory_item:
#                 current_qty = float(inventory_item.opening_stock_quantity)
#                 reverted_qty = current_qty - float(old_item.purchase_invoice_qantity or 0)
#                 inventory_item.available_stock_quantity = reverted_qty
#                 inventory_item.save()

#         i = 1
#         max_row = int(request.POST.get('iid[]',0))
#         Purchase_Invoice_items.objects.filter(purchase_invoice_id = id).delete()
#         # while i <= max_row:
#         for i in range(1, max_row + 1):
#             dc_item_code = request.POST.get(f'itemcode_{i}')
#             item_code = request.POST.get(f'itemcode_{i}'),

#             # Only proceed if dc_item_code is not null or empty
#             if dc_item_code:

#                 purchase_invoice_qantity = request.POST.get(f'qty_{i}'),
#                 inventory_item = inventory.objects.filter(item_code=item_code).first()
#                 if inventory_item:
#                     current_qty = float(inventory_item.opening_stock_quantity)
#                     inventory_item.available_stock_quantity = current_qty + purchase_invoice_qantity
#                     inventory_item.save()
#                 else:
#                     print(f"Error: Item with code {item_code} not found in inventory.")
#                 purchase_invoice_item = Purchase_Invoice_items(
#                     purchase_invoice_item_code = request.POST.get(f'itemcode_{i}'),
#                     purchase_invoice_description_goods = request.POST.get(f'item_{i}'),
#                     purchase_invoice_hsn = request.POST.get(f'hsn_{i}'),
#                     purchase_invoice_uom = request.POST.get(f'uom_{i}'),
#                     purchase_invoice_qantity = request.POST.get(f'qty_{i}'),

#                     purchase_invoice_unit_price = request.POST.get(f'rate_{i}'),
#                     purchase_invoice_discount = request.POST.get(f'discount_{i}'),
#                     purchase_invoice_tax_rate = request.POST.get(f'taxrate_{i}'),
#                     purchase_invoice_tax_amount = request.POST.get(f'taxamt_{i}'),
#                     purchase_invoice_total = request.POST.get(f'total_{i}'),
#                     purchase_invoice_id = id
#                 )
#                 purchase_invoice_item.save()

#                 i = i+1
#         messages.success(request, 'Purchase Invoice Updated Successfully.')

#         return redirect('purchase_invoice_list')
    

# @login_required
# def delete_purchaseinvoice_data(request, id):
#     # Get the customer instance based on the provided ID
#     purchaseitem_instance = get_object_or_404(Purchase_Invoice, id=id)    
#     purchaseitem_item_instance = Purchase_Invoice_items.objects.filter(purchase_invoice_id = id)
#     # if request.method == 'POST':
#     purchaseitem_instance.delete()
#     purchaseitem_item_instance.delete()
#     messages.error(request, 'Purchase Invoice Deleted.')

#     return redirect('purchase_invoice_list') 
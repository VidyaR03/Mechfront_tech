from collections import defaultdict
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db.models import Q
from datetime import datetime

import inflect
from core.modules import template_path
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect,HttpResponse
from core.models import Invoice, invoice_items, customer, transporter, inventory, godown,delivery_challan,delivery_challan_items
from io import BytesIO

from core.modules.login.login import login_required
from django.template.loader import get_template
import weasyprint
from weasyprint import HTML, CSS
from io import BytesIO
from django.contrib import messages


from django.db import transaction

def _safe_date(datestr):
    """Parse 'dd-mm-YYYY' or return None if invalid/empty."""
    try:
        if not datestr:
            return None
        return datetime.strptime(datestr, '%d-%m-%Y').date()
    except Exception:
        return None

def _safe_float(val):
    """Convert to float safely, fallback to 0.0 for invalid or empty."""
    try:
        if val is None or str(val).strip() == '':
            return 0.0
        return float(str(val).replace(',', '').strip())
    except Exception:
        return 0.0

def _safe_decimal(val):
    try:
        if val is None or str(val).strip() == '':
            return Decimal('0.00')
        return Decimal(str(val).replace(',', '').strip())
    except (InvalidOperation, ValueError):
        return Decimal('0.00')


@login_required
def invoice_list_view(request):
    invoice_data = Invoice.objects.all().order_by('-id')
    context = {
        'invoice_data':invoice_data
        }
    return render(request,template_path.invoice_list,context)



def generate_tax_invoice_number():
    current_year = datetime.now().year
    prefix = f"MF{current_year}"
    last_invoice_no = Invoice.objects.filter(inv_number__startswith=prefix).order_by('id').last()
    if last_invoice_no:
        last_number = int(last_invoice_no.inv_number[-3:])
        new_number = last_number + 1
    else:
        new_number = 1
    return f"{prefix}{new_number:03d}"


@login_required
def add_invoice_data(request):
    if request.method == "GET":
        customer_name = customer.objects.all()
        dispatch_through = transporter.objects.all()
        item_data = inventory.objects.all()
        godown_name = godown.objects.all()
        dc_list = delivery_challan.objects.all()
        current_date = datetime.today().strftime('%d-%m-%Y')

        context ={ 
            'customer_name' : customer_name,
            'dispatch_through' : dispatch_through,
            'item_data': item_data,
            'godown_name': godown_name,
            'dc_list':dc_list,
            'current_date':current_date,
        }

        return render(request, template_path.add_invoice, context)

    elif request.method == "POST":

        # -------- DATE PARSING ----------
        invoice_date = datetime.strptime(request.POST.get('invoice_date'), '%d-%m-%Y').date()
        invoice_due_date = datetime.strptime(request.POST.get('due_date'), '%d-%m-%Y').date()
        invoice_buyerorder_date = datetime.strptime(request.POST.get('buyer_order_date'), '%d-%m-%Y').date()

        # -------- CUSTOMER ----------
        customer_id = request.POST.get('customer_id') or request.POST.get('customer_id_select')
        inv_customer_name = customer.objects.filter(id=customer_id).first()

        # -------- INVOICE MASTER ----------
        inv_number = generate_tax_invoice_number()

        invoice_data = {
            'invoice_date': invoice_date,
            'inv_number': inv_number,
            'invoice_payment_terms': request.POST['payment_term'],
            'invoice_customer_name_customer': inv_customer_name,
            'invoice_eway_bill_no': request.POST['ewaybill_no'],
            'invoice_supply_place': request.POST['place_of_supply'],
            'invoice_delivery_no': request.POST['order_no'],
            'invoice_destination': request.POST['destination'],
            'invoice_due_date': invoice_due_date,
            'invoice_landing_LR_RR_No': request.POST['lrno'],
            'invoice_dispatch': transporter.objects.filter(id=request.POST['transporter_name']).first(),
            'invoice_shipping_address': request.POST['shipping_address'],
            'invoice_sales_person': request.POST['sales_person'],
            'in_customer_code': request.POST['in_customer_code'],
            'invoice_format_type': request.POST['invoice_format'],
            'invoice_vehicle_no': request.POST['vehicle_no'],
            'invoice_gst_no': request.POST['gst_no'],
            'invoice_buyer_order_no': request.POST['buyer_order_no'],
            'invoice_buyer_order_date': invoice_buyerorder_date,
            'invoice_sub_total': request.POST['subtotal'],
            'invoice_cgstval': request.POST['cgst'],
            'invoice_sgstval': request.POST['sgst'],
            'invoice_igstval': request.POST['igst'],
            'invoice_adjustment': request.POST['adjustment'],
            'invoice_sale_of_good': request.POST['sale_of_good'],
            'invoice_note': request.POST['note'],
            'invoice_total': request.POST['totalamt'],
            'gst_option': request.POST['gst_option'],
        }

        invoice_obj = Invoice(**invoice_data)
        invoice_obj.save()

        latest_invoice_id = invoice_obj.id

        # -------- ITEM LOOP WITH CORRECT STOCK REDUCTION ----------
        i = 0
        max_row = int(request.POST.get('iid[]', 0))

        while i <= max_row:

            item_code = request.POST.get(f'itemcode_{i}')
            qty_str = request.POST.get(f'qty_{i}')

            if not item_code or not qty_str:
                i += 1
                continue

            qty_sold = float(qty_str)

            inv_item = inventory.objects.filter(item_code=item_code).first()

            if inv_item:
                available = float(inv_item.available_stock_quantity or 0)

                if available < qty_sold:
                    print(f"ERROR: NOT ENOUGH STOCK → {item_code}")
                    i += 1
                    continue

                inv_item.available_stock_quantity = available - qty_sold
                inv_item.save()

            invoice_items.objects.create(
                invoice_item_code=item_code,
                invoice_description_goods=request.POST.get(f'item_{i}'),
                invoice_hsn=request.POST.get(f'hsn_{i}'),
                invoice_godown=request.POST.get(f'godown_{i}'),
                invoice_qantity=qty_str,
                invoice_uom=request.POST.get(f'uom_{i}'),
                invoice_unit_price=request.POST.get(f'rate_{i}'),
                invoice_discount=request.POST.get(f'discount_{i}'),
                invoice_tax_rate=request.POST.get(f'taxrate_{i}'),
                invoice_tax_amount=request.POST.get(f'taxamt_{i}'),
                invoice_total=request.POST.get(f'total_{i}'),
                invoice_id=latest_invoice_id,
            )

            i += 1

        messages.success(request, 'Invoice Created Successfully.')
        return redirect('invoice_list')


# @login_required
# def add_invoice_data(request):
#     if request.method == "GET":
#         customer_name = customer.objects.all()
#         dispatch_through = transporter.objects.all()
#         item_data = inventory.objects.all()
#         godown_name = godown.objects.all()
#         dc_list = delivery_challan.objects.all()
#         current_date = datetime.today().strftime('%d-%m-%Y')


#         context ={ 
#             'customer_name' : customer_name,
#             'dispatch_through' : dispatch_through,
#             'item_data': item_data,
#             'godown_name': godown_name,
#             'dc_list':dc_list,
#             'current_date':current_date,
#             }

#         return render(request, template_path.add_invoice, context)
#     elif request.method == "POST":
#         inv_number = generate_tax_invoice_number()
#         invoice_date_str = request.POST['invoice_date']
#         invoice_due_date_str = request.POST.get('due_date')
#         if not invoice_due_date_str:
#             return HttpResponse("Missing 'due_date' field in form.", status=400)
#         invoice_buyer_order_date_str = request.POST['buyer_order_date']
#         invoice_due_date_date = datetime.strptime( invoice_due_date_str, '%d-%m-%Y').date()
#         invoice_buyerorder_date = datetime.strptime( invoice_buyer_order_date_str, '%d-%m-%Y').date()
#         invoice_date = datetime.strptime( invoice_date_str, '%d-%m-%Y').date()
#         # customer_id = request.POST['customer_id']


#         # Optional: Check if customer_id exists
#         customer_id = request.POST.get('customer_id', None)
#         customer_id_customer = request.POST.get('customer_id_select', None)

#         if customer_id:
#             inv_customer_name = customer.objects.filter(id=customer_id).first()
#         else:
#             inv_customer_name = customer.objects.filter(id=customer_id_customer).first()
       
#         invoice_data = {
#             'invoice_date': invoice_date,
#             'inv_number':inv_number,
#             'invoice_payment_terms':request.POST['payment_term'],
#             'invoice_customer_name_customer':inv_customer_name,
#             'invoice_eway_bill_no':request.POST['ewaybill_no'],

#             'invoice_supply_place':request.POST['place_of_supply'],
#             'invoice_delivery_no':request.POST['order_no'],
#             'invoice_destination':request.POST['destination'],
#             'invoice_due_date': invoice_due_date_date,
#             'invoice_landing_LR_RR_No':request.POST['lrno'],
#             'invoice_dispatch':request.POST['transporter_name'],
#             'invoice_shipping_address':request.POST['shipping_address'],
#             'invoice_sales_person':request.POST['sales_person'],
#             'in_customer_code':request.POST['in_customer_code'],
#             'invoice_format_type':request.POST['invoice_format'],
#             'invoice_vehicle_no':request.POST['vehicle_no'],
#             'invoice_gst_no':request.POST['gst_no'],
#             'invoice_term_of_delivery':request.POST['invoice_format'],
#             'invoice_buyer_order_no':request.POST['buyer_order_no'],
#             'invoice_buyer_order_date':invoice_buyerorder_date,
#             # ' invoice_packing':request.POST['packing'],
#             'invoice_dispatch':transporter.objects.filter(id=request.POST['transporter_name']).first(),
#             # 'invoice_freight':request.POST['freight'],
#             'invoice_sub_total':request.POST['subtotal'],
#             # 'invoice_cgstper':request.POST['cgstper'],
#             'invoice_cgstval':request.POST['cgst'],
#             # 'invoice_sgstper':request.POST['sgstper'],
#             'invoice_sgstval':request.POST['sgst'],
#             # 'invoice_igstper':request.POST['igstper'],
#             'invoice_igstval':request.POST['igst'],
#             'invoice_adjustment':request.POST['adjustment'],
#             'invoice_sale_of_good':request.POST['sale_of_good'],
#             'invoice_note':request.POST['note'],
#             'invoice_total':request.POST['totalamt'],
#             'gst_option':request.POST['gst_option'],
#             'inv_packaging_forwording_amount': request.POST.get('packaging_forwording_amount', '0'),
#             'inv_packaging_forwording_percentage': request.POST.get('packaging_forwording_percentage', '0'),
#             'inv_freight_amount': request.POST.get('freight_amount', '0'),
#             'inv_freight_percentage': request.POST.get('freight_percentage', '0'),
#             'inv_packaging_forwording_percentage_amt': request.POST.get('packaging_forwording_percentage_amt', '0'),
#             'inv_freight_percentage_amt': request.POST.get('freight_percentage_amt', '0'),
#             'inv_total_amt_word':request.POST['inv_total_amt_word'],
#             'inv_packaging_forwording_amt_amt': request.POST.get('packaging_forwording_amt_amt', '0'),
#             'inv_freight_amt_amt': request.POST.get('freight_amt_amt', '0'),
#             'invoice_due': request.POST['totalamt'],
#             # 'invoice_term_of_delivery': request.POST['delivery_term'],





#         }
#         Invoice_object = Invoice(**invoice_data)
#         # cust_data = customer.objects.filter(id = customer_id).first()
#         Invoice_object.save()
#         latest_invoice_id = Invoice.objects.latest('id')
#         # cust_data.cust_receive_amount += float(latest_invoice_id.invoice_total)
#         # cust_data.due_date = latest_invoice_id.invoice_due_date
#         # cust_data.save()
#         i = 0
#         max_row = int(request.POST.get('iid[]', 0))

#         while i <= max_row:
#             item_code = request.POST.get(f'itemcode_{i}')
#             qty_str = request.POST.get(f'qty_{i}')

#             if not item_code or not qty_str:
#                 i += 1
#                 continue

#             try:
#                 qty_sold = float(qty_str)
#             except:
#                 qty_sold = 0

#             inv = inventory.objects.filter(item_code=item_code).first()

#             if inv:
#                 available = float(inv.available_stock_quantity or 0)

#                 if available < qty_sold:
#                     print(f"ERROR: Insufficient stock for {item_code} | Available={available} Needed={qty_sold}")
#                     i += 1
#                     continue

#                 # ↓↓↓ REDUCE STOCK (correct)
#                 inv.available_stock_quantity = available - qty_sold
#                 inv.save()
#             else:
#                 print(f"ERROR: Item not found: {item_code}")

#             invoice_items.objects.create(
#                 invoice_item_code=item_code,
#                 invoice_description_goods=request.POST.get(f'item_{i}'),
#                 invoice_hsn=request.POST.get(f'hsn_{i}'),
#                 invoice_godown=request.POST.get(f'godown_{i}'),
#                 invoice_qantity=qty_str,
#                 invoice_uom=request.POST.get(f'uom_{i}'),
#                 invoice_unit_price=request.POST.get(f'rate_{i}'),
#                 invoice_discount=request.POST.get(f'discount_{i}'),
#                 invoice_tax_rate=request.POST.get(f'taxrate_{i}'),
#                 invoice_tax_amount=request.POST.get(f'taxamt_{i}'),
#                 invoice_total=request.POST.get(f'total_{i}'),
#                 invoice_id=latest_invoice_id.id,
#             )

#             i += 1


#         messages.success(request, 'Invoice Created Successfully.')
#         return redirect('invoice_list')
    


def check_duplicate_invoice_no(request):
    invoice_no = request.GET.get('invoice_no')
    is_duplicate = Invoice.objects.filter(inv_number=invoice_no).exists() 
    return JsonResponse({'is_duplicate': is_duplicate})

from django.http import JsonResponse

def check_inventory_stock(request):
    try:
        return JsonResponse({'success': True})
        # Fetch 'item_code' and 'qty' from the GET request parameters
        item_code = request.GET.get('item_code')
        qty = request.GET.get('qty')

        if not item_code or not qty:
            return JsonResponse({'error': 'Missing item_code or qty in request'}, status=400)

        # Fetch the item from the inventory model based on item code
        item = inventory.objects.filter(item_code=item_code).first()

        if not item:
            return JsonResponse({'error': 'Item not found in inventory'}, status=404)

        # Ensure both opening_stock_quantity and qty are converted to floats for comparison
        try:
            opening_stock_quantity = float(item.opening_stock_quantity)
            requested_qty = float(qty)
        except ValueError:
            return JsonResponse({'error': 'Invalid quantity format'}, status=400)

        # Compare the quantities
        if opening_stock_quantity >= requested_qty:
            # Stock is sufficient, return success with no message (or minimal response)
            return JsonResponse({'success': True})  # No message needed for sufficient stock
        else:
            # Stock is insufficient, return failure response with message
            return JsonResponse({'success': False, 'message': 'Not enough stock','available_qty': opening_stock_quantity})

    except Exception as e:
        # Handle other exceptions
        print(f"Error: {e}")
        return JsonResponse({'error': str(e)}, status=500)
    
# def check_inventory_stock_edit(request):
#     try:
#         item_code = request.GET.get('item_code')
#         qty = request.GET.get('qty')
#         old_qty = request.GET.get('old_qty')
#         print(old_qty,"olddddddddddddddddddddd")
#         qty = qty - old_qty
        
#         print(qty,"kkkkkk")

#         if not item_code or not qty:
#             return JsonResponse({'error': 'Missing item_code or qty in request'}, status=400)

#         item = inventory.objects.filter(item_code=item_code).first()

#         if not item:
#             return JsonResponse({'error': 'Item not found in inventory'}, status=404)

#         try:
#             opening_stock_quantity = float(item.opening_stock_quantity)
#             requested_qty = float(qty)
#         except ValueError:
#             return JsonResponse({'error': 'Invalid quantity format'}, status=400)

#         if opening_stock_quantity >= requested_qty:
#             return JsonResponse({'success': True})  # No message needed for sufficient stock
#         else:
#             return JsonResponse({'success': False, 'message': 'Not enough stock','available_qty': opening_stock_quantity})

#     except Exception as e:
#         print(f"Error: {e}")
#         return JsonResponse({'error': str(e)}, status=500)

def check_inventory_stock_edit(request):
    try:
        item_code = request.GET.get('item_code')
        qty = request.GET.get('qty')
        old_qty = request.GET.get('old_qty')  


        if not item_code or not qty:
            return JsonResponse({'error': 'Missing item_code or qty in request'}, status=400)

        item = inventory.objects.filter(item_code=item_code).first()

        if not item:
            return JsonResponse({'error': 'Item not found in inventory'}, status=404)

        try:
            opening_stock_quantity = float(item.opening_stock_quantity)
            requested_qty = float(qty)
            old_qty = float(old_qty)  
        except ValueError:
            return JsonResponse({'error': 'Invalid quantity format'}, status=400)

        net_qty_needed = requested_qty - old_qty 
        # print(net_qty_needed,"net_qty_needed.........")

        if opening_stock_quantity >= net_qty_needed:
            return JsonResponse({'success': True})  
        else:
            return JsonResponse({'success': False, 'message': 'Not enough stock', 'available_qty': opening_stock_quantity})

    except Exception as e:
        # print(f"Error: {e}")
        return JsonResponse({'error': str(e)}, status=500)
    
@login_required
def edit_invoice_data(request, id):
    invoice_obj = get_object_or_404(Invoice, id=id)

    if request.method == "GET":
        invoice_item_data = invoice_items.objects.filter(invoice_id=id)
        context = {
            'invoice_data': invoice_obj,
            'invoice_item_data': invoice_item_data,
            'len_invoice_item': len(invoice_item_data),
            'all_customer_name': customer.objects.all(),
            'item_data': inventory.objects.all(),
            'godown_name': godown.objects.all(),
            'all_dispatch_through': transporter.objects.all(),
            'dc_list': delivery_challan.objects.all(),
        }
        return render(request, template_path.edit_invoice, context)

    elif request.method == "POST":
        with transaction.atomic():
            # ---------- RESTORE OLD STOCK ----------
            old_items = invoice_items.objects.filter(invoice_id=id)
            for old in old_items:
                inv_item = inventory.objects.filter(item_code=old.invoice_item_code).first()
                if inv_item:
                    inv_item.available_stock_quantity = _safe_float(inv_item.available_stock_quantity) + _safe_float(old.invoice_qantity)
                    inv_item.save()

            # Delete old items
            old_items.delete()

            # ---------- UPDATE INVOICE MASTER FIELDS ----------
            invoice_obj.inv_number = request.POST.get('invoice_no', invoice_obj.inv_number)
            invoice_obj.invoice_date = _safe_date(request.POST.get('invoice_date')) or invoice_obj.invoice_date
            invoice_obj.invoice_due_date = _safe_date(request.POST.get('due_date')) or invoice_obj.invoice_due_date
            invoice_obj.invoice_buyer_order_date = _safe_date(request.POST.get('buyer_order_date')) or getattr(invoice_obj, 'invoice_buyer_order_date', None)

            # update lots of fields (mirror your add fields)
            invoice_obj.invoice_payment_terms = request.POST.get('payment_term', invoice_obj.invoice_payment_terms)
            # Customer change handling
            customer_id = request.POST.get('customer_id') or request.POST.get('customer_id_select')
            invoice_obj.invoice_customer_name_customer = customer.objects.filter(id=customer_id).first() if customer_id else invoice_obj.invoice_customer_name_customer

            invoice_obj.invoice_eway_bill_no = request.POST.get('ewaybill_no', invoice_obj.invoice_eway_bill_no)
            invoice_obj.invoice_supply_place = request.POST.get('place_of_supply', invoice_obj.invoice_supply_place)
            invoice_obj.invoice_delivery_no = request.POST.get('order_no', invoice_obj.invoice_delivery_no)
            invoice_obj.invoice_destination = request.POST.get('destination', invoice_obj.invoice_destination)
            invoice_obj.invoice_landing_LR_RR_No = request.POST.get('lrno', invoice_obj.invoice_landing_LR_RR_No)
            transporter_id = request.POST.get('transporter_name')
            invoice_obj.invoice_dispatch = transporter.objects.filter(id=transporter_id).first() if transporter_id else invoice_obj.invoice_dispatch
            invoice_obj.invoice_shipping_address = request.POST.get('shipping_address', invoice_obj.invoice_shipping_address)
            invoice_obj.invoice_sales_person = request.POST.get('sales_person', invoice_obj.invoice_sales_person)
            invoice_obj.in_customer_code = request.POST.get('in_customer_code', invoice_obj.in_customer_code)
            invoice_obj.invoice_format_type = request.POST.get('invoice_format', invoice_obj.invoice_format_type)
            invoice_obj.invoice_vehicle_no = request.POST.get('vehicle_no', invoice_obj.invoice_vehicle_no)
            invoice_obj.invoice_gst_no = request.POST.get('gst_no', invoice_obj.invoice_gst_no)
            invoice_obj.invoice_term_of_delivery = request.POST.get('invoice_format', invoice_obj.invoice_term_of_delivery)
            invoice_obj.invoice_buyer_order_no = request.POST.get('buyer_order_no', invoice_obj.invoice_buyer_order_no)
            invoice_obj.invoice_sub_total = request.POST.get('subtotal', invoice_obj.invoice_sub_total)
            invoice_obj.invoice_cgstval = request.POST.get('cgst', invoice_obj.invoice_cgstval)
            invoice_obj.invoice_sgstval = request.POST.get('sgst', invoice_obj.invoice_sgstval)
            invoice_obj.invoice_igstval = request.POST.get('igst', invoice_obj.invoice_igstval)
            invoice_obj.invoice_adjustment = request.POST.get('adjustment', invoice_obj.invoice_adjustment)
            invoice_obj.invoice_sale_of_good = request.POST.get('sale_of_good', invoice_obj.invoice_sale_of_good)
            invoice_obj.invoice_note = request.POST.get('note', invoice_obj.invoice_note)
            invoice_obj.invoice_total = request.POST.get('totalamt', invoice_obj.invoice_total)
            invoice_obj.gst_option = request.POST.get('gst_option', invoice_obj.gst_option)

            # packaging & freight
            invoice_obj.inv_packaging_forwording_amount = request.POST.get('packaging_forwording_amount', invoice_obj.inv_packaging_forwording_amount)
            invoice_obj.inv_packaging_forwording_percentage = request.POST.get('packaging_forwording_percentage', invoice_obj.inv_packaging_forwording_percentage)
            invoice_obj.inv_freight_amount = request.POST.get('freight_amount', invoice_obj.inv_freight_amount)
            invoice_obj.inv_freight_percentage = request.POST.get('freight_percentage', invoice_obj.inv_freight_percentage)
            invoice_obj.inv_packaging_forwording_percentage_amt = request.POST.get('packaging_forwording_percentage_amt', invoice_obj.inv_packaging_forwording_percentage_amt)
            invoice_obj.inv_freight_percentage_amt = request.POST.get('freight_percentage_amt', invoice_obj.inv_freight_percentage_amt)
            invoice_obj.inv_total_amt_word = request.POST.get('inv_total_amt_word', invoice_obj.inv_total_amt_word)
            invoice_obj.inv_packaging_forwording_amt_amt = request.POST.get('packaging_forwording_amt_amt', invoice_obj.inv_packaging_forwording_amt_amt)
            invoice_obj.inv_freight_amt_amt = request.POST.get('freight_amt_amt', invoice_obj.inv_freight_amt_amt)
            invoice_obj.invoice_due = request.POST.get('totalamt', invoice_obj.invoice_due)

            invoice_obj.save()

            # ---------- ADD NEW ITEMS & REDUCE STOCK ----------
            # Build index set robustly from POST keys
            indices = set()
            for key in request.POST.keys():
                if "_" in key:
                    field, _, idx = key.rpartition("_")
                    if field in ("itemcode", "qty", "uom", "rate", "hsn", "discount", "taxrate", "total", "godown"):
                        try:
                            indices.add(int(idx))
                        except:
                            pass

            for idx in sorted(indices):
                item_code = request.POST.get(f'itemcode_{idx}')
                qty_str = request.POST.get(f'qty_{idx}')

                if not item_code or not qty_str:
                    continue

                qty = _safe_float(qty_str)
                inv_item = inventory.objects.filter(item_code=item_code).first()
                if inv_item:
                    available = _safe_float(inv_item.available_stock_quantity)
                    if available < qty:
                        print(f"ERROR: Insufficient stock for {item_code} while editing invoice (available {available}, needed {qty})")
                        # skip saving this line if not enough stock
                        continue

                    inv_item.available_stock_quantity = available - qty
                    inv_item.save()

                invoice_items.objects.create(
                    invoice_item_code = item_code,
                    invoice_description_goods = request.POST.get(f'item_{idx}',''),
                    invoice_hsn = request.POST.get(f'hsn_{idx}',''),
                    invoice_godown = request.POST.get(f'godown_{idx}',''),
                    invoice_qantity = qty_str,
                    invoice_uom = request.POST.get(f'uom_{idx}',''),
                    invoice_unit_price = request.POST.get(f'rate_{idx}','0'),
                    invoice_discount = request.POST.get(f'discount_{idx}','0'),
                    invoice_tax_rate = request.POST.get(f'taxrate_{idx}','0'),
                    invoice_tax_amount = request.POST.get(f'taxamt_{idx}','0'),
                    invoice_total = request.POST.get(f'total_{idx}','0'),
                    invoice_id = invoice_obj.id,
                )

            messages.success(request, 'Invoice Updated Successfully.')
            return redirect('invoice_list')


# @login_required
# def edit_invoice_data(request, id):
#     if request.method == "GET":
        
#         invoice_data = get_object_or_404(Invoice, id=id)
#         dc_list = delivery_challan.objects.all()

#         all_customer_name = customer.objects.all()
#         all_dispatch_through = transporter.objects.all()
#         item_data = inventory.objects.all()
#         godown_name = godown.objects.all()
#         customer_name = invoice_data.invoice_customer_name
#         dispatch_through = invoice_data.invoice_dispatch.name

#         item_data = inventory.objects.all()
#         all_dispatch_through = transporter.objects.all()
#         all_customer_name = customer.objects.all()
#         invoice_item_data = invoice_items.objects.filter(invoice_id = id)
#         len_invoice_item = len(invoice_item_data)
#         context ={
#             'invoice_data':invoice_data, 
#             'all_customer_name' : all_customer_name,
#             'all_dispatch_through' : all_dispatch_through,
#             'len_invoice_item':len_invoice_item,
#             'item_data': item_data,
#             'invoice_item_data':invoice_item_data,
#             'customer_name':customer_name,
#             'dispatch_through':dispatch_through,
#             'godown_name': godown_name,
#             'dc_list':dc_list,
#             }

#         return render(request, template_path.edit_invoice, context)
#     elif request.method == "POST":
#         invoice_obj = get_object_or_404(Invoice, id=id)

#         # parse dates safely (existing code)
#         invoice_date_str = request.POST.get('invoice_date', '')
#         invoice_due_date_str = request.POST.get('due_date', '')
#         invoice_buyer_order_date_str = request.POST.get('buyer_order_date', '')

#         invoice_date = datetime.strptime(invoice_date_str, '%d-%m-%Y').date() if invoice_date_str else None
#         invoice_due_date_date = datetime.strptime(invoice_due_date_str, '%d-%m-%Y').date() if invoice_due_date_str else None
#         invoice_buyerorder_date = datetime.strptime(invoice_buyer_order_date_str, '%d-%m-%Y').date() if invoice_buyer_order_date_str else None

#         customer_id = request.POST.get('customer_id')

#         # Build update dict for the Invoice fields (use conservative .get())
#         update_fields = {
#             'inv_number': request.POST.get('invoice_no'),
#             'invoice_date': invoice_date,
#             'invoice_payment_terms': request.POST.get('payment_term'),
#             'invoice_eway_bill_no': request.POST.get('ewaybill_no',''),
#             'invoice_supply_place': request.POST.get('place_of_supply',''),
#             'invoice_delivery_no': request.POST.get('order_no',''),
#             'invoice_destination': request.POST.get('destination',''),
#             'invoice_due_date': invoice_due_date_date,
#             'invoice_landing_LR_RR_No': request.POST.get('lrno',''),
#             'invoice_shipping_address': request.POST.get('shipping_address',''),
#             'invoice_sales_person': request.POST.get('sales_person',''),
#             'in_customer_code': request.POST.get('in_customer_code',''),
#             'invoice_format_type': request.POST.get('invoice_format',''),
#             'invoice_vehicle_no': request.POST.get('vehicle_no',''),
#             'invoice_gst_no': request.POST.get('gst_no',''),
#             'invoice_buyer_order_no': request.POST.get('buyer_order_no',''),
#             'invoice_buyer_order_date': invoice_buyerorder_date,
#             'invoice_sub_total': request.POST.get('subtotal','0'),
#             'invoice_cgstval': request.POST.get('cgst','0'),
#             'invoice_sgstval': request.POST.get('sgst','0'),
#             'invoice_igstval': request.POST.get('igst','0'),
#             'invoice_adjustment': request.POST.get('adjustment','0'),
#             'invoice_sale_of_good': request.POST.get('sale_of_good','0'),
#             'invoice_note': request.POST.get('note',''),
#             'invoice_total': request.POST.get('totalamt','0'),
#             'gst_option': request.POST.get('gst_option',''),
#             'inv_packaging_forwording_amount': request.POST.get('packaging_forwording_amount', '0'),
#             'inv_packaging_forwording_percentage': request.POST.get('packaging_forwording_percentage', '0'),
#             'inv_freight_amount': request.POST.get('freight_amount', '0'),
#             'inv_freight_percentage': request.POST.get('freight_percentage', '0'),
#             'inv_packaging_forwording_percentage_amt': request.POST.get('packaging_forwording_percentage_amt', '0'),
#             'inv_freight_percentage_amt': request.POST.get('freight_percentage_amt', '0'),
#             'inv_total_amt_word': request.POST.get('inv_total_amt_word',''),
#             'inv_packaging_forwording_amt_amt': request.POST.get('packaging_forwording_amt_amt', '0'),
#             'inv_freight_amt_amt': request.POST.get('freight_amt_amt', '0'),
#         }

#         # Attach FK objects safely (if you need actual model instances)
#         if customer_id:
#             try:
#                 update_fields['invoice_customer_name_customer'] = customer.objects.get(id=customer_id)
#             except customer.DoesNotExist:
#                 update_fields['invoice_customer_name_customer'] = None

#         transporter_id = request.POST.get('transporter_name')
#         if transporter_id:
#             update_fields['invoice_dispatch'] = transporter.objects.filter(id=transporter_id).first()

#         # Start DB transaction to avoid partial updates
#         with transaction.atomic():
#             # update invoice_obj instance (assign attributes then save)
#             for k, v in update_fields.items():
#                 setattr(invoice_obj, k, v)
#             invoice_obj.save()

#             # Rebuild items: remove old items and add new ones
#             invoice_items.objects.filter(invoice_id = invoice_obj.id).delete()

#             # Determine which row indices are present in POST by scanning keys
#             indices = set()
#             for key in request.POST.keys():
#                 if '_' in key:
#                     name, _, idx = key.rpartition('_')
#                     if name in ('itemcode','qty','qty_old','uom','rate','hsn','discount','taxrate','total'):
#                         try:
#                             indices.add(int(idx))
#                         except ValueError:
#                             pass

#             # iterate sorted indices (this is robust even if some rows were removed/added in UI)
#             for idx in sorted(indices):
#                 # fetch itemcode; skip if empty
#                 dc_item_code = (request.POST.get(f'itemcode_{idx}') or '').strip()
#                 if not dc_item_code:
#                     continue

#                 # safe float conversion with fallback
#                 def safe_float(val):
#                     try:
#                         # treat empty string or None as 0.0
#                         if val is None or val == '':
#                             return 0.0
#                         return float(val)
#                     except (ValueError, TypeError):
#                         return 0.0

#                 quantity_sold = safe_float(request.POST.get(f'qty_{idx}'))
#                 quantity_sold_old = safe_float(request.POST.get(f'qty_old_{idx}'))
#                 remaining_qty = abs(quantity_sold_old - quantity_sold)

#                 inventory_item = inventory.objects.filter(item_code=dc_item_code).first()
#                 if inventory_item:
#                     # opening stock might be None in DB; use safe_float
#                     t_qty = safe_float(inventory_item.opening_stock_quantity)
#                     if t_qty >= remaining_qty:
#                         inventory_item.opening_stock_quantity = t_qty - remaining_qty
#                         inventory_item.save()
#                     else:
#                         # not enough stock: handle as you want (log / messages)
#                         print(f"Error: Insufficient stock for item code {dc_item_code}. Available: {inventory_item.opening_stock_quantity}, Requested change: {remaining_qty}")
#                 else:
#                     print(f"Error: Item with code {dc_item_code} not found in inventory.")

#                 # Save invoice item if at least itemcode present
#                 invoice_item = invoice_items(
#                     invoice_item_code = dc_item_code,
#                     invoice_description_goods = request.POST.get(f'item_{idx}',''),
#                     invoice_hsn = request.POST.get(f'hsn_{idx}',''),
#                     invoice_qantity = request.POST.get(f'qty_{idx}','0'),
#                     invoice_uom = request.POST.get(f'uom_{idx}',''),
#                     invoice_unit_price = request.POST.get(f'rate_{idx}','0'),
#                     invoice_discount = request.POST.get(f'discount_{idx}','0'),
#                     invoice_tax_rate = request.POST.get(f'taxrate_{idx}','0'),
#                     invoice_tax_amount = request.POST.get(f'taxamt_{idx}','0'),
#                     invoice_total = request.POST.get(f'total_{idx}','0'),
#                     invoice_id = invoice_obj.id
#                 )
#                 invoice_item.save()

#         messages.success(request, 'Invoice Updated Successfully.')
#         return redirect('invoice_list')

@login_required
def delete_invoice_data(request, id):
    with transaction.atomic():
        invoice_instance = get_object_or_404(Invoice, id=id)
        items = invoice_items.objects.filter(invoice_id=id)

        # Restore stock for each item
        for item in items:
            inv_item = inventory.objects.filter(item_code=item.invoice_item_code).first()
            if inv_item:
                inv_item.available_stock_quantity = _safe_float(inv_item.available_stock_quantity) + _safe_float(item.invoice_qantity)
                inv_item.save()

        # Optionally adjust customer receive_amount if you tracked it earlier
        try:
            cust = invoice_instance.invoice_customer_name_customer
            if cust and hasattr(cust, 'cust_receive_amount'):
                # subtract invoice total (if stored as string it will be parsed)
                cust.cust_receive_amount = (cust.cust_receive_amount or 0) - float(_safe_decimal(invoice_instance.invoice_total))
                cust.save()
        except Exception:
            pass

        # Delete items & invoice
        items.delete()
        invoice_instance.delete()

        messages.error(request, 'Invoice Deleted Successfully.')
        return redirect('invoice_list')


# @login_required
# def delete_invoice_data(request, id):
#     # Get the customer instance based on the provided ID
#     # print("Httt")
#     invoice_instance = get_object_or_404(Invoice, id=id)    
#     invoice_item_instance = invoice_items.objects.filter(invoice_id = id)
#     invoice_instance.delete()
#     invoice_item_instance.delete()
#     messages.error(request, 'Invoice Deleted.')

#     return redirect('invoice_list')



@login_required
def invoice_pdf(request, id):
    invo = get_object_or_404(Invoice, id=id)
  
    items = invoice_items.objects.filter(invoice_id = id)
    customer_data = invo.invoice_customer_name_customer

    chunk_size = 8
    for index, item in enumerate(items, start=1):
        item.sr_no = index

    combined_chunks = [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]

    if combined_chunks and len(combined_chunks[-1]) < chunk_size:
        combined_chunks[-1].extend([None] * (chunk_size - len(combined_chunks[-1])))


    list_n = []
    count_page = int(len(items) / chunk_size)
    next = False
    if (len(items) % chunk_size) != 0:
        next = True
        count_page += 1



    if items.exists():
        tax_inv_id = items.first().invoice_id
    else:
        tax_inv_id = 'N/A'

    hsn_totals = defaultdict(float)
    for item in items:
        try:
            amount = float(item.invoice_total)
            hsn_totals[item.invoice_hsn] += amount
        except (ValueError, TypeError):
            continue  


    hsn_tax_details = []
   


    for hsn, taxable_value in hsn_totals.items():
        try:
            # Remove '%' symbol and convert to float
            cgst_rate_str = invo.invoice_cgstper.strip('%')
            cgst_rate = float(cgst_rate_str)
            cgst_amount = (taxable_value * cgst_rate) / 100
            # print(f"{cgst_amount} = {taxable_value} * {(cgst_rate / 100)}",'cgst_amount---', cgst_amount)
        except (ValueError, TypeError):
            cgst_rate = cgst_amount = 0.0

        try:
            # Remove '%' symbol and convert to float
            sgst_rate_str = invo.invoice_sgstper.strip('%')
            sgst_rate = float(sgst_rate_str)
            sgst_amount = taxable_value * (sgst_rate / 100)
            # print(sgst_amount)
        except (ValueError, TypeError):
            sgst_rate = sgst_amount = 0.0

        hsn_tax_details.append({
            'hsn': hsn,
            'taxable_value': taxable_value,
            'cgst_rate': cgst_rate,
            'cgst_amount': cgst_amount,
            'sgst_rate': sgst_rate,
            'sgst_amount': sgst_amount
        })

    p = inflect.engine()
    total_amount_in_words = p.number_to_words(invo.invoice_total)
    total_amount_in_words = total_amount_in_words.title()
    total_amount_in_words = total_amount_in_words.replace(",", "")


    total_quantity = sum(float(item.invoice_qantity) for item in items)

    try:
        total_amount = sum(float(item.invoice_total) for item in items)
    except (ValueError, TypeError):
        total_amount = 0.0

    try:
        freight_amount = float(invo.inv_freight_amount)
    except (ValueError, TypeError):
        freight_amount = 0.0

    i_total_amount = total_amount + freight_amount

    for detail in items:
        if invo.gst_option == 'Interstate':
            detail.half_tax_amount = float(detail.invoice_tax_amount)
            detail.half_tax_rate = float(detail.invoice_tax_rate)
        else:
            detail.half_tax_amount = float(detail.invoice_tax_amount) / 2
            detail.half_tax_rate = float(detail.invoice_tax_rate) / 2 


    context = {
        'invo': invo,
        'items': items,
        'total_amount_in_words': total_amount_in_words,
        'total_amount': total_amount,
        'total_quantity': total_quantity,
        'customer_email': customer_data.cust_email,
        'customer_gst': customer_data.gst_number,
        'customer_contact': customer_data.contact_number,
        'customer_pincode': customer_data.pincode,
        'bill_street': customer_data.street,
        'bill_city': customer_data.city,
        'bii_com_state': customer_data.com_state,
        'bill_pincode': customer_data.pincode,
        'bill_gst_uin': customer_data.gst_uin,
        'bill_contact_number': customer_data.contact_number,
        'shipping_1_street': customer_data.shipping_1_street,
        'shipping_1_city': customer_data.shipping_1_city,
        'shipping_1_state': customer_data.shipping_1_state,
        'shipping_1_pincode': customer_data.shipping_1_pincode,
        'shipping_1_gst_uin': customer_data.shipping_1_gst_uin,
        'shipping_1_contact_number': customer_data.shipping_1_contact_number,
        'company_name': customer_data.company_name,
        'total_amount_in_words': total_amount_in_words,
        'bank_name': customer_data.bank_name,
        'account_number': customer_data.account_number,
        'branch_name': customer_data.branch_name,
        'ifsc_code': customer_data.ifsc_code,
        'tax_inv_id': tax_inv_id,
        'hsn_totals': dict(hsn_totals),
        'hsn_tax_details': hsn_tax_details,
        'i_total_amount': i_total_amount,
        'count_page': list(range(1, count_page + 1)),
        'item_list': combined_chunks,
    }

    return render(request, template_path.invoice_show_pdf,context)




from xhtml2pdf import pisa
from django.template.loader import get_template
from django.templatetags.static import static
from weasyprint import HTML, CSS
from django.contrib.staticfiles import finders
import base64



def download_invoice_pdf(request, id):
    invo = get_object_or_404(Invoice, id=id)
  
    items = invoice_items.objects.filter(invoice_id = id)
    customer_data = invo.invoice_customer_name_customer

    chunk_size = 8
    for index, item in enumerate(items, start=1):
        item.sr_no = index

    combined_chunks = [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]

    if combined_chunks and len(combined_chunks[-1]) < chunk_size:
        combined_chunks[-1].extend([None] * (chunk_size - len(combined_chunks[-1])))

    list_n = []
    count_page = int(len(items) / chunk_size)
    next = False
    if (len(items) % chunk_size) != 0:
        next = True
        count_page += 1



    if items.exists():
        tax_inv_id = items.first().invoice_id
    else:
        tax_inv_id = 'N/A'

    hsn_totals = defaultdict(float)
    for item in items:
        try:
            amount = float(item.invoice_total)
            hsn_totals[item.invoice_hsn] += amount
        except (ValueError, TypeError):
            continue  


    hsn_tax_details = []
   


    for hsn, taxable_value in hsn_totals.items():
        try:
            # Remove '%' symbol and convert to float
            cgst_rate_str = invo.invoice_cgstper.strip('%')
            cgst_rate = float(cgst_rate_str)
            cgst_amount = (taxable_value * cgst_rate) / 100
            # print(f"{cgst_amount} = {taxable_value} * {(cgst_rate / 100)}",'cgst_amount---', cgst_amount)
        except (ValueError, TypeError):
            cgst_rate = cgst_amount = 0.0

        try:
            # Remove '%' symbol and convert to float
            sgst_rate_str = invo.invoice_sgstper.strip('%')
            sgst_rate = float(sgst_rate_str)
            sgst_amount = taxable_value * (sgst_rate / 100)
            # print(sgst_amount)
        except (ValueError, TypeError):
            sgst_rate = sgst_amount = 0.0

        hsn_tax_details.append({
            'hsn': hsn,
            'taxable_value': taxable_value,
            'cgst_rate': cgst_rate,
            'cgst_amount': cgst_amount,
            'sgst_rate': sgst_rate,
            'sgst_amount': sgst_amount
        })

    for detail in items:
        if invo.gst_option == 'Interstate':
            detail.half_tax_amount = float(detail.invoice_tax_amount)
            detail.half_tax_rate = float(detail.invoice_tax_rate)
        else:
            detail.half_tax_amount = float(detail.invoice_tax_amount) / 2
            detail.half_tax_rate = float(detail.invoice_tax_rate) / 2 


    p = inflect.engine()
    total_amount_in_words = p.number_to_words(invo.invoice_total)
    total_amount_in_words = total_amount_in_words.title()
    total_amount_in_words = total_amount_in_words.replace(",", "")


    total_quantity = sum(float(item.invoice_qantity) for item in items)

    try:
        total_amount = sum(float(item.invoice_total) for item in items)
    except (ValueError, TypeError):
        total_amount = 0.0

    try:
        freight_amount = float(invo.inv_freight_amount)
    except (ValueError, TypeError):
        freight_amount = 0.0

    i_total_amount = total_amount + freight_amount

    template = get_template('sales/invoice/pdf.html')


    context = {
        'invo': invo,
        'items': items,
        'total_amount_in_words': total_amount_in_words,
        'total_amount': total_amount,
        'total_quantity': total_quantity,
        'customer_email': customer_data.cust_email,
        'customer_contact': customer_data.contact_number,
        'customer_pincode': customer_data.pincode,
        'customer_gst': customer_data.gst_number,
        'bill_street': customer_data.street,
        'bill_city': customer_data.city,
        'bii_com_state': customer_data.com_state,
        'bill_pincode': customer_data.pincode,
        'bill_gst_uin': customer_data.gst_uin,
        'bill_contact_number': customer_data.contact_number,
        'shipping_1_street': customer_data.shipping_1_street,
        'shipping_1_city': customer_data.shipping_1_city,
        'shipping_1_state': customer_data.shipping_1_state,
        'shipping_1_pincode': customer_data.shipping_1_pincode,
        'shipping_1_gst_uin': customer_data.shipping_1_gst_uin,
        'shipping_1_contact_number': customer_data.shipping_1_contact_number,
        'company_name': customer_data.company_name,
        'total_amount_in_words': total_amount_in_words,
        'bank_name': customer_data.bank_name,
        'account_number': customer_data.account_number,
        'branch_name': customer_data.branch_name,
        'ifsc_code': customer_data.ifsc_code,
        'tax_inv_id': tax_inv_id,
        'hsn_totals': dict(hsn_totals),
        'hsn_tax_details': hsn_tax_details,
        'i_total_amount': i_total_amount,
        'count_page': list(range(1, count_page + 1)),
        'item_list': combined_chunks,
    }
    
    html_string = template.render(context)

    # Ensure static files are correctly referenced
    base_url = request.build_absolute_uri('/')

    # Create an HTTP response with the PDF content type
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="TaxInvoice.pdf"'

    try:
        # Generate PDF using WeasyPrint with correct base_url
        HTML(string=html_string, base_url=base_url).write_pdf(response)
        return response
        # pdf_file = HTML(string=html_string, base_url=base_url).write_pdf()

        # Encode PDF to base64
        # pdf_base64 = base64.b64encode(pdf_file).decode('utf-8')
        # Render HTML page with PDF preview
        # return render(request, 'sales/invoice/pdf_preview.html', {'pdf_base64': pdf_base64})

    except Exception as e:
        return HttpResponse(f'Error generating PDF: {str(e)}')



@csrf_exempt
def get_dc_order_items(request, quotation_id):
    try:
        items = delivery_challan_items.objects.filter(delivery_challan_id=quotation_id)
        data = [
            {
                'dc_item_code': item.dc_item_code,
                'dc_description_goods': item.dc_description_goods,
                'dc_hsn': item.dc_hsn,
                'dc_qantity': item.dc_qantity,  # Corrected typo
                'dc_uom': item.dc_uom,
                'dc_unit_price': item.dc_unit_price,
                'dc_discount': item.dc_discount,
                'dc_tax_rate': item.dc_tax_rate,
                'dc_tax_amount': item.dc_tax_amount,
                'dc_total': item.dc_total
            } for item in items
        ]
        return JsonResponse(data, safe=False)
    except Exception as e:
        print(e)
        return JsonResponse({'error': str(e)}, status=500)

 
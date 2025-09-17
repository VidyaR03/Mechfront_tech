from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db.models import Q
from datetime import date, datetime
from core.modules import template_path
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect,HttpResponse
from core.models import customer, transporter, Goods_received_notes, inventory, vendor, good_received_note_items
from core.modules.login.login import login_required
from django.contrib import messages


@login_required
def grn_list_view(request):
    grn_list = Goods_received_notes.objects.all().order_by('-id')
    context = {
        'grn_list':grn_list
        }
    return render(request,template_path.good_return_note_list,context)



@login_required
def add_good_note_data(request):
    if request.method == "GET":
        vendor_name = vendor.objects.all()
        dispatch_through = transporter.objects.all()
        item_data = inventory.objects.all()
        context ={ 
            'vendor_name' : vendor_name,
            'dispatch_through' : dispatch_through,
            'item_data': item_data
            }

        return render(request, template_path.good_return_note_add, context)
    elif request.method == "POST":
        grn_date_str = request.POST['order_date']
        grn_po_date_str = request.POST['po_date']
        grn_invoice_date_str = request.POST['bill_date']


        grn_date = datetime.strptime(grn_date_str, '%d-%m-%Y').date() if grn_date_str else date.today()
        grn_invoice_date = datetime.strptime(grn_invoice_date_str, '%d-%m-%Y').date() if grn_invoice_date_str else date.today()
        grn_po_date = datetime.strptime(grn_po_date_str, '%d-%m-%Y').date() if grn_po_date_str else date.today()

        grn_object = {
            'grn_date':grn_date,
            'grn_vendor_name':vendor.objects.filter(id=request.POST['vendor_name']).first(),
            'grn_vehicle_number':request.POST['vehicle_no'],
            'grn_purchase_order_no':request.POST['po_no'],
            'grn_purchase_order_date':grn_po_date,
            'grn_invoice_no':request.POST['bill_no'],
            'grn_invoice_date':grn_invoice_date,
            'grn_transporter':transporter.objects.filter(id=request.POST['transporter_name']).first(),
            'grn_source_supply':request.POST['place_of_supply'],
            'grn_destination_of_supply':request.POST['destination_of_supply'],
            # 'grn_delivery_type':request.POST['delivery_type'],
            # 'grn_freight':request.POST['freight'],
            'grn_sub_total':request.POST['subtotal'],
            'grn_cgstval':request.POST['cgst'],
            'grn_sgstval':request.POST['sgst'],
            'grn_igstval':request.POST['igst'],
            'grn_adjustment':request.POST['adjustment'],
            # 'grn_sale_of_good':request.POST['sale_of_good'],
            'grn_note':request.POST['note'],
            'grn_total':request.POST['totalamt'],
            'gst_option':request.POST['gst_option'],
            'grn_packaging_forwording_amount': request.POST.get('packaging_forwording_amount', '0'),
            'grn_packaging_forwording_percentage': request.POST.get('packaging_forwording_percentage', '0'),
            'grn_freight_amount': request.POST.get('freight_amount', '0'),
            'grn_freight_percentage': request.POST.get('freight_percentage', '0'),
            'totalamt_word':request.POST['totalamt_word'],
            'grn_packaging_forwording_percentage_amt': request.POST.get('packaging_forwording_percentage_amt', '0'),
            'grn_freight_percentage_amt': request.POST.get('freight_percentage_amt', '0'),
            'grn_packaging_forwording_amt_amt': request.POST.get('packaging_forwording_amt_amt', '0'),
            'grn_freight_percentage_amt_amt': request.POST.get('freight_amt_amt', '0'),

            
        }
        grn_object_data = Goods_received_notes(**grn_object)
        grn_object_data.save()
        latest_grn_id = Goods_received_notes.objects.latest('id')
        i = 0
        max_row = int(request.POST.get('iid[]',0))
        while i <= max_row:
            grn_item = good_received_note_items(
                grn_item_code = request.POST.get(f'itemcode_{i}'),
                grn_description_goods = request.POST.get(f'item_{i}'),
                grn_hsn = request.POST.get(f'hsn_{i}'),
                grn_qantity = request.POST.get(f'qty_{i}'),
                grn_uom = request.POST.get(f'uom_{i}'),
                grn_unit_price = request.POST.get(f'rate_{i}'),
                grn_discount = request.POST.get(f'discount_{i}'),
                grn_tax_rate = request.POST.get(f'taxrate_{i}'),
                grn_tax_amount = request.POST.get(f'taxamt_{i}'),
                grn_total = request.POST.get(f'total_{i}'),
                good_received_note_id = latest_grn_id.id
            )
            grn_item.save()
            i = i+1
        messages.success(request, 'Good Received Created Successfully.')

        return redirect('grn_list')
    
@login_required
def edit_good_note_data(request, id):
    if request.method == "GET":
        grn_data = get_object_or_404(Goods_received_notes, id = id)
        vendor_name = vendor.objects.all()
        dispatch_through = transporter.objects.all()
        item_data = inventory.objects.all()
        grn_item_data = good_received_note_items.objects.filter(good_received_note_id = id)
        context ={
            'grn_item_data':grn_item_data,
            'len_grn_item_data': len(grn_item_data),
            'grn_data':grn_data,
            'vendor_name' : vendor_name,
            'dispatch_through' : dispatch_through,
            'item_data': item_data
            }
        return render(request, template_path.good_return_note_edit, context)
    elif request.method == "POST":
        grn_data = get_object_or_404(Goods_received_notes, id = id)
        grn_date_str = request.POST['order_date']
        grn_po_date_str = request.POST['po_date']
        grn_invoice_date_str = request.POST['bill_date']
        grn_date = datetime.strptime(grn_date_str, '%d-%m-%Y').date() if grn_date_str else date.today()
        grn_invoice_date = datetime.strptime(grn_invoice_date_str, '%d-%m-%Y').date() if grn_invoice_date_str else date.today()
        grn_po_date = datetime.strptime(grn_po_date_str, '%d-%m-%Y').date() if grn_po_date_str else date.today()

        grn_object = {
            'id':id,
            'grn_date':grn_date,
            'grn_vendor_name':vendor.objects.filter(id=request.POST['vendor_name']).first(),
            'grn_vehicle_number':request.POST['vehicle_no'],
            'grn_purchase_order_no':request.POST['po_no'],
            'grn_purchase_order_date':grn_po_date,
            'grn_invoice_no':request.POST['bill_no'],
            'grn_invoice_date':grn_invoice_date,
            'grn_transporter':transporter.objects.filter(id=request.POST['transporter_name']).first(),
            'grn_source_supply':request.POST['place_of_supply'],
            'grn_destination_of_supply':request.POST['destination_of_supply'],
            # 'grn_delivery_type':request.POST['delivery_type'],
            # 'grn_freight':request.POST['freight'],
            'grn_sub_total':request.POST['subtotal'],
            # 'grn_cgstper':request.POST['cgstper'],
            'grn_cgstval':request.POST['cgst'],
            # 'grn_sgstper':request.POST['sgstper'],
            'grn_sgstval':request.POST['sgst'],
            # 'grn_igstper':request.POST['igstper'],
            'grn_igstval':request.POST['igst'],
            'grn_adjustment':request.POST['adjustment'],
            # 'grn_sale_of_good':request.POST['sale_of_good'],
            'grn_note':request.POST['note'],
            'grn_total':request.POST['totalamt'],
            'gst_option':request.POST['gst_option'],
            'grn_packaging_forwording_amount': request.POST.get('packaging_forwording_amount', '0'),
            'grn_packaging_forwording_percentage': request.POST.get('packaging_forwording_percentage', '0'),
            'grn_freight_amount': request.POST.get('freight_amount', '0'),
            'grn_freight_percentage': request.POST.get('freight_percentage', '0'),
            'totalamt_word':request.POST['totalamt_word'],
            'grn_packaging_forwording_percentage_amt': request.POST.get('packaging_forwording_percentage_amt', '0'),
            'grn_freight_percentage_amt': request.POST.get('freight_percentage_amt', '0'),
            'grn_packaging_forwording_amt_amt': request.POST.get('packaging_forwording_amt_amt', '0'),
            'grn_freight_percentage_amt_amt': request.POST.get('freight_amt_amt', '0'),

        }
        grn_object_data = Goods_received_notes(**grn_object)
        grn_object_data.save()
        # latest_grn_id = Goods_received_notes.objects.latest('id')
        i = 1
        max_row = int(request.POST.get('iid[]',0))
        good_received_note_items.objects.filter(good_received_note_id = id).delete()
        # while i <= max_row:
        for i in range(1, max_row + 1):
            dc_item_code = request.POST.get(f'itemcode_{i}')

            # Only proceed if dc_item_code is not null or empty
            if dc_item_code:
                grn_item = good_received_note_items(
                    grn_item_code = request.POST.get(f'itemcode_{i}'),
                    grn_description_goods = request.POST.get(f'item_{i}'),
                    grn_hsn = request.POST.get(f'hsn_{i}'),
                    grn_qantity = request.POST.get(f'qty_{i}'),
                    grn_uom = request.POST.get(f'uom_{i}'),
                    grn_unit_price = request.POST.get(f'rate_{i}'),
                    grn_discount = request.POST.get(f'discount_{i}'),
                    grn_tax_rate = request.POST.get(f'taxrate_{i}'),
                    grn_tax_amount = request.POST.get(f'taxamt_{i}'),
                    grn_total = request.POST.get(f'total_{i}'),
                    good_received_note_id = id
                )
                grn_item.save()
                i = i+1
        messages.success(request, 'Good Received Updated Successfully.')

        return redirect('grn_list')

    

@login_required
def grn_delete_view(request, id):
    # Get the GRN instance based on the provided ID
    grn_instance = get_object_or_404(Goods_received_notes, id=id)
    # Filter related items using the correct foreign key field
    grn_item_instances = good_received_note_items.objects.filter(good_received_note_id=id)
    
    # Delete the GRN instance and its related items
    grn_instance.delete()
    grn_item_instances.delete()
    messages.success(request, f'GRN {id} Deleted Successfully.')
    
    return redirect('grn_list')
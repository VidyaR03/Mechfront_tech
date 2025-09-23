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


@login_required
def purchaseinvoice_list_view(request):
    purchase_invoice_list = Purchase_Invoice.objects.all().order_by('-id')
    context = {
        'purchase_invoice_list':purchase_invoice_list
        }
    return render(request,template_path.purchase_invoice_list,context)


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
            'dispatch_through':dispatch_through,
            'current_date':current_date
            }
        return render(request, template_path.purchase_invoice_add, context)
    elif request.method == "POST":
        purchase_invoice_date_str = request.POST['bill_date']
        purchase_invoice_grn_date_str = request.POST['grn_date']
        purchase_invoice_po_date_str = request.POST['po_date']
        purchase_invoice_due_date_str = request.POST['due_date']
        purchase_invoice_date = datetime.strptime(purchase_invoice_date_str, '%d-%m-%Y').date() if purchase_invoice_date_str else date.today()
        purchase_invoice_due_date = datetime.strptime(purchase_invoice_due_date_str, '%d-%m-%Y').date() if purchase_invoice_due_date_str else date.today()
        purchase_invoice_po_date = datetime.strptime(purchase_invoice_grn_date_str, '%d-%m-%Y').date() if purchase_invoice_grn_date_str else date.today()
        purchase_invoice_grn_date = datetime.strptime(purchase_invoice_grn_date_str, '%d-%m-%Y').date() if purchase_invoice_grn_date_str else date.today()
        vendor_id = request.POST.get('vendor_name_id')




        purchase_invoice_object = {
            'purchase_invoice_date':purchase_invoice_date,
            'purchase_invoice_vendor_name': vendor.objects.filter(id=vendor_id).first(),

            'purchase_due_date':purchase_invoice_due_date,
            'purchase_invoice_source_supply':request.POST['place_of_supply'],
            'pi_vendor_code':request.POST['vendor_code'],
            'purchase_invoice_destination_of_supply':request.POST['destination_of_supply'],
            'purchase_invoice_PO_no':request.POST['order_no'],
            'purchase_invoice_PO_date':purchase_invoice_po_date,
            'purchase_invoice_grn_no':request.POST['grn_no'],
            'purchase_invoice_grn_date':purchase_invoice_grn_date,
            'purchase_invoice_gst_no':request.POST['gst_no'],
            # 'purchase_invoice_delivery_type':request.POST['delivery_type'],
            # 'purchase_invoice_freight':request.POST['freight'],
            'purchase_invoice_sub_total':request.POST['subtotal'],
            # 'purchase_invoice_cgstper':request.POST['cgstper'],
            'purchase_invoice_cgstval':request.POST['cgst'],
            # 'purchase_invoice_sgstper':request.POST['sgstper'],
            'purchase_invoice_sgstval':request.POST['sgst'],
            # 'purchase_invoice_igstper':request.POST['igstper'],
            'purchase_invoice_igstval':request.POST['igst'],
            'purchase_invoice_adjustment':request.POST['adjustment'],
            # 'purchase_invoice_sale_of_good':request.POST['sale_of_good'],
            'purchase_invoice_note':request.POST['note'],
            'purchase_invoice_total':request.POST['totalamt'],
            'purchase_dispatch':transporter.objects.filter(id=request.POST['transporter_name']).first(),
            'gst_option':request.POST['gst_option'],
            'purchase_packaging_forwording_amount': request.POST.get('packaging_forwording_amount', '0'),
            'purchase_packaging_forwording_percentage': request.POST.get('packaging_forwording_percentage', '0'),
            'purchase_freight_amount': request.POST.get('freight_amount', '0'),
            'purchase_freight_percentage': request.POST.get('freight_percentage', '0'),
            'cn_packaging_forwording_percentage_amt': request.POST.get('packaging_forwording_percentage_amt', '0'),
            'cn_freight_percentage_amt': request.POST.get('freight_percentage_amt', '0'),
            'cn_total_amt_word':request.POST['cn_total_amt_word'],
            'cn_packaging_forwording_amt_amt': request.POST.get('packaging_forwording_amt_amt', '0'),
            'cn_freight_percentage_amt_amt': request.POST.get('freight_amt_amt', '0'),



        }
        purchase_invoice_object_data = Purchase_Invoice(**purchase_invoice_object)
        vendor_data = vendor.objects.filter(id = vendor_id).first()

        # print("balance",vendor_data.receive_amount)
        purchase_invoice_object_data.save()
        latest_purchase_invoice_id = Purchase_Invoice.objects.latest('id')
        vendor_data.receive_amount += float(latest_purchase_invoice_id.purchase_invoice_total)
        vendor_data.due_date = latest_purchase_invoice_id.purchase_due_date
        vendor_data.save()
        i = 0
        max_row = int(request.POST.get('iid[]',0))
        while i <= max_row:
            purchase_invoice_item = Purchase_Invoice_items(
                purchase_invoice_item_code = request.POST.get(f'itemcode_{i}'),
                purchase_invoice_description_goods = request.POST.get(f'item_{i}'),
                purchase_invoice_hsn = request.POST.get(f'hsn_{i}'),

                purchase_invoice_qantity = request.POST.get(f'qty_{i}'),
                purchase_invoice_uom = request.POST.get(f'uom_{i}'),
                purchase_invoice_unit_price = request.POST.get(f'rate_{i}'),
                purchase_invoice_discount = request.POST.get(f'discount_{i}'),
                purchase_invoice_tax_rate = request.POST.get(f'taxrate_{i}'),
                purchase_invoice_tax_amount = request.POST.get(f'taxamt_{i}'),
                purchase_invoice_total = request.POST.get(f'total_{i}'),
                purchase_invoice_id = latest_purchase_invoice_id.id
            )
            purchase_invoice_item.save()
            i = i+1
        messages.success(request, 'Purchase Invoice Created Successfully.')

        return redirect('purchase_invoice_list')


@login_required
def edit_purchaseinvoice_data(request, id):
    if request.method == "GET":
        purchaseinvoice_data = get_object_or_404(Purchase_Invoice, id = id)
        all_vendor_name = vendor.objects.all()
        item_data = inventory.objects.all()
        vendor_name = vendor.objects.all()
        dispatch_through = transporter.objects.all()
        purchaseinvoice_item_data = Purchase_Invoice_items.objects.filter(purchase_invoice_id = id)
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
        vendor_id = request.POST.get("vendor_name_id")  
        if vendor_id:
            po_vendor = vendor.objects.filter(id=vendor_id).first()
        else:
            po_vendor = None    

        purchaseinvoice_data = get_object_or_404(Purchase_Invoice, id = id)
        id = purchaseinvoice_data.id 
        purchase_invoice_date_str = request.POST['bill_date']
        purchase_invoice_grn_date_str = request.POST['grn_date']
        purchase_invoice_po_date_str = request.POST['po_date']
        purchase_invoice_due_date_str = request.POST['due_date']
        purchase_invoice_date = datetime.strptime(purchase_invoice_date_str, '%d-%m-%Y').date() if purchase_invoice_date_str else date.today()
        purchase_invoice_due_date = datetime.strptime(purchase_invoice_due_date_str, '%d-%m-%Y').date() if purchase_invoice_due_date_str else date.today()
        purchase_invoice_po_date = datetime.strptime(purchase_invoice_grn_date_str, '%d-%m-%Y').date() if purchase_invoice_grn_date_str else date.today()
        purchase_invoice_grn_date = datetime.strptime(purchase_invoice_grn_date_str, '%d-%m-%Y').date() if purchase_invoice_grn_date_str else date.today()
       
        purchase_invoice_object = {
            'id': id,
            'purchase_invoice_date':purchase_invoice_date,
            'purchase_invoice_vendor_name':po_vendor,
            'purchase_due_date':purchase_invoice_due_date,
            'purchase_invoice_source_supply':request.POST['place_of_supply'],
            'pi_vendor_code':request.POST['vendor_code'],
            'purchase_invoice_destination_of_supply':request.POST['destination_of_supply'],
            'purchase_invoice_PO_no':request.POST['order_no'],
            'purchase_invoice_PO_date':purchase_invoice_po_date,
            'purchase_invoice_grn_no':request.POST['grn_no'],
            'purchase_invoice_grn_date':purchase_invoice_grn_date,
            'purchase_invoice_gst_no':request.POST['gst_no'],
            # 'purchase_invoice_delivery_type':request.POST['delivery_type'],
            # 'purchase_invoice_freight':request.POST['freight'],
            'purchase_invoice_sub_total':request.POST['subtotal'],
            # 'purchase_invoice_cgstper':request.POST['cgstper'],
            'purchase_invoice_cgstval':request.POST['cgst'],
            # 'purchase_invoice_sgstper':request.POST['sgstper'],
            'purchase_invoice_sgstval':request.POST['sgst'],
            # 'purchase_invoice_igstper':request.POST['igstper'],
            'purchase_invoice_igstval':request.POST['igst'],
            'purchase_invoice_adjustment':request.POST['adjustment'],
            # 'purchase_invoice_sale_of_good':request.POST['sale_of_good'],
            'purchase_invoice_note':request.POST['note'],
            'purchase_invoice_total':request.POST['totalamt'],
            'gst_option':request.POST['gst_option'],
            'purchase_dispatch':transporter.objects.filter(id=request.POST['transporter_name']).first(),

            'purchase_packaging_forwording_amount': request.POST.get('packaging_forwording_amount', '0'),
            'purchase_packaging_forwording_percentage': request.POST.get('packaging_forwording_percentage', '0'),
            'purchase_freight_amount': request.POST.get('freight_amount', '0'),
            'purchase_freight_percentage': request.POST.get('freight_percentage', '0'),
    
            'cn_packaging_forwording_percentage_amt': request.POST.get('packaging_forwording_percentage_amt', '0'),
            'cn_freight_percentage_amt': request.POST.get('freight_percentage_amt', '0'),
            'cn_total_amt_word':request.POST['cn_total_amt_word'],
            'cn_packaging_forwording_amt_amt': request.POST.get('packaging_forwording_amt_amt', '0'),
            'cn_freight_percentage_amt_amt': request.POST.get('freight_amt_amt', '0'),

        }
        purchase_invoice_object_data = Purchase_Invoice(**purchase_invoice_object)
        purchase_invoice_object_data.save()
        i = 1
        max_row = int(request.POST.get('iid[]',0))
        Purchase_Invoice_items.objects.filter(purchase_invoice_id = id).delete()
        # while i <= max_row:
        for i in range(1, max_row + 1):
            dc_item_code = request.POST.get(f'itemcode_{i}')

            # Only proceed if dc_item_code is not null or empty
            if dc_item_code:
                purchase_invoice_item = Purchase_Invoice_items(
                    purchase_invoice_item_code = request.POST.get(f'itemcode_{i}'),
                    purchase_invoice_description_goods = request.POST.get(f'item_{i}'),
                    purchase_invoice_hsn = request.POST.get(f'hsn_{i}'),
                    purchase_invoice_qantity = request.POST.get(f'qty_{i}'),
                    purchase_invoice_uom = request.POST.get(f'uom_{i}'),
                    purchase_invoice_unit_price = request.POST.get(f'rate_{i}'),
                    purchase_invoice_discount = request.POST.get(f'discount_{i}'),
                    purchase_invoice_tax_rate = request.POST.get(f'taxrate_{i}'),
                    purchase_invoice_tax_amount = request.POST.get(f'taxamt_{i}'),
                    purchase_invoice_total = request.POST.get(f'total_{i}'),
                    purchase_invoice_id = id
                )
                purchase_invoice_item.save()
                i = i+1
        messages.success(request, 'Purchase Invoice Updated Successfully.')

        return redirect('purchase_invoice_list')
    

@login_required
def delete_purchaseinvoice_data(request, id):
    # Get the customer instance based on the provided ID
    purchaseitem_instance = get_object_or_404(Purchase_Invoice, id=id)    
    purchaseitem_item_instance = Purchase_Invoice_items.objects.filter(purchase_invoice_id = id)
    # if request.method == 'POST':
    purchaseitem_instance.delete()
    purchaseitem_item_instance.delete()
    messages.error(request, 'Purchase Invoice Deleted.')

    return redirect('purchase_invoice_list') 
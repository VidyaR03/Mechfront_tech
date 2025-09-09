import base64
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db.models import Q
from datetime import datetime
from core.modules import template_path
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect,HttpResponse
from core.models import customer, transporter, Purchase_order, inventory, vendor, purchase_order_items
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.templatetags.static import static
from weasyprint import HTML, CSS
from django.contrib.staticfiles import finders
from datetime import datetime, date
from core.modules.login.login import login_required
from django.contrib import messages
from django.db.models import Sum

@login_required
def purchaseorder_list_view(request):
    purchase_order_list = Purchase_order.objects.all().order_by('-id')
    context = {
        'purchase_order_list':purchase_order_list
        }
    return render(request,template_path.purchase_order_list,context)


@login_required
def add_purchase_order_data(request):
    if request.method == "GET":
        vendor_name = vendor.objects.all()
        dispatch_through = transporter.objects.all()
        item_data = inventory.objects.all()
        current_date = datetime.today().strftime('%d-%m-%Y')

        context ={ 
            'vendor_name' : vendor_name,
            'dispatch_through' : dispatch_through,
            'item_data': item_data,
            'current_date':current_date
            }

        return render(request, template_path.purchase_order_add, context)
    elif request.method == "POST":
        import re
        
        lattest_order = Purchase_order.objects.all().order_by('id').last()

        if lattest_order and lattest_order.po_no:
            last_po = lattest_order.po_no
            po_suffix = last_po.split('-')[1] if '-' in last_po else last_po

            # Remove all non-digit characters
            numeric_part = re.sub(r'\D', '', po_suffix)

            if numeric_part:
                po_number = int(numeric_part) + 1
            else:
                po_number = 1
        else:
            po_number = 1

        po_no = f"PO-{po_number:03d}"

        # Ensure uniqueness
        while Purchase_order.objects.filter(po_no=po_no).exists():
            po_number += 1
            po_no = f"PO-{po_number:03d}"

        po_date_str = request.POST['order_date']
        po_delivery_date_str = request.POST['delivery_date']
        po_date = datetime.strptime(po_date_str, '%d-%m-%Y').date() if po_date_str else date.today()
        po_delivery_date = datetime.strptime(po_delivery_date_str, '%d-%m-%Y').date()  if po_delivery_date_str else date.today()
        purchase_order = {
            'po_no':po_no,
            'po_date':po_date,
            'po_vendor_code':request.POST['vendor_code'],
            'po_vendor_name':vendor.objects.filter(id=request.POST['vendor_name']).first(),
            'po_payment_terms':request.POST['payment_term'],
            'po_delivery_date':po_delivery_date,
            'po_delivery_type':request.POST['delivery_type'],
            'po_source_supply':request.POST['place_of_supply'],
            'po_destination':request.POST['destination_of_supply'],
            # 'po_delivery_type':request.POST['delivery_type'],
            'po_dispatch':transporter.objects.get(id=request.POST['transporter_name']),
            # 'po_freight':request.POST['freight'],
            'po_sub_total':request.POST['subtotal'],
            # 'po_cgstper':request.POST['cgstper'],
            'po_cgstval':request.POST['cgst'],
            # 'po_sgstper':request.POST['sgstper'],
            'po_sgstval':request.POST['sgst'],
            # 'po_igstper':request.POST['igstper'],
            'po_igstval':request.POST['igst'],
            'po_adjustment':request.POST['adjustment'],
            # 'po_sale_of_good':request.POST['sale_of_good'],
            'po_note':request.POST['note'],
            'po_total':request.POST['totalamt'],
            'gst_option':request.POST['gst_option'],
            'po_packaging_forwording_amount': request.POST.get('packaging_forwording_amount', '0'),
            'po_packaging_forwording_percentage': request.POST.get('packaging_forwording_percentage', '0'),
            'po_freight_amount': request.POST.get('freight_amount', '0'),
            'po_freight_percentage': request.POST.get('freight_percentage', '0'),
            'po_total_amt_word':request.POST['po_total_amt_word'],
            'po_packaging_forwording_percentage_amt': request.POST.get('packaging_forwording_percentage_amt', '0'),
            'po_freight_percentage_amt': request.POST.get('freight_percentage_amt', '0'),
            'po_packaging_forwording_amt_amt': request.POST.get('packaging_forwording_amt_amt', '0'),
            'po_freight_amt_amt': request.POST.get('freight_amt_amt', '0'),
            'po_price':request.POST['po_price'],
            'po_test_certificate':request.POST['po_test_certificate'],
            'po_warranty_certificate':request.POST['po_warranty_certificate'],
            'po_coc':request.POST['po_coc'],
            'po_delivery':request.POST['po_delivery'],
            'po_payment':request.POST['po_payment'],
            'po_quotation':request.POST['po_quotation'],
            'po_quo_date':request.POST['po_quo_date'],



       
            
        }
        purchase_order_object = Purchase_order(**purchase_order)
        purchase_order_object.save()
        latest_purchase_order_id = Purchase_order.objects.latest('id')
        i = 0
        max_row = int(request.POST.get('iid[]',0))
        while i <= max_row:
            po_item = purchase_order_items(
                po_item_code = request.POST.get(f'itemcode_{i}'),
                po_description_goods = request.POST.get(f'item_{i}'),
                po_hsn = request.POST.get(f'hsn_{i}'),
                po_qantity = request.POST.get(f'qty_{i}'),
                po_uom = request.POST.get(f'uom_{i}'),
                po_unit_price = request.POST.get(f'rate_{i}'),
                po_discount = request.POST.get(f'discount_{i}'),
                po_tax_rate = request.POST.get(f'taxrate_{i}'),
                po_tax_amount = request.POST.get(f'taxamt_{i}'),
                po_total = request.POST.get(f'total_{i}'),
                purchase_order_id = latest_purchase_order_id.id
            )
            po_item.save()
            i = i+1

        messages.success(request, 'Purchase Order Created Successfully.')

        return redirect('purchase_order_list')

def check_duplicate_purchase_order_no(request):
    purchase_order = request.GET.get('purchase_order_no')
    is_duplicate = Purchase_order.objects.filter(po_no=purchase_order).exists()
    return JsonResponse({'is_duplicate':is_duplicate})

@login_required
def edit_purchase_order_data(request,id):
    if request.method == "GET":
        purchase_order_data = get_object_or_404(Purchase_order, id=id)
        all_vendor_name = vendor.objects.all()
        all_dispatch_through = transporter.objects.all()
        item_data = inventory.objects.all()
        purchase_order_data_item = purchase_order_items.objects.filter(purchase_order_id = id)
        context ={
            'purchase_order_data':purchase_order_data,
            'purchase_order_data_item': purchase_order_data_item,
            'len_purchase_order_data_item': len(purchase_order_data_item),
            'all_vendor_name':all_vendor_name,
            'all_dispatch_through':all_dispatch_through,
            # 'vendor_name' : purchase_order_data.vendor_name,
            # 'dispatch_through' : purchase_order_data.dispatch_through,
            'item_data': item_data
            }

        return render(request, template_path.purchase_order_edit, context)
    elif request.method == "POST":

        purchase_order_data = get_object_or_404(Purchase_order, id=id)
        id = purchase_order_data.id
        po_date_str = request.POST['order_date']
        po_delivery_date_str = request.POST['delivery_date']
        po_date = datetime.strptime(po_date_str, '%d-%m-%Y').date() if po_date_str else date.today()
        po_delivery_date = datetime.strptime(po_delivery_date_str, '%d-%m-%Y').date() if po_delivery_date_str else date.today()
        purchase_order = {
            'id' : id,
            'po_no':request.POST['purchase_order_no'],
            'po_date':po_date,
            'po_vendor_code':request.POST['vendor_code'],
            'po_vendor_name':vendor.objects.filter(id=request.POST['vendor_name']).first(),
            'po_payment_terms':request.POST['payment_term'],
            'po_delivery_date':po_delivery_date,
            'po_delivery_type':request.POST['delivery_type'],
            'po_source_supply':request.POST['place_of_supply'],
            'po_destination':request.POST['destination_of_supply'],
            # 'po_delivery_type':request.POST['delivery_type'],
            # 'po_dispatch':transporter.objects.filter(id=request.POST['transporter_name']).first(),
            # 'po_freight':request.POST['freight'],
            'po_dispatch':transporter.objects.get(id=request.POST['transporter_name']),
            'po_sub_total':request.POST['subtotal'],
            # 'po_cgstper':request.POST['cgstper'],
            'po_cgstval':request.POST['cgst'],
            # 'po_sgstper':request.POST['sgstper'],
            'po_sgstval':request.POST['sgst'],
            # 'po_igstper':request.POST['igstper'],
            'po_igstval':request.POST['igst'],
            'po_adjustment':request.POST['adjustment'],
            # 'po_sale_of_good':request.POST['sale_of_good'],
            'po_note':request.POST['note'],
            'po_total':request.POST['totalamt'],
            'gst_option':request.POST['gst_option'],
            'po_packaging_forwording_amount': request.POST.get('packaging_forwording_amount', '0'),
            'po_packaging_forwording_percentage': request.POST.get('packaging_forwording_percentage', '0'),
            'po_freight_amount': request.POST.get('freight_amount', '0'),
            'po_freight_percentage': request.POST.get('freight_percentage', '0'),
            'po_total_amt_word':request.POST['po_total_amt_word'],
            'po_packaging_forwording_percentage_amt': request.POST.get('packaging_forwording_percentage_amt', '0'),
            'po_freight_percentage_amt': request.POST.get('freight_percentage_amt', '0'),
            'po_packaging_forwording_amt_amt': request.POST.get('packaging_forwording_amt_amt', '0'),
            'po_freight_amt_amt': request.POST.get('freight_amt_amt', '0'),

            'po_price':request.POST['po_price'],
            'po_test_certificate':request.POST['po_test_certificate'],
            'po_warranty_certificate':request.POST['po_warranty_certificate'],
            'po_coc':request.POST['po_coc'],
            'po_delivery':request.POST['po_delivery'],
            'po_payment':request.POST['po_payment'],
            'po_quotation':request.POST['po_quotation'],
            'po_quo_date':request.POST['po_quo_date'],


       
        }
        purchase_order_object = Purchase_order(**purchase_order)
        purchase_order_object.save()
        i = 1
        max_row = int(request.POST.get('iid[]',0))
        purchase_order_items.objects.filter(purchase_order_id = id).delete()
        # while i <= max_row:
        for i in range(1, max_row + 1):
            dc_item_code = request.POST.get(f'itemcode_{i}')

            # Only proceed if dc_item_code is not null or empty
            if dc_item_code:
                po_item = purchase_order_items(
                    po_item_code = request.POST.get(f'itemcode_{i}'),
                    po_description_goods = request.POST.get(f'item_{i}'),
                    po_hsn = request.POST.get(f'hsn_{i}'),
                    po_qantity = request.POST.get(f'qty_{i}'),
                    po_uom = request.POST.get(f'uom_{i}'),
                    po_unit_price = request.POST.get(f'rate_{i}'),
                    po_discount = request.POST.get(f'discount_{i}'),
                    po_tax_rate = request.POST.get(f'taxrate_{i}'),
                    po_tax_amount = request.POST.get(f'taxamt_{i}'),
                    po_total = request.POST.get(f'total_{i}'),
                    purchase_order_id = id
                )
                po_item.save()
                i = i+1
        messages.success(request, 'Purchase Order Updated Successfully.')

        return redirect('purchase_order_list')
    

@login_required
def delete_purchase_order_data(request, id):
    # Get the customer instance based on the provided ID
    purchase_order_instance = get_object_or_404(Purchase_order, id=id)    
    purchase_order_item_instance = purchase_order_items.objects.filter(purchase_order_id = id)
    purchase_order_instance.delete()
    purchase_order_item_instance.delete()
    messages.error(request, 'Purchase Order Deleted.')

    return redirect('purchase_order_list')



@login_required
def purchase_show_pdf(request, id):
    purchase_ord = get_object_or_404(Purchase_order, id=id)
    purchase_ord_item_data = purchase_order_items.objects.filter(purchase_order_id = id)
    sum_total = purchase_order_items.objects.filter(purchase_order_id=id).aggregate(total=Sum('po_total'))['total']
    # Set to 0 if no items are found or the total is None
    sum_total = sum_total or 0
    gst_percentage = 0

    total_gst = float(purchase_ord.po_igstval) + float(purchase_ord.po_cgstval) + float(purchase_ord.po_sgstval)

    # Calculate GST percentage
    if purchase_ord.po_total:  # Ensure po_total is not zero or None
        gst_percentage = (total_gst / float(purchase_ord.po_total)) * 100
    else:
        gst_percentage = 0  # or handle the division by zero case appropriately

    context = {
        'purchase_ord':purchase_ord,
        'purchase_ord_item_data':purchase_ord_item_data,
         'sum_total': sum_total,
         'gst_percentage': gst_percentage
        }
    return render(request, template_path.purchase_order_pdf,context)



# def purchsae_download_pdf(request, id):
#     purchase_ord = get_object_or_404(Purchase_order, id=id)

#     purchase_ord_item_data = purchase_order_items.objects.filter(purchase_order_id = id)

#     context = {
#         'purchase_ord':purchase_ord,
#         'purchase_ord_item_data':purchase_ord_item_data
#         }
#     return render(request, template_path.purchase_order_pdf,context)




# def purchsae_download_pdf(request, id):
#     purchase_ord = get_object_or_404(Purchase_order, id=id)
#     items = purchase_order_items.objects.filter(purchase_order_id = id)
#     print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&"* 8)
#     context = {
#         'purchase_ord':purchase_ord,
#         'purchase_ord_item_data':items
#         }
    
#     template = get_template('purchase/purchase_order/purchase_order_pdf_download.html')


#     html_string = template.render(context)
#     # Ensure static files are correctly referenced
#     base_url = request.build_absolute_uri('/')
#     # Create an HTTP response with the PDF content type
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = 'attachment; filename="PO.pdf"'

#     try:
#         # Generate PDF using WeasyPrint with correct base_url
#         # HTML(string=html_string, base_url=base_url).write_pdf(response)
#         # return response

#         pdf_file = HTML(string=html_string, base_url=base_url).write_pdf()
#         # Encode PDF to base64
#         pdf_base64 = base64.b64encode(pdf_file).decode('utf-8')
#         # Render HTML page with PDF preview
#         return render(request, 'purchase/purchase_order/purchase_order_pdf_download.html', {'pdf_base64': pdf_base64})

#     except Exception as e:
#         return HttpResponse(f'Error generating PDF: {str(e)}')


    
@login_required
def purchsae_download_pdf(request, id):
    purchase_ord = get_object_or_404(Purchase_order, id=id)
    items = purchase_order_items.objects.filter(purchase_order_id=id)

    sum_total = purchase_order_items.objects.filter(purchase_order_id=id).aggregate(total=Sum('po_total'))['total']
    # Set to 0 if no items are found or the total is None
    sum_total = sum_total or 0
    gst_percentage = 0

    total_gst = float(purchase_ord.po_igstval) + float(purchase_ord.po_cgstval) + float(purchase_ord.po_sgstval)

    # Calculate GST percentage
    if purchase_ord.po_total:  # Ensure po_total is not zero or None
        gst_percentage = (total_gst / float(purchase_ord.po_total)) * 100
    else:
        gst_percentage = 0  # or handle the division by zero case appropriately

    context = {
        'purchase_ord':purchase_ord,
        'purchase_ord_item_data':items,
         'sum_total': sum_total,
         'gst_percentage': gst_percentage
        }
    
    template = get_template('purchase/purchase_order/purchase_order_pdf_download.html')
    html_string = template.render(context)
    
    base_url = request.build_absolute_uri('/')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="PO.pdf"'
    
    try:
        HTML(string=html_string, base_url=base_url).write_pdf(response)
        return response
       
    except Exception as e:
        return HttpResponse(f'Error generating PDF: {str(e)}')



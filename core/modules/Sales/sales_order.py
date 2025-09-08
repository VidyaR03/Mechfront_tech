from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db.models import Q
from datetime import datetime

import inflect
from weasyprint import HTML
from core.modules import template_path
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect,HttpResponse
from core.models import sales_order, sales_order_items, customer, transporter, inventory, godown,quotation,quotation_items
from core.modules.login.login import login_required
from django.template.loader import get_template
from django.contrib import messages



@login_required
def sales_order_list_view(request):
    sales_order_list = sales_order.objects.all().order_by('-id')
    context = {
        'sales_order_list':sales_order_list
        }
    return render(request,template_path.sales_order_list,context)



def generate_sales_order_number():
    current_year = datetime.now().year
    prefix = f"SO{current_year}"
    last_sales_order = sales_order.objects.filter(so_number__startswith=prefix).order_by('id').last()
    if last_sales_order:
        last_number = int(last_sales_order.so_number[-3:])
        new_number = last_number + 1
    else:
        new_number = 1
    return f"{prefix}{new_number:03d}"

@login_required
def add_sales_order_data(request):
    current_date = datetime.now().date()

    if request.method == "GET":
        customer_name = customer.objects.all()
        godown_name = godown.objects.all()
        transporter_name = transporter.objects.all()
        quotation_list = quotation.objects.all()

        shipping_address_list = []
        for i in customer_name:
            shipping_address_list.append(i.shipping_1_attention)
            shipping_address_list.append(i.shipping_2_attention)
            shipping_address_list.append(i.shipping_2_attention)
        dispatch_through = transporter.objects.all()
        item_data = inventory.objects.all()
        context ={ 
            'customer_name' : customer_name,
            'dispatch_through' : dispatch_through,
            'item_data': item_data,
            'godown_name':godown_name,
            'current_date':current_date,
            'transporter_name':transporter_name,
            'quotation_list':quotation_list,
            }

        return render(request, template_path.add_sales_order, context)
    elif request.method == "POST":
        so_number = generate_sales_order_number()
        so_due_date_str = request.POST.get('due_date', '')
        if so_due_date_str:
            so_due_date = datetime.strptime(so_due_date_str, '%d-%m-%Y').date()
        else:
            so_due_date = datetime.now().date()
        so_shipping_address = request.POST.get('shipping_address', None)
        so_date_str = request.POST.get('so_date', '')
        if so_date_str:
            so_date = datetime.strptime(so_date_str, '%d-%m-%Y').date()
        else:
            so_date = datetime.now().date()

        sales_order_data = {
            'so_date':so_date,
            'so_number':so_number,
            'so_payment_terms':request.POST['payment_term'],
            'so_customer_name':customer.objects.filter(id=request.POST['customer_Name']).first(),
            'so_due_date':so_due_date,
            # 'so_packaging_forwording':request.POST['packaging_forwading'],
            'so_order_confirmation_no':request.POST['order_confirmation_no'],
            'so_supply_place':request.POST['place_of_supply'],
            'so_destination':request.POST['destination'],
            'so_dispatch':request.POST['transporter_name'],
            'so_sales_person':request.POST['sales_person'],
            # 'so_contact_person_email':request.POST['contact_person_email'],
            'so_invoice_type':request.POST['invoice_type'],
            'so_delivery_type':request.POST['delivery_type'],
            'so_buyer_order_no':request.POST['buyer_order_no'],
            'so_buyer_order_date':request.POST['buyer_order_date'],
            'so_shipping_address':so_shipping_address,
            'so_dc_no_1':request.POST['dc_no_1'],
            'so_dc_date_1':request.POST['dc_date_1'],
            'so_dc_no_2':request.POST['dc_no_2'],
            'so_dc_date_2':request.POST['dc_date_2'],
            'so_dc_no_3':request.POST['dc_no_3'],
            'so_dc_date_3':request.POST['dc_date_3'],
            'so_dc_no_4':request.POST['dc_no_4'],
            'so_ewaybill_no_1':request.POST['so_ewaybill_no_1'],
            'so_ewaybill_no_2':request.POST['so_ewaybill_no_2'],
            'so_ewaybill_no_3':request.POST['so_ewaybill_no_3'],
            'so_ewaybill_no_4':request.POST['so_ewaybill_no_4'],
            'so_invoce_no_1':request.POST['invoice_no_1'],
            'so_invoce_date_1':request.POST['invoice_date_1'],
            'so_invoce_no_2':request.POST['invoice_no_2'],
            'so_invoce_date_2':request.POST['invoice_date_2'],
            'so_invoce_no_3':request.POST['invoice_no_3'],
            'so_invoce_date_3':request.POST['invoice_date_3'],
            'so_invoce_no_4':request.POST['invoice_no_4'],
            'so_invoce_date_4':request.POST['invoice_date_4'],
            'so_dispatch':transporter.objects.filter(id=request.POST['transporter_name']).first(),
            # 'so_freight':request.POST['freight'],
            'so_sub_total':request.POST['subtotal'],
            # 'so_cgstper':request.POST['cgstper'],
            'so_cgstval':request.POST['cgst'],
            # 'so_sgstper':request.POST['sgstper'],
            'so_sgstval':request.POST['sgst'],
            # 'so_igstper':request.POST['igstper'],
            'so_igstval':request.POST['igst'],
            'so_adjustment':request.POST['adjustment'],
            'so_sale_of_good':request.POST['sale_of_good'],
            'so_note':request.POST['note'],
            'so_total':request.POST['totalamt'],
            'gst_option':request.POST['gst_option'],
            'so_packaging_forwording_amount': request.POST.get('packaging_forwording_amount', '0'),
            'so_packaging_forwording_percentage': request.POST.get('packaging_forwording_percentage', '0'),
            'so_freight_amount': request.POST.get('freight_amount', '0'),
            'so_freight_percentage': request.POST.get('freight_percentage', '0'),
            'so_packaging_forwording_percentage_amt': request.POST.get('packaging_forwording_percentage_amt', '0'),
            'so_freight_percentage_amt': request.POST.get('freight_percentage_amt', '0'),
            'so_total_amt_word':request.POST['so_total_amt_word'],
            'so_packaging_forwording_amt_amt': request.POST.get('packaging_forwording_amt_amt', '0'),
            'so_freight_amt_amt': request.POST.get('freight_amt_amt', '0'),


        }
        sales_order_object = sales_order(**sales_order_data)
        sales_order_object.save()
        latest_sales_oreder_id = sales_order.objects.latest('id')
        i = 0
        max_row = int(request.POST.get('iid[]',0))
        
        while i <= max_row:
            so_item = sales_order_items(
                so_item_code = request.POST.get(f'itemcode_{i}'),
                so_description_goods = request.POST.get(f'item_{i}'),
                so_godown = request.POST.get(f'godown_{i}'),
                so_hsn = request.POST.get(f'hsn_{i}'),
                so_qantity = request.POST.get(f'qty_{i}'),
                so_uom = request.POST.get(f'uom_{i}'),
                so_unit_price = request.POST.get(f'rate_{i}'),
                so_discount = request.POST.get(f'discount_{i}'),
                so_tax_rate = request.POST.get(f'taxrate_{i}'),
                so_tax_amount = request.POST.get(f'taxamt_{i}'),
                so_total = request.POST.get(f'total_{i}'),
                date = request.POST.get('date'),
                so_sales_order_id = latest_sales_oreder_id.id
            )
            so_item.save()
            i = i+1
            messages.success(request, 'Sales Order Created Successfully.')

        return redirect('sales_order_list')
    
def check_duplicate_sales_order_no(request):
    sales_order_no = request.GET.get('sales_order_no')
    is_duplicate = sales_order.objects.filter(so_number=sales_order_no).exists()
    return JsonResponse({'is_duplicate': is_duplicate})


@login_required
def edit_sales_order_data(request,id):
    if request.method == "GET":
        sales_order_data = get_object_or_404(sales_order, id=id)
        customer_name = sales_order_data.so_customer_name
        all_customer_name = customer.objects.all()
        godown_name = godown.objects.all()
        item_data = inventory.objects.all()
        dispatch_through = sales_order_data.so_dispatch
        all_dispatch_through = transporter.objects.all()
        sales_order_item = sales_order_items.objects.filter(so_sales_order_id = id)
        len_sales_order_item = len(sales_order_item)
        # for i in sales_order_item:
        #     print(i.so_item_code,">>>>>>>>>>>>>>>>>>>>>>>")
        shipping_address_list = []
        for i in all_customer_name:
            shipping_address_list.append(i.shipping_1_attention)
            shipping_address_list.append(i.shipping_2_attention)
            shipping_address_list.append(i.shipping_2_attention)
        item_data = inventory.objects.all()
        context ={ 
            'sales_order_item' : sales_order_item,
            'all_customer_name' : all_customer_name,
            'sales_order_data':sales_order_data,
            'all_dispatch_through' : all_dispatch_through,
            'item_data': item_data,
            'godown_name':godown_name,
            'len_sales_order_item':len_sales_order_item
            
            }
        return render(request, template_path.edit_sales_order, context)
    elif request.method == "POST":
        sales_order_data = get_object_or_404(sales_order, id=id)
        id = sales_order_data.id
        so_date_str = request.POST['sales_order_date']
        so_due_date_str = request.POST['due_date']
        so_due_date = datetime.strptime(so_due_date_str, '%d-%m-%Y').date()
        so_date = datetime.strptime(so_date_str, '%d-%m-%Y').date()
        sales_order_data = {
            'id':id,
            'so_date':so_date,
            'so_number':request.POST['sales_order_no'],
            'so_payment_terms':request.POST['payment_term'],
            'so_customer_name':customer.objects.filter(id=request.POST['customer_Name']).first(),
            'so_due_date':so_due_date,
            # 'so_packaging_forwording':request.POST['packaging_forwading'],
            'so_order_confirmation_no':request.POST['order_confirmation_no'],
            'so_supply_place':request.POST['place_of_supply'],
            'so_destination':request.POST['destination'],
            'so_sales_person':request.POST['sales_person'],
            # 'so_contact_person_email':request.POST['contact_person_email'],
            'so_invoice_type':request.POST['invoice_type'],
            'so_delivery_type':request.POST['delivery_type'],
            'so_buyer_order_no':request.POST['buyer_order_no'],
            'so_buyer_order_date':request.POST['buyer_order_date'],
            'so_shipping_address':request.POST['shipping_address'],
            'so_dc_no_1':request.POST['dc_no_1'],
            'so_dc_date_1':request.POST['dc_date_1'],
            'so_dc_no_2':request.POST['dc_no_2'],
            'so_dc_date_2':request.POST['dc_date_2'],
            'so_dc_no_3':request.POST['dc_no_3'],
            'so_dc_date_3':request.POST['dc_date_3'],
            'so_dc_no_4':request.POST['dc_no_4'],
            'so_invoce_no_1':request.POST['invoice_no_1'],
            'so_invoce_date_1':request.POST['invoice_date_1'],
            'so_invoce_no_2':request.POST['invoice_no_2'],
            'so_invoce_date_2':request.POST['invoice_date_2'],
            'so_invoce_no_3':request.POST['invoice_no_3'],
            'so_invoce_date_3':request.POST['invoice_date_3'],
            'so_invoce_no_4':request.POST['invoice_no_4'],
            'so_invoce_date_4':request.POST['invoice_date_4'],
            'so_ewaybill_no_1':request.POST['so_ewaybill_no_1'],
            'so_ewaybill_no_2':request.POST['so_ewaybill_no_2'],
            'so_ewaybill_no_3':request.POST['so_ewaybill_no_3'],
            'so_ewaybill_no_4':request.POST['so_ewaybill_no_4'],
            'so_dispatch':transporter.objects.filter(id=request.POST['transporter_name']).first(),
            # 'so_freight':request.POST['freight'],
            'so_sub_total':request.POST['subtotal'],
            # 'so_cgstper':request.POST['cgstper'],
            'so_cgstval':request.POST['cgst'],
            # 'so_sgstper':request.POST['sgstper'],
            'so_sgstval':request.POST['sgst'],
            # 'so_igstper':request.POST['igstper'],
            'so_igstval':request.POST['igst'],
            'so_adjustment':request.POST['adjustment'],
            'so_sale_of_good':request.POST['sale_of_good'],
            'so_note':request.POST['note'],
            'so_total':request.POST['totalamt'],
            'gst_option':request.POST['gst_option'],
            'so_packaging_forwording_amount': request.POST.get('packaging_forwording_amount', '0'),
            'so_packaging_forwording_percentage': request.POST.get('packaging_forwording_percentage', '0'),
            'so_freight_amount': request.POST.get('freight_amount', '0'),
            'so_freight_percentage': request.POST.get('freight_percentage', '0'),
            'so_packaging_forwording_percentage_amt': request.POST.get('packaging_forwording_percentage_amt', '0'),
            'so_freight_percentage_amt': request.POST.get('freight_percentage_amt', '0'),
            'so_total_amt_word':request.POST['so_total_amt_word'],
            'so_packaging_forwording_amt_amt': request.POST.get('packaging_forwording_amt_amt', '0'),
            'so_freight_amt_amt': request.POST.get('freight_amt_amt', '0'),


        }
        sales_order_object = sales_order(**sales_order_data)
        sales_order_object.save()
        # latest_sales_order_id = sales_order.objects.latest('id')
        i = 1
        max_row = int(request.POST.get('iid[]', 0))
        sales_order_items.objects.filter(so_sales_order_id = id).delete()

        while i <= max_row:
            item_code = request.POST.get(f'itemcode_{i}')
            if item_code:
                so_item = sales_order_items(
                    so_item_code = request.POST.get(f'itemcode_{i}'),
                    so_description_goods = request.POST.get(f'item_{i}'),
                    so_godown = request.POST.get(f'godown_{i}'),
                    so_hsn = request.POST.get(f'hsn_{i}'),
                    so_qantity = request.POST.get(f'qty_{i}'),
                    so_uom = request.POST.get(f'uom_{i}'),
                    so_unit_price = request.POST.get(f'rate_{i}'),
                    so_discount = request.POST.get(f'discount_{i}'),
                    so_tax_rate = request.POST.get(f'taxrate_{i}'),
                    so_tax_amount = request.POST.get(f'taxamt_{i}'),
                    so_total = request.POST.get(f'total_{i}'),
                    so_sales_order_id = id
                )
                so_item.save()
            i = i+1
        messages.success(request, 'Sales Order Updated Successfully.')

        return redirect('sales_order_list')
    

@login_required
def delete_sales_order_data(request, id):
    # Get the customer instance based on the provided ID
    sales_order_instance = get_object_or_404(sales_order, id=id)    
    sales_order_item_instance = sales_order_items.objects.filter(so_sales_order_id = id)
    # if request.method == 'POST':
    sales_order_instance.delete()
    sales_order_item_instance.delete()
    messages.error(request, 'Sales Order Deleted.')
    return redirect('sales_order_list') 



# @csrf_exempt
# @require_POST
# def get_item_code_details(request):
#     name_starts_with = request.POST.get('name_startsWith', '')[:2]
#     # items_details = request.POST.getlist('itemsdetails[]', '')
#     items = inventory.objects.filter(inventory_name__istartswith=name_starts_with)
#     data = []
#     for item in items:
#         item_data = (
#             f"{item.item_code}|{item.inventory_name}|{item.hsn}|1|"
#             f"{item.default_discount}|{item.intrastate_gst}|{item.interstate_gst}|0|"
#         )
#         data.append(item_data)
#     return JsonResponse(data, safe=False)


def show_pdf(request, id):
    sales = get_object_or_404(sales_order, id=id)
    items = sales_order_items.objects.filter(so_sales_order_id = id)
    customer_data = sales.so_customer_name
    chunk_size = 14
    for index, item in enumerate(items, start=1):
            item.sr_no = index

    combined_chunks = [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]


    if combined_chunks and len(combined_chunks[-1]) < chunk_size:
        combined_chunks[-1].extend([None] * (chunk_size - len(combined_chunks[-1])))



    
    list_n = []
    count_page = int(len(items) / 12)
    next = False
    if (len(items) % 12) != 0:
        next = True
        count_page += 1    
        



          # Calculate total quantity
    total_quantity = sum(float(item.so_qantity) for item in items)


    
    
    if items.exists():
            purchase_id = items.first().so_sales_order_id
    else:
        purchase_id = 'N/A'

    
    p = inflect.engine()
    total_amount_in_words = p.number_to_words(sales.so_total)
    total_amount_in_words = total_amount_in_words.title()
    total_amount_in_words = total_amount_in_words.replace(",", "")



    total_amount = sum(float(item.so_total) for item in items)



    context = {
        'sales':sales,
        'items':items,
        'count_page': list(range(1, count_page + 1)),
        'item_list': combined_chunks,


        'total_quantity':total_quantity,
        'total_amount_in_words':total_amount_in_words,
        'total_amount':total_amount,
        'purchase_id':purchase_id,
        'gst_number':customer_data.gst_number,
        'state':customer_data.state,
        'pan_number':customer_data.pan_number,
        'bank_name':customer_data.bank_name,
        'account_number':customer_data.account_number,
        'branch_name':customer_data.branch_name,
        'ifsc_code':customer_data.ifsc_code,
        'street':customer_data.street,
        'city':customer_data.city,
        'pincode':customer_data.pincode,
        'gst_uin':customer_data.gst_uin,
        'contact_number':customer_data.contact_number,
        'bill_company_name':customer_data.company_name,
        'bill_city':customer_data.city,
        'com_state':customer_data.com_state,
        'bill_pincode':customer_data.pincode,
        'bill_gst_uin':customer_data.gst_uin,
       
        'shipping_street':customer_data.shipping_1_street,
        'shipping_contact_number':customer_data.shipping_1_contact_number,
        'shipping_city':customer_data.shipping_1_city,
        'shipping_state':customer_data.shipping_1_state,
        'shipping_pincode':customer_data.shipping_1_pincode,
        'shipping_gst_uin':customer_data.shipping_1_gst_uin,
        'so_order_no': sales.id,
        'so_buyer_order_no': sales.so_buyer_order_no,
        'so_payment_terms': sales.so_payment_terms,
        'so_dispatch': sales.so_dispatch.name if sales.so_dispatch else '',
        'so_delivery_type': sales.so_delivery_type,
        'so_destination': sales.so_destination,
        'so_invoice_type': sales.so_invoice_type,
        'so_due_date': sales.so_due_date,
        'so_sales_person': sales.so_sales_person,
        'ship_to_name': customer_data.company_name,
        'ship_to_address': f"{customer_data.shipping_1_street}, {customer_data.shipping_1_city}, {customer_data.shipping_1_state} {customer_data.shipping_1_pincode}",
        'ship_to_gst_uin': customer_data.shipping_1_gst_uin,
        'ship_to_contact_number': customer_data.shipping_1_contact_number,
        'ship_to_state': customer_data.shipping_1_state,



    }
    return render(request, template_path.sales_pdf,context)





# @login_required
# def show_pdf(request, id):
#     sales = get_object_or_404(sales_order, id=id)

#     sales_item_data = sales_order_items.objects.filter(so_sales_order_id = id)

#     context = {
#         'sales':sales,
#         'sales_item_data':sales_item_data
#         }
#     return render(request, template_path.sales_pdf, context)

def download_sales_order_pdf(request, id):
    # Fetch the sales order and related items
    sales = get_object_or_404(sales_order, id=id)
    items = sales_order_items.objects.filter(so_sales_order_id=id)
    customer_data = sales.so_customer_name

    # Pagination and chunking setup
    chunk_size = 14
    for index, item in enumerate(items, start=1):
        item.sr_no = index
    combined_chunks = [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]
    if combined_chunks and len(combined_chunks[-1]) < chunk_size:
        combined_chunks[-1].extend([None] * (chunk_size - len(combined_chunks[-1])))

    # Count pages and handle pagination
    count_page = (len(items) + 11) // 12  # round up page count
    next = (len(items) % 12) != 0

    # Calculate total quantity
    total_quantity = sum(float(item.so_qantity) for item in items)

    # Handle purchase ID display
    purchase_id = items.first().so_sales_order_id if items.exists() else 'N/A'

    # Convert total amount to words
    p = inflect.engine()
    total_amount_in_words = p.number_to_words(sales.so_total).title().replace(",", "")

    # Calculate total amount
    total_amount = sum(float(item.so_total) for item in items)



    if items.exists():
            
            sales_id = items.first().so_sales_order_id
    else:

        sales_id = 'N/A'

    # Define the context for the template
    context = {
        'sales': sales,
        'items': items,
        'count_page': list(range(1, count_page + 1)),
        'item_list': combined_chunks,
        'total_quantity': total_quantity,
        'total_amount_in_words': total_amount_in_words,
        'total_amount': total_amount,
        'purchase_id': purchase_id,
        'gst_number': customer_data.gst_number,
        'state': customer_data.state,
        'pan_number': customer_data.pan_number,
        'bank_name': customer_data.bank_name,
        'account_number': customer_data.account_number,
        'branch_name': customer_data.branch_name,
        'ifsc_code': customer_data.ifsc_code,
        'street': customer_data.street,
        'city': customer_data.city,
        'pincode': customer_data.pincode,
        'gst_uin': customer_data.gst_uin,
        'contact_number': customer_data.contact_number,
        'bill_company_name': customer_data.company_name,
        'bill_city': customer_data.city,
        'com_state': customer_data.com_state,
        'bill_pincode': customer_data.pincode,
        'bill_gst_uin': customer_data.gst_uin,
        'shipping_street': customer_data.shipping_1_street,
        'shipping_contact_number': customer_data.shipping_1_contact_number,
        'shipping_city': customer_data.shipping_1_city,
        'shipping_state': customer_data.shipping_1_state,
        'shipping_pincode': customer_data.shipping_1_pincode,
        'shipping_gst_uin': customer_data.shipping_1_gst_uin,
        'so_order_no': sales.id,
        'so_buyer_order_no': sales.so_buyer_order_no,
        'so_payment_terms': sales.so_payment_terms,
        'so_dispatch': sales.so_dispatch.name if sales.so_dispatch else '',
        'so_delivery_type': sales.so_delivery_type,
        'so_destination': sales.so_destination,
        'so_invoice_type': sales.so_invoice_type,
        'so_due_date': sales.so_due_date,
        'so_sales_person': sales.so_sales_person,
        'ship_to_name': customer_data.company_name,
        'ship_to_address': f"{customer_data.shipping_1_street}, {customer_data.shipping_1_city}, {customer_data.shipping_1_state} {customer_data.shipping_1_pincode}",
        'ship_to_gst_uin': customer_data.shipping_1_gst_uin,
        'ship_to_contact_number': customer_data.shipping_1_contact_number,
        'ship_to_state': customer_data.shipping_1_state,
        'sales_id': sales_id,
        'so_date':sales.so_date
    }

    # Render the template with context
    template = get_template('sales/sales_order/pdf.html')
    html_string = template.render(context)

    # Ensure static files are correctly referenced
    base_url = request.build_absolute_uri('/')

    # Create an HTTP response with the PDF content type
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="sales_order.pdf"'

    try:
        # Generate PDF using WeasyPrint with correct base_url
        HTML(string=html_string, base_url=base_url).write_pdf(response)
        return response
    except Exception as e:
        return HttpResponse(f'Error generating PDF: {str(e)}')


def get_quotation_items(request, quotation_id):
    items = quotation_items.objects.filter(q_quotation_id=quotation_id)
    items_list = list(items.values())
    return JsonResponse(items_list, safe=False)

def get_shipping_address(request):
    customer_id = request.GET.get('customer_id')
    customer_obj = customer.objects.filter(id=customer_id).first()

    if customer_obj:
        # Create a list of shipping addresses from the customer object
        shipping_addresses = []
        
        # Check each shipping address field and add if not empty
        if customer_obj.shipping_1_attention:
            addr1 = f"{customer_obj.shipping_1_attention}, {customer_obj.shipping_1_street}, {customer_obj.shipping_1_city}, {customer_obj.shipping_1_state}, {customer_obj.shipping_1_pincode}"
            shipping_addresses.append({'value': addr1, 'state': customer_obj.shipping_1_state})
        
        if customer_obj.shipping_2_attention:
            addr2 = f"{customer_obj.shipping_2_attention}, {customer_obj.shipping_2_street}, {customer_obj.shipping_2_city}, {customer_obj.shipping_2_state}, {customer_obj.shipping_2_pincode}"
            shipping_addresses.append({'value': addr2, 'state': customer_obj.shipping_2_state})
        
        if customer_obj.shipping_3_attention:
            addr3 = f"{customer_obj.shipping_3_attention}, {customer_obj.shipping_3_street}, {customer_obj.shipping_3_city}, {customer_obj.shipping_3_state}, {customer_obj.shipping_3_pincode}"
            shipping_addresses.append({'value': addr3, 'state': customer_obj.shipping_3_state})
        
        if customer_obj.shipping_4_attention:
            addr4 = f"{customer_obj.shipping_4_attention}, {customer_obj.shipping_4_street}, {customer_obj.shipping_4_city}, {customer_obj.shipping_4_state}, {customer_obj.shipping_4_pincode}"
            shipping_addresses.append({'value': addr4, 'state': customer_obj.shipping_4_state})

        return JsonResponse({
            'shipping_addresses': shipping_addresses,
            'gst_number': customer_obj.gst_number or '',
            'place_of_supply': customer_obj.state or '',
        })
    else:
        return JsonResponse({
            'shipping_addresses': [],
            'gst_number': '',
            'place_of_supply': '',
        })
from collections import defaultdict
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db.models import Q
from datetime import datetime
from core.modules import template_path
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect,HttpResponse
from core.models import delivery_challan, delivery_challan_items, customer, transporter, inventory,sales_order,sales_order_items
from core.modules.login.login import login_required
import inflect

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.templatetags.static import static
from weasyprint import HTML, CSS
from django.contrib.staticfiles import finders
from django.contrib import messages
import re
@login_required
def deliverychallan_list_view(request):
    delivery_challan_list = delivery_challan.objects.all().order_by('-id')
    context = {
        'delivery_challan_list':delivery_challan_list
        }
    return render(request,template_path.deliveryorder_list,context)


def get_financial_year():
    current_date = datetime.now()
    if current_date.month > 3:  # After March
        start_year = current_date.year
        end_year = current_date.year + 1
    else:  # January to March
        start_year = current_date.year - 1
        end_year = current_date.year
    return f"{start_year}-{end_year % 100:02d}"


# def generate_delivery_challan_number():
#     financial_year = get_financial_year()
#     prefix = f"DC"
#     last_delivery_challan = delivery_challan.objects.filter(dc_number__endswith=financial_year).order_by('id').last()
#     if last_delivery_challan:
#         # last_number = int(last_delivery_challan.dc_number.split('/')[0][2:])
#         # new_number = last_number + 1
#         # Extract the numeric part of the challan number, ignoring any suffix (like '-A')
#         challan_number = last_delivery_challan.dc_number.split('/')[0][2:]  # Extract '011' from 'DC011/2024-25'
#         suffix_match = re.search(r'-([A-Z])$', last_delivery_challan.dc_number)

#         # Check if there's a suffix like '-A'
#         if suffix_match:
#             last_number = int(challan_number)  # Number part (e.g., 11 from DC011)
#             next_number = last_number + 1  # Increment the number part
#         else:
#             last_number = int(challan_number)  # Handle regular case
#             next_number = last_number + 1
#     else:
#         new_number = 1
#     return f"{prefix}{new_number:03d}/{financial_year}"

import re

def generate_delivery_challan_number():
    financial_year = get_financial_year()
    prefix = f"DC/"
    
    # Fetch the last delivery challan for the current financial year
    last_delivery_challan = delivery_challan.objects.filter(dc_number__contains=financial_year).order_by('id').last()
    
    if last_delivery_challan:
        # Extract the main numeric part (e.g., '013' from 'DC013/2024-25-A' or 'DC013/2024-25')
        last_number_match = re.search(r'DC(\d{3})', last_delivery_challan.dc_number)
        if last_number_match:
            last_number = int(last_number_match.group(1))  # Extract '013' as an integer
            
            # Increment the number part
            new_number = last_number + 1
        else:
            # In case there is no match, set the first number
            new_number = 1
    else:
        # Start with 001 if no previous challan exists
        new_number = 1
    
    # Return the new delivery challan number, with leading zeros for the number part
    return f"DC{new_number:03d}/{financial_year}"




@login_required
def add_deliverychallan_data(request):
    if request.method == "GET":
        customer_name = customer.objects.all()
        dispatch_through = transporter.objects.all()
        item_data = inventory.objects.all()
        sales_order_list = sales_order.objects.all()
        current_date = datetime.now().strftime('%d-%m-%Y')
        context ={ 
            'customer_name' : customer_name,
            'dispatch_through' : dispatch_through,
            'item_data': item_data,
            'sales_order_list':sales_order_list,
            'current_date':current_date
            }

        return render(request, template_path.add_delivery_challan, context)
    elif request.method == "POST":
        dc_number = generate_delivery_challan_number()
        dc_date_str = request.POST['challan_date']
        dc_buyer_order_str = request.POST['buyer_order_date']
        dc_buyer_order_date = datetime.strptime(dc_buyer_order_str, '%d-%m-%Y').date()
        dc_date = datetime.strptime(dc_date_str, '%d-%m-%Y').date()

         # Optional: Check if customer_id exists
        customer_Name = request.POST.get('customer_Name', None)
        customer_id = request.POST.get('customer_id', None)
        customer_id_customer = request.POST.get('customer_id_select', None)
        if customer_id:
            dc_customer_name = customer.objects.filter(id=customer_id).first()
        else:
            dc_customer_name = customer.objects.filter(id=customer_id_customer).first()
        
        quotation_data = {
            'dc_date':dc_date,
            'dc_number':dc_number,
            'dc_payment_terms':request.POST['payment_term'],
            # 'dc_customer_name':customer.objects.filter(id=request.POST['customer_id']).first(),
            'dc_customer_name':dc_customer_name,

            'dc_type':request.POST['challan_type'],
            'dc_supply_place':request.POST['place_of_supply'],
            'dc_destination':request.POST['destination'],
            'dc_delivery_type':request.POST['delivery_type'],
            'dc_buyer_order_date':dc_buyer_order_date,
            'dc_buyer_order_no':request.POST['buyer_order_no'],
            'dc_customer_code':request.POST['dc_customer_code'],
            'dc_sales_order_no':request.POST['customer_Name'],
            'dc_shipping_address':request.POST['shipping_address'],
            'dc_sales_person':request.POST['sales_person'],
            'dc_landing_LR_RR_No':request.POST['lr_no'],
            # 'dc_packing':request.POST['packing'],
            'dc_dispatch':transporter.objects.filter(id=request.POST['transporter_name']).first(),
            # 'dc_freight':request.POST['freight'],
            'dc_sub_total':request.POST['subtotal'],
            # 'dc_cgstper':request.POST['cgstper'],
            'dc_cgstval':request.POST['cgst'],
            # 'dc_sgstper':request.POST['sgstper'],
            'dc_sgstval':request.POST['sgst'],
            # 'dc_igstper':request.POST['igstper'],
            'dc_igstval':request.POST['igst'],
            'dc_adjustment':request.POST['adjustment'],
            'dc_sale_of_good':request.POST['sale_of_good'],
            'dc_note':request.POST['note'],
            'dc_total':request.POST['totalamt'],
            'gst_option':request.POST['gst_option'],
            'dc_packaging_forwording_amount': request.POST.get('packaging_forwording_amount', '0'),
            'dc_packaging_forwording_percentage': request.POST.get('packaging_forwording_percentage', '0'),
            'dc_freight_amount': request.POST.get('freight_amount', '0'),
            'dc_freight_percentage': request.POST.get('freight_percentage', '0'),
            'totalamt_word':request.POST['totalamt_word'],
            'dc_packaging_forwording_percentage_amt': request.POST.get('packaging_forwording_percentage_amt', '0'),
            'dc_freight_percentage_amt': request.POST.get('freight_percentage_amt', '0'),
            'dc_packaging_forwording_amt_amt': request.POST.get('packaging_forwording_amt_amt', '0'),
            'dc_freight_amt_amt': request.POST.get('freight_amt_amt', '0'),



        }
        quotation_object = delivery_challan(**quotation_data)
        quotation_object.save()
        latest_deliverychallan_id = delivery_challan.objects.latest('id')
        i = 0
        max_row = int(request.POST.get('iid[]',0))
        while i <= max_row:
            dc_item = delivery_challan_items(
                dc_item_code = request.POST.get(f'itemcode_{i}'),
                dc_description_goods = request.POST.get(f'item_{i}'),
                dc_hsn = request.POST.get(f'hsn_{i}'),
                dc_qantity = request.POST.get(f'qty_{i}'),
                dc_uom = request.POST.get(f'uom_{i}'),
                dc_unit_price = request.POST.get(f'rate_{i}'),
                dc_discount = request.POST.get(f'discount_{i}'),
                dc_tax_rate = request.POST.get(f'taxrate_{i}'),
                dc_tax_amount = request.POST.get(f'taxamt_{i}'),
                dc_total = request.POST.get(f'total_{i}'),
                delivery_challan_id = latest_deliverychallan_id.id
            )

            dc_item.save()
            i = i+1
        messages.success(request, 'Delivery Challan Created Successfully.')

        return redirect('delivery_challan_list')
    

@login_required
def edit_delivery_challan_data(request, id):
    if request.method == "GET":
        challan_data = get_object_or_404(delivery_challan, id=id)
        customer_name = challan_data.dc_customer_name
        # challan_data = challan.objects.filter(id = id).first()
        # customer_name = customer.objects.filter(id = challan_data.q_customer_name_id.id)
        # dispatch_through = transporter.objects.filter(id = challan_data.q_dispatch_id.id)
        dispatch_through = challan_data.dc_dispatch
        item_data = inventory.objects.all()
        all_dispatch_through = transporter.objects.all()
        all_customer_name = customer.objects.all()
        challan_item_data = delivery_challan_items.objects.filter(delivery_challan_id = id)
        len_dc_items = len(challan_item_data)
        
        context ={ 
            'len_dc_items':len_dc_items,
            'customer_name' : customer_name,
            'all_customer_name':all_customer_name,
            'dispatch_through' : dispatch_through,
            'item_data': item_data,
            'challan_item_data':challan_item_data,
            'challan_data': challan_data,
            'all_dispatch_through':all_dispatch_through
            }

        return render(request, template_path.edit_delivery_challan, context)
    elif request.method == "POST":
        challan_data = get_object_or_404(delivery_challan, id=id)
        id = challan_data.id
        dc_date_str = request.POST['challan_date']
        dc_buyer_order_str = request.POST['buyer_order_date']
        dc_buyer_order_date = datetime.strptime(dc_buyer_order_str, '%d-%m-%Y').date()
        dc_date = datetime.strptime(dc_date_str, '%d-%m-%Y').date()
        

        quotation_data = {
            'id': id,
            'dc_number':request.POST['challan_no'],
            'dc_date':dc_date,
            'dc_payment_terms':request.POST['payment_term'],
            'dc_customer_name':customer.objects.filter(id=request.POST['customer_id']).first(),
            'dc_type':request.POST['challan_type'],
            'dc_supply_place':request.POST['place_of_supply'],
            'dc_destination':request.POST['destination'],
            'dc_delivery_type':request.POST['delivery_type'],
            'dc_customer_code':request.POST['dc_customer_code'],
            'dc_buyer_order_date':dc_buyer_order_date,
            'dc_buyer_order_no':request.POST['buyer_order_no'],
            'dc_sales_order_no':request.POST['customer_Name'],
            'dc_shipping_address':request.POST['shipping_address'],
            'dc_sales_person':request.POST['sales_person'],
            'dc_landing_LR_RR_No':request.POST['lr_no'],
            # 'dc_packing':request.POST['packing'],
            'dc_dispatch':transporter.objects.filter(id=request.POST['transporter_name']).first(),
            # 'dc_freight':request.POST['freight'],
            'dc_sub_total':request.POST['subtotal'],
            # 'dc_cgstper':request.POST['cgstper'],
            'dc_cgstval':request.POST['cgst'],
            # 'dc_sgstper':request.POST['sgstper'],
            'dc_sgstval':request.POST['sgst'],
            # 'dc_igstper':request.POST['igstper'],
            'dc_igstval':request.POST['igst'],
            'dc_adjustment':request.POST['adjustment'],
            'dc_sale_of_good':request.POST['sale_of_good'],
            'dc_note':request.POST['note'],
            'dc_total':request.POST['totalamt'],
            'gst_option':request.POST['gst_option'],
            'dc_packaging_forwording_amount': request.POST.get('packaging_forwording_amount', '0'),
            'dc_packaging_forwording_percentage': request.POST.get('packaging_forwording_percentage', '0'),
            'dc_freight_amount': request.POST.get('freight_amount', '0'),
            'dc_freight_percentage': request.POST.get('freight_percentage', '0'),
            'totalamt_word':request.POST['totalamt_word'],
            'dc_packaging_forwording_percentage_amt': request.POST.get('packaging_forwording_percentage_amt', '0'),
            'dc_freight_percentage_amt': request.POST.get('freight_percentage_amt', '0'),
            'dc_packaging_forwording_amt_amt': request.POST.get('packaging_forwording_amt_amt', '0'),
            'dc_freight_amt_amt': request.POST.get('freight_amt_amt', '0'),


        }
        quotation_object = delivery_challan(**quotation_data)
        quotation_object.save()
        # latest_deliverychallan_id = delivery_challan.objects.latest('id')
        i = 1
        max_row = int(request.POST.get('iid[]',0))
        delivery_challan_items.objects.filter(delivery_challan_id = id).delete()
        for i in range(1, max_row + 1):
            dc_item_code = request.POST.get(f'itemcode_{i}')

            # Only proceed if dc_item_code is not null or empty
            if dc_item_code:
                dc_item = delivery_challan_items(
                    dc_item_code = request.POST.get(f'itemcode_{i}'),
                    dc_description_goods = request.POST.get(f'item_{i}'),
                    dc_hsn = request.POST.get(f'hsn_{i}'),
                    dc_qantity = request.POST.get(f'qty_{i}'),
                    dc_uom = request.POST.get(f'uom_{i}'),
                    dc_unit_price = request.POST.get(f'rate_{i}'),
                    dc_discount = request.POST.get(f'discount_{i}'),
                    dc_tax_rate = request.POST.get(f'taxrate_{i}'),
                    dc_tax_amount = request.POST.get(f'taxamt_{i}'),
                    dc_total = request.POST.get(f'total_{i}'),
                    delivery_challan_id = id
                )

                dc_item.save()
                i = i+1
        messages.success(request, 'Delivery Challan Updated Successfully.')
        return redirect('delivery_challan_list')
    
def check_duplicate_challan_no(request):
    quotation_no = request.GET.get('challan_no')
    is_duplicate = delivery_challan.objects.filter(dc_number=quotation_no).exists()
    # print(is_duplicate,"is_duplicate.........")
    return JsonResponse({'is_duplicate': is_duplicate})

@login_required
def delete_challan_data(request, id):
    # Get the customer instance based on the provided ID
    challan_instance = get_object_or_404(delivery_challan, id=id)    
    challan_item_instance = delivery_challan_items.objects.filter(delivery_challan_id = id)
    # if request.method == 'POST':
    challan_instance.delete()
    challan_item_instance.delete()
    messages.error(request, 'Delivery Challan Deleted.')

    return redirect('delivery_challan_list')


# @login_required
# def delivery_chalan_pdf(request, id):
#     dchallan = get_object_or_404(delivery_challan, id=id)

#     delivery_challan_data = delivery_challan_items.objects.filter(delivery_challan_id = id)

#     context = {
#         'dchallan':dchallan,
#         'delivery_challan_data':delivery_challan_data
#         }
#     return render(request, template_path.delivery_challan_pdf,context)
    


# @login_required
def delivery_chalan_pdf(request, id):
    dchallan = get_object_or_404(delivery_challan, id=id)

    items = delivery_challan_items.objects.filter(delivery_challan_id = id)
    total_quantity = sum(float(item.dc_qantity) for item in items)
    customer_data = dchallan.dc_customer_name

   
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

    # hsn_tax_details = []




    if items.exists():
            
            dc_id = items.first().delivery_challan_id
    else:

        dc_id = 'N/A'

   
    p = inflect.engine()
    total_amount_in_words = p.number_to_words(dchallan.dc_total)
    total_amount_in_words = total_amount_in_words.title()
    total_amount_in_words = total_amount_in_words.replace(",", "")


    total_amount = sum(float(item.dc_total) for item in items)


    for detail in items:
        if dchallan.gst_option == 'Interstate':
            detail.half_tax_amount = float(detail.dc_tax_rate)
            detail.half_tax_rate = float(detail.dc_tax_amount)
        else:
            detail.half_tax_amount = float(detail.dc_tax_amount) / 2
            detail.half_tax_rate = float(detail.dc_tax_rate) / 2 

    context = {
        'dchallan':dchallan,
        'items':items,
        'total_quantity':total_quantity,
        'customer_email':customer_data.cust_email,
        'customer_contact':customer_data.contact_number,
        'customer_pincode': customer_data.pincode,
        'customer_gst': customer_data.gst_number,
        'dc_id':dc_id,
        'bill_street':customer_data.street,
        'bill_city':customer_data.city,
        'bii_com_state':customer_data.com_state,
        'bill_pincode':customer_data.pincode,
        'bill_gst_uin':customer_data.gst_uin,
        'bill_contact_number':customer_data.contact_number,
        'shipping_1_street':customer_data.shipping_1_street,
        'shipping_1_city':customer_data.shipping_1_city,
        'shipping_1_state':customer_data.shipping_1_state,
        'shipping_1_pincode':customer_data.shipping_1_pincode,
        'shipping_1_gst_uin':customer_data.shipping_1_gst_uin,
        'shipping_1_contact_number':customer_data.shipping_1_contact_number,
        'company_name':customer_data.company_name,
        'total_amount_in_words':total_amount_in_words,
        'bank_name':customer_data.bank_name,
        'account_number':customer_data.account_number,
        'branch_name':customer_data.branch_name,
        'ifsc_code':customer_data.ifsc_code,
        # 'hsn_totals': dict(hsn_totals),
        # 'hsn_tax_details': hsn_tax_details,
        'total_amount':total_amount,
        'count_page': list(range(1, count_page + 1)),
        'item_list': combined_chunks,

    }
    return render(request, template_path.delivery_challan_pdf,context)




def download_delivery_chalan_pdf(request, id):
    dchallan = get_object_or_404(delivery_challan, id=id)
    items = delivery_challan_items.objects.filter(delivery_challan_id = id)

    total_quantity = sum(float(item.dc_qantity) for item in items)
    customer_data = dchallan.dc_customer_name

    total_quantity = sum(float(item.dc_qantity) for item in items)
    customer_data = dchallan.dc_customer_name

   
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
            
            dc_id = items.first().delivery_challan_id
    else:

        dc_id = 'N/A'
    


    hsn_totals = defaultdict(float)
    for item in items:
        try:
            amount = float(item.dc_total)
            hsn_totals[item.dc_hsn] += amount
        except (ValueError, TypeError):
            continue  
        
    
    hsn_tax_details = []

    print(hsn_totals)
   

    for hsn, taxable_value in hsn_totals.items():
        try:
            # Remove '%' symbol and convert to float
            cgst_rate_str = dchallan.dc_cgstper.strip('%')
            cgst_rate = float(cgst_rate_str)
            cgst_amount = (taxable_value * cgst_rate) / 100
            print(f"{cgst_amount} = {taxable_value} * {(cgst_rate / 100)}",'cgst_amount---', cgst_amount)
        except (ValueError, TypeError):
            cgst_rate = cgst_amount = 0.0

        try:
            # Remove '%' symbol and convert to float
            sgst_rate_str = dchallan.dc_sgstper.strip('%')
            sgst_rate = float(sgst_rate_str)
            sgst_amount = taxable_value * (sgst_rate / 100)
            print(sgst_amount)
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
        if dchallan.gst_option == 'Interstate':
            detail.half_tax_amount = float(detail.dc_tax_rate)
            detail.half_tax_rate = float(detail.dc_tax_amount)
        else:
            detail.half_tax_amount = float(detail.dc_tax_amount) / 2
            detail.half_tax_rate = float(detail.dc_tax_rate) / 2 


    p = inflect.engine()
    total_amount_in_words = p.number_to_words(dchallan.dc_total)
    total_amount_in_words = total_amount_in_words.title()



    total_amount = sum(float(item.dc_total) for item in items)
    template = get_template('sales/delivery_challan/pdf.html')



    total_amount_in_words = total_amount_in_words.replace(",", "")


    context = {
        'dchallan':dchallan,
        'items':items,
        'total_quantity':total_quantity,
        'customer_email':customer_data.cust_email,
        'customer_contact':customer_data.contact_number,
        'customer_pincode': customer_data.pincode,
        'customer_gst': customer_data.gst_number,
        'dc_id':dc_id,
        'bill_street':customer_data.street,
        'bill_city':customer_data.city,
        'bii_com_state':customer_data.com_state,
        'bill_pincode':customer_data.pincode,
        'bill_gst_uin':customer_data.gst_uin,
        'bill_contact_number':customer_data.contact_number,
        'shipping_1_street':customer_data.shipping_1_street,
        'shipping_1_city':customer_data.shipping_1_city,
        'shipping_1_state':customer_data.shipping_1_state,
        'shipping_1_pincode':customer_data.shipping_1_pincode,
        'shipping_1_gst_uin':customer_data.shipping_1_gst_uin,
        'shipping_1_contact_number':customer_data.shipping_1_contact_number,
        'company_name':customer_data.company_name,
        'total_amount_in_words':total_amount_in_words,
        'bank_name':customer_data.bank_name,
        'account_number':customer_data.account_number,
        'branch_name':customer_data.branch_name,
        'ifsc_code':customer_data.ifsc_code,
        'hsn_totals': dict(hsn_totals),
        'hsn_tax_details': hsn_tax_details,
        'total_amount':total_amount,
        'count_page': list(range(1, count_page + 1)),
        'item_list': combined_chunks,

    }
   
    html_string = template.render(context)
    # Ensure static files are correctly referenced
    base_url = request.build_absolute_uri('/')

    # Create an HTTP response with the PDF content type
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="DC.pdf"'

    try:
        # Generate PDF using WeasyPrint with correct base_url
        HTML(string=html_string, base_url=base_url).write_pdf(response)
        return response

        # pdf_file = HTML(string=html_string, base_url=base_url).write_pdf()
        # # Encode PDF to base64
        # pdf_base64 = base64.b64encode(pdf_file).decode('utf-8')
        # # Render HTML page with PDF preview
        # return render(request, 'sales/quotation/pdf_preview.html', {'pdf_base64': pdf_base64})

    except Exception as e:
        return HttpResponse(f'Error generating PDF: {str(e)}')
    
# @csrf_exempt
# @require_POST
# def get_item_code_details(request):
#     name_starts_with = request.POST.get('name_startsWith', '')
#     items_details = request.POST.getlist('itemsdetails[]', '')
#     items = inventory.objects.filter(inventory_name__istartswith=name_starts_with)
#     data = []
#     for item in items:
#         item_data = (
#             f"{item.item_code}|{item.inventory_name}|{item.hsn}|{item.units}|{item.type}|"
#             f"{item.default_discount}|{item.intrastate_gst}|{item.interstate_gst}|{item.sales_rate}|{item.sku}"
#         )
#         data.append(item_data)
#     return JsonResponse(data, safe=False)

def get_sales_order_items(request, quotation_id):
    print(quotation_id,"quotation_id..............")
    items = sales_order_items.objects.filter(so_sales_order_id=quotation_id)
    items_list = list(items.values())
    return JsonResponse(items_list, safe=False)

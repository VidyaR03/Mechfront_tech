from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db.models import Q
from datetime import datetime
from core.modules import template_path
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect,HttpResponse
from core.models import quotation, quotation_items, customer, transporter, inventory
from core.modules.login.login import login_required
from django.contrib import messages
from weasyprint import HTML, CSS
import inflect
from django.template.loader import get_template


@login_required
def quotation_list_view(request):
    quotation_list = quotation.objects.all().order_by('-id')
    context = {
        'quotation_list':quotation_list
        }
    return render(request,template_path.quotation_list,context)

from django.utils import timezone

def get_financial_year():
    current_date = timezone.now()
    if current_date.month > 3:  # After March
        start_year = current_date.year
        end_year = current_date.year + 1
    else:  # January to March
        start_year = current_date.year - 1
        end_year = current_date.year
    return f"{start_year % 100:02d}-{end_year % 100:02d}"

def generate_quotation_number():
    financial_year = get_financial_year()
    prefix = f"MF/{financial_year}/"
    last_quotation = quotation.objects.filter(q_quotation_number__startswith=prefix).order_by('id').last()
    if last_quotation:
        last_number_part = last_quotation.q_quotation_number.split('/')[-1].split('-')[0]
        last_number = int(last_number_part)
        new_number = last_number + 1
    else:
        new_number = 1
    return f"{prefix}{new_number:03d}"


def check_duplicate_quotation_no(request):
    quotation_no = request.GET.get('quotation_no')
    is_duplicate = quotation.objects.filter(q_quotation_number=quotation_no).exists()
    return JsonResponse({'is_duplicate': is_duplicate})



@login_required
def add_quotation_data(request):
    if request.method == "GET":
        customer_name = customer.objects.all()
        dispatch_through = transporter.objects.all()
        item_data = inventory.objects.all()
        context ={ 
            'customer_name' : customer_name,
            'dispatch_through' : dispatch_through,
            'item_data': item_data
            }

        return render(request, template_path.add_quotation, context)
    elif request.method == "POST":
        q_date_str = request.POST['quotation_date']
        q_expirydate_str = request.POST['expiry_date']
        q_expiry_date = datetime.strptime(q_expirydate_str, '%d-%m-%Y').date()
        q_date = datetime.strptime(q_date_str, '%d-%m-%Y').date()

        q_quotation_number = generate_quotation_number()
        # print(q_quotation_number,"qn........")
        quotation_data = {
            'q_date':q_date,
            'q_quotation_number':q_quotation_number,
            # 'q_date':request.POST['quotation_date'],
            'q_payment_terms':request.POST['payment_term'],
            'q_customer_name':customer.objects.filter(id=request.POST['customer_id']).first(),
            'q_expiry_date':q_expiry_date,
            'q_supply_place':request.POST['place_of_supply'],
            'q_destination':request.POST['destination'],
            'q_delivery':request.POST['delivery'],
            'q_contact_person_name':request.POST['contact_person_name'],
            'q_contact_person_email':request.POST['contact_person_email'],
            'q_reference':request.POST['reference'],
            'q_packing':request.POST['packing'],
            'q_dispatch':transporter.objects.filter(id=request.POST['transporter_name']).first(),
            'q_sub_total':request.POST['subtotal'],
            # 'q_cgstper':request.POST['cgstper'],
            'q_cgstval':request.POST['cgst'],
            # 'q_sgstper':request.POST['sgstper'],
            'q_sgstval':request.POST['sgst'],
            # 'q_igstsper':request.POST['igstper'],
            'q_igstval':request.POST['igst'],
            'q_adjustment':request.POST['adjustment'],
            'q_sale_of_good':request.POST['sale_of_good'],
            'q_note':request.POST['note'],
            'q_total':request.POST['totalamt'],
            'gst_option':request.POST['gst_option'],
            'q_packaging_forwording_amount': request.POST.get('packaging_forwording_amount', '0'),
            'q_packaging_forwording_percentage': request.POST.get('packaging_forwording_percentage', '0'),
            'q_freight_amount': request.POST.get('freight_amount', '0'),
            'q_freight_percentage': request.POST.get('freight_percentage', '0.00'),
            'q_packaging_forwording_percentage_amt': request.POST.get('packaging_forwording_percentage_amt', '0'),
            'q_freight_percentage_amt': request.POST.get('freight_percentage_amt', '0'),
            'q_total_amt_word':request.POST['q_total_amt_word'],
            'q_packaging_forwording_amt_amt': request.POST.get('packaging_forwording_amt_amt', '0'),
            'q_freight_percentage_amt_amt': request.POST.get('freight_amt_amt', '0'),


        }

        quotation_object = quotation(**quotation_data)
        quotation_object.save()
        # print(quotation_object)
        latest_quotation_id = quotation.objects.latest('id')
        i = 0
        max_row = int(request.POST.get('iid[]',0))
        while i <= max_row:
            q_item = quotation_items(
                q_item_code = request.POST.get(f'itemcode_{i}'),
                q_description_goods = request.POST.get(f'item_{i}'),
                q_hsn = request.POST.get(f'hsn_{i}'),
                q_qantity = request.POST.get(f'qty_{i}'),
                q_uom = request.POST.get(f'uom_{i}'),
                q_unit_price = request.POST.get(f'rate_{i}'),
                q_discount = request.POST.get(f'discount_{i}'),
                q_tax_rate = request.POST.get(f'taxrate_{i}'),
                q_tax_amount = request.POST.get(f'taxamt_{i}'),
                q_total = request.POST.get(f'total_{i}'),
                q_quotation_id = latest_quotation_id.id
            )

            q_item.save()
            i = i+1
        messages.success(request, 'Quotation Created Successfully.')

        return redirect('quotation_list')
    

# def edit_quotation_data(request, id):
#     if request.method == "GET":
#         quotation_data = get_object_or_404(quotation, id=id)
#         customer_name = quotation_data.q_customer_name
#         print(customer_name.customer,"customer_name..............")
#         # quotation_data = quotation.objects.filter(id = id).first()
#         # customer_name = customer.objects.filter(id = quotation_data.q_customer_name_id.id)
#         # dispatch_through = transporter.objects.filter(id = quotation_data.q_dispatch_id.id)
#         dispatch_through = quotation_data.q_dispatch
#         item_data = inventory.objects.all()
#         all_dispatch_through = transporter.objects.all()
#         all_customer_name = customer.objects.all()
#         quotation_item_data = quotation_items.objects.filter(q_quotation_id = id)
#         len_quotation_item = len(quotation_item_data)
#         context ={ 
#             'customer_name' : customer_name,
#             'all_customer_name':all_customer_name,
#             'dispatch_through' : dispatch_through,
#             'item_data': item_data,
#             'quotation_item_data':quotation_item_data,
#             'quotation_data': quotation_data,
#             'all_dispatch_through':all_dispatch_through,
#             'len_quotation_item':len_quotation_item
#             }

#         return render(request, template_path.edit_quotation, context)
#     elif request.method == "POST":
#         quotation_data = get_object_or_404(quotation, id=id)
#         id = quotation_data.id
#         q_date_str = request.POST['quotation_date']
#         q_expirydate_str = request.POST['expiry_date']
#         q_expiry_date = datetime.strptime(q_expirydate_str, '%d-%m-%Y').date()
#         q_date = datetime.strptime(q_date_str, '%d-%m-%Y').date()
#         quotation_data = {
#             'id':id,
#             'q_date':q_date,
#             'q_quotation_number':request.POST['quotation_no'],

#             'q_payment_terms':request.POST['payment_term'],
#             'q_customer_name':customer.objects.filter(id=request.POST['customer_id']).first(),
#             'q_expiry_date':q_expiry_date,
#             # 'q_packaging_forwording':request.POST['packaging_forwading'],
#             'q_supply_place':request.POST['place_of_supply'],
#             'q_destination':request.POST['destination'],
#             'q_delivery':request.POST['delivery'],
#             'q_contact_person_name':request.POST['contact_person_name'],
#             'q_contact_person_email':request.POST['contact_person_email'],
#             'q_reference':request.POST['reference'],
#             'q_packing':request.POST['packing'],
#             'q_dispatch':transporter.objects.filter(id=request.POST['transporter_name']).first(),
#             # 'q_freight':request.POST['freight'],
#             'q_sub_total':request.POST['subtotal'],
#             # 'q_cgstper':request.POST['cgstper'],
#             'q_cgstval':request.POST['cgst'],
#             # 'q_sgstper':request.POST['sgstper'],
#             'q_sgstval':request.POST['sgst'],
#             # 'q_igstper':request.POST['igstper'],
#             'q_igstval':request.POST['igst'],
#             'q_adjustment':request.POST['adjustment'],
#             'q_sale_of_good':request.POST['sale_of_good'],
#             'q_note':request.POST['note'],
#             'q_total':request.POST['totalamt'],
#             'gst_option':request.POST['gst_option'],
#             'q_packaging_forwording_amount': request.POST.get('packaging_forwording_amount', '0'),
#             'q_packaging_forwording_percentage': request.POST.get('packaging_forwording_percentage', '0'),
#             'q_freight_amount': request.POST.get('freight_amount', '0'),
#             'q_freight_percentage': request.POST.get('freight_percentage', '0'),
#             'q_packaging_forwording_percentage_amt': request.POST.get('packaging_forwording_percentage_amt', '0'),
#             'q_freight_percentage_amt': request.POST.get('freight_percentage_amt', '0'),
#             'q_total_amt_word':request.POST['q_total_amt_word'],
#             'q_packaging_forwording_amt_amt': request.POST.get('packaging_forwording_amt_amt', '0'),
#             'q_freight_percentage_amt_amt': request.POST.get('freight_amt_amt', '0'),


#         }
#         quotation_object = quotation(**quotation_data)
#         quotation_object.save()
#         # latest_quotation_id = quotation.objects.latest('id')
#         i = 1
#         max_row = int(request.POST.get('iid[]',0))
#         quotation_items.objects.filter(q_quotation_id = id).delete()
#         while i <= max_row:
#             q_item = quotation_items(
#                 q_item_code = request.POST.get(f'itemcode_{i}'),
#                 q_description_goods = request.POST.get(f'item_{i}'),
#                 q_hsn = request.POST.get(f'hsn_{i}'),
#                 q_qantity = request.POST.get(f'qty_{i}'),
#                 q_uom = request.POST.get(f'uom_{i}'),
#                 q_unit_price = request.POST.get(f'rate_{i}'),
#                 q_discount = request.POST.get(f'discount_{i}'),
#                 q_tax_rate = request.POST.get(f'taxrate_{i}'),
#                 q_tax_amount = request.POST.get(f'taxamt_{i}'),
#                 q_total = request.POST.get(f'total_{i}'),
#                 q_quotation_id = id
#             )
#             q_item.save()
#             i = i+1

#         messages.success(request, 'Quotation Updated Successfully.')

#         return redirect('quotation_list')

@login_required
def edit_quotation_data(request, id):
    if request.method == "GET":
        quotation_data = get_object_or_404(quotation, id=id)
        customer_name = quotation_data.q_customer_name
        # print(customer_name.customer,"customer_name..............")
        # quotation_data = quotation.objects.filter(id = id).first()
        # customer_name = customer.objects.filter(id = quotation_data.q_customer_name_id.id)
        # dispatch_through = transporter.objects.filter(id = quotation_data.q_dispatch_id.id)
        dispatch_through = quotation_data.q_dispatch
        item_data = inventory.objects.all()
        all_dispatch_through = transporter.objects.all()
        all_customer_name = customer.objects.all()
        quotation_item_data = quotation_items.objects.filter(q_quotation_id = id)
        len_quotation_item = len(quotation_item_data)
        context ={ 
            'customer_name' : customer_name,
            'all_customer_name':all_customer_name,
            'dispatch_through' : dispatch_through,
            'item_data': item_data,
            'quotation_item_data':quotation_item_data,
            'quotation_data': quotation_data,
            'all_dispatch_through':all_dispatch_through,
            'len_quotation_item':len_quotation_item
            }

        return render(request, template_path.edit_quotation, context)
    elif request.method == "POST":
        quotation_data = get_object_or_404(quotation, id=id)
        id = quotation_data.id
        q_date_str = request.POST['quotation_date']
        q_expirydate_str = request.POST['expiry_date']
        q_expiry_date = datetime.strptime(q_expirydate_str, '%d-%m-%Y').date()
        q_date = datetime.strptime(q_date_str, '%d-%m-%Y').date()

        # Update the quotation_data
        quotation_data.q_date = q_date
        quotation_data.q_quotation_number = request.POST['quotation_no']
        quotation_data.q_payment_terms = request.POST['payment_term']
        quotation_data.q_customer_name = customer.objects.filter(id=request.POST['customer_id']).first()
        quotation_data.q_expiry_date = q_expiry_date
        quotation_data.q_supply_place = request.POST['place_of_supply']
        quotation_data.q_destination = request.POST['destination']
        quotation_data.q_delivery = request.POST['delivery']
        quotation_data.q_contact_person_name = request.POST['contact_person_name']
        quotation_data.q_contact_person_email = request.POST['contact_person_email']
        quotation_data.q_reference = request.POST['reference']
        quotation_data.q_packing = request.POST['packing']
        quotation_data.q_dispatch = transporter.objects.filter(id=request.POST['transporter_name']).first()
        quotation_data.q_sub_total = request.POST['subtotal']
        quotation_data.q_cgstval = request.POST['cgst']
        quotation_data.q_sgstval = request.POST['sgst']
        quotation_data.q_igstval = request.POST['igst']
        quotation_data.q_adjustment = request.POST['adjustment']
        quotation_data.q_sale_of_good = request.POST['sale_of_good']
        quotation_data.q_note = request.POST['note']
        quotation_data.q_total = request.POST['totalamt']
        quotation_data.gst_option = request.POST['gst_option']
        quotation_data.q_packaging_forwording_amount = request.POST.get('packaging_forwording_amount', '0')
        quotation_data.q_packaging_forwording_percentage = request.POST.get('packaging_forwording_percentage', '0')
        quotation_data.q_freight_amount = request.POST.get('freight_amount', '0')
        quotation_data.q_freight_percentage = request.POST.get('freight_percentage', '0.00')
        quotation_data.q_packaging_forwording_percentage_amt = request.POST.get('packaging_forwording_percentage_amt', '0')
        quotation_data.q_freight_percentage_amt = request.POST.get('freight_percentage_amt', '0')
        quotation_data.q_total_amt_word = request.POST['q_total_amt_word']
        quotation_data.q_packaging_forwording_amt_amt = request.POST.get('packaging_forwording_amt_amt', '0')
        quotation_data.q_freight_percentage_amt_amt = request.POST.get('freight_amt_amt', '0')

        quotation_data.save()

        # Delete old quotation items
        quotation_items.objects.filter(q_quotation_id=id).delete()

        # Loop through all item rows
        i = 1
        max_row = int(request.POST.get('iid[]', 0))
        while i <= max_row:
            q_item_code = request.POST.get(f'itemcode_{i}')
            q_description_goods = request.POST.get(f'item_{i}')
            q_hsn = request.POST.get(f'hsn_{i}')
            q_qantity = request.POST.get(f'qty_{i}')
            q_uom = request.POST.get(f'uom_{i}')
            q_unit_price = request.POST.get(f'rate_{i}')
            q_discount = request.POST.get(f'discount_{i}')
            q_tax_rate = request.POST.get(f'taxrate_{i}')
            q_tax_amount = request.POST.get(f'taxamt_{i}')
            q_total = request.POST.get(f'total_{i}')

            # Ensure that the item code and description are not empty
            if q_item_code and q_description_goods:
                q_item = quotation_items(
                    q_item_code=q_item_code,
                    q_description_goods=q_description_goods,
                    q_hsn=q_hsn,
                    q_qantity=q_qantity,
                    q_uom=q_uom,
                    q_unit_price=q_unit_price,
                    q_discount=q_discount,
                    q_tax_rate=q_tax_rate,
                    q_tax_amount=q_tax_amount,
                    q_total=q_total,
                    q_quotation_id=id
                )
                q_item.save()

            i += 1

        messages.success(request, 'Quotation Updated Successfully.')
        return redirect('quotation_list')


@csrf_exempt
@require_POST
def get_item_code_details(request):
    name_starts_with = request.POST.get('name_startsWith', '')
    items = inventory.objects.filter(item_code__istartswith=name_starts_with)[:10]  # Limit to 10 results for performance

    data = []
    for item in items:
        item_data = (
            f"{item.item_code}|{item.inventory_name}|{item.hsn}|1|"
            f"{item.default_discount}|{item.sales_rate}||{item.units}|{item.sales_information_description}"
        )
        data.append(item_data)

    print(data)  # Debugging: Print the data list
    return JsonResponse(data, safe=False)  
 

# @csrf_exempt
# @require_POST
# def get_item_code_details(request):
#     name_starts_with = request.POST.get('name_startsWith', '')
#     # items_details = request.POST.getlist('itemsdetails[]', '')
#     items = inventory.objects.filter(item_code__istartswith=name_starts_with)

#     data = []
#     for item in items:
#        item_data = (
#             f"{item.item_code}|{item.inventory_name}|{item.hsn}|1|"
#             f"{item.default_discount}|{item.sales_rate}||{item.units}|{item.sales_information_description}"
#         )
#     print(item_data)
#     print("***")
#     data.append(item_data)
#     return JsonResponse(data, safe=False)


@login_required
def delete_quotation_data(request, id):
    # Get the customer instance based on the provided ID
    quotation_instance = get_object_or_404(quotation, id=id)    
    quotation_item_instance = quotation_items.objects.filter(q_quotation_id = id)
    # if request.method == 'POST':
    quotation_instance.delete()
    quotation_item_instance.delete()
    messages.error(request, 'Quotation Deleted.')

    return redirect('quotation_list')  # Redirect to a success page or customer list




import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt  # Use this decorator if CSRF protection is enabled
def getitemscodedetails_1(request):
    if request.method == 'POST':
        try:
            # Assuming the data is sent as JSON
            data = json.loads(request.body)
            item_code = data.get('itemCode')

            # print(item_code)
            item_details = inventory.objects.filter(item_code__startswith=item_code)
            itemCode = [i.item_code for i in item_details]
            # Example response
            response_data = {"data":itemCode}
            # response_data = {'status': 'success', 'message': 'Data received successfully'}
            return JsonResponse(response_data)

        except json.JSONDecodeError as e:
            # Handle JSON decoding errors
            response_data = {'status': 'error', 'message': 'Invalid JSON data'}
            return JsonResponse(response_data, status=400)

    # Handle other HTTP methods if needed
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


# @login_required
# def show_quo_pdf(request, id):
#     quo = get_object_or_404(quotation, id=id)

#     quotation_item_data = quotation_items.objects.filter(q_quotation_id = id)

#     context = {
#         'quo':quo,
#         'quotation_item_data':quotation_item_data
#         }
#     return render(request, template_path.quo_pdf,context)


@login_required
def quotation_pdf(request, id):
    quo = quotation.objects.filter(id=id).first()
    if quo:
        print(quo.__dict__)

    list_item = quotation_items.objects.filter(q_quotation_id=id).all()
    chunk_size = 12
    for index, item in enumerate(list_item, start=1):
        
        item.sr_no = index
 
    combined_chunks = [list_item[i:i + chunk_size] for i in range(0, len(list_item), chunk_size)]
 
    if combined_chunks and len(combined_chunks[-1]) < chunk_size:
        combined_chunks[-1].extend([None] * (chunk_size - len(combined_chunks[-1])))
    list_n = []
    count_page = int(len(list_item) / 12)
    next = False
    if (len(list_item) % 12) != 0:
        next = True
        count_page += 1

    p = inflect.engine()
    total_amount_in_words = p.number_to_words(quo.q_total)
    template = get_template('sales/quotation/pdf.html')

    context={
        'quo':quo,
        'quo_item':list_item,
        'count_page': list(range(1, count_page + 1)),
        'item_list': combined_chunks,
        'total_amount_in_words':total_amount_in_words
    }
    return render(request, template_path.quo_pdf,context)


def download_qou_pdf(request, id):
    quo = quotation.objects.filter(id=id).first()
    list_item = quotation_items.objects.filter(q_quotation_id=id).all()
    chunk_size = 12
    for index, item in enumerate(list_item, start=1):
        item.sr_no = index
 
    combined_chunks = [list_item[i:i + chunk_size] for i in range(0, len(list_item), chunk_size)]
 
    if combined_chunks and len(combined_chunks[-1]) < chunk_size:
        combined_chunks[-1].extend([None] * (chunk_size - len(combined_chunks[-1])))
    list_n = []
    count_page = int(len(list_item) / 12)
    next = False
    if (len(list_item) % 12) != 0:
        next = True
        count_page += 1

    p = inflect.engine()
    total_amount_in_words = p.number_to_words(quo.q_total)
    template = get_template('sales/quotation/pdf.html')

    context={
        'quo':quo,
        'quo_item':list_item,
        'count_page': list(range(1, count_page + 1)),
        'item_list': combined_chunks,
        'total_amount_in_words':total_amount_in_words
    }
    
    html_string = template.render(context)
    # Ensure static files are correctly referenced
    base_url = request.build_absolute_uri('/')

    # Create an HTTP response with the PDF content type
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Quotation_{id}.pdf"'

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
    


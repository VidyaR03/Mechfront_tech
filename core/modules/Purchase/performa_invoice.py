from collections import defaultdict
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db.models import Q
from datetime import date, datetime
from django.template.loader import get_template
import inflect
from weasyprint import HTML
from core.modules import template_path
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect,HttpResponse
from core.models import Invoice, invoice_items, customer, transporter, inventory, godown,Performa_Invoice,performa_invoice_items,delivery_challan
from django.http import JsonResponse, HttpResponseBadRequest
import csv
from core.modules.login.login import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
@login_required
def performa_invoice_list_view(request):
    try:
        invoice_data = Performa_Invoice.objects.all().order_by('-id')
        context = {
            'invoice_data':invoice_data
            }
        return render(request,template_path.performa_invoice_list,context)
    except Exception as a:
        print(f'An Error Occured {a}')

def generate_proforma_invoice_number():
    current_year = datetime.now().year
    year_suffix = str(current_year)[-2:]  # Get last two digits of the current year
    prefix = f"MF{year_suffix}/PI-"
    last_proforma_invoice = Performa_Invoice.objects.filter(pi_number__startswith=prefix).order_by('id').last()
    if last_proforma_invoice:
        last_number = int(last_proforma_invoice.pi_number.split('-')[-1])
        new_number = last_number + 1
    else:
        new_number = 1
    return f"{prefix}{new_number:03d}"
 
@login_required
def performa_add_invoice_data(request):
    if request.method == "GET":
        customer_name = customer.objects.all()
        dispatch_through = transporter.objects.all()
        item_data = inventory.objects.all()
        godown_name = godown.objects.all()
        dc_list = delivery_challan.objects.all()


        context ={ 
            'customer_name' : customer_name,
            'dispatch_through' : dispatch_through,
            'item_data': item_data,
            'godown_name': godown_name,
            'dc_list':dc_list,
            }

        return render(request, template_path.performa_add_invoice, context)
    elif request.method == "POST":
        pi_number = generate_proforma_invoice_number()
        # print(pi_number,'PPPPPPPPPPPPPP')
        invoice_date_str = request.POST['invoice_date']
        invoice_due_date_str = request.POST['due_date']
        invoice_buyer_order_date_str = request.POST['buyer_order_date']
        
        invoice_due_date_date = datetime.strptime(invoice_due_date_str, '%d-%m-%Y').date() if invoice_due_date_str else date.today()
        invoice_buyerorder_date = datetime.strptime(invoice_buyer_order_date_str, '%d-%m-%Y').date() if invoice_buyer_order_date_str else date.today()
        invoice_date = datetime.strptime(invoice_date_str, '%d-%m-%Y').date() if invoice_date_str else date.today()
       

       
        if request.POST.get('note'):
            note = request.POST['note']
        else:
            note = ""

        customer_id = request.POST.get('customer_id', None)

        if customer_id:
            q_customer_name = delivery_challan.objects.get(id=customer_id)
            inv_customer_name = None  # Set inv_customer_name to None if customer_id exists
        else:
            q_customer_name = None
            customer_id_customer = request.POST.get('customer_id_select', None)

            if customer_id_customer:
                inv_customer_name = customer.objects.filter(id=customer_id_customer).first()
            else:
                inv_customer_name = None  # Default to None if customer_id_customer is empty or not provided

        
        
        print(q_customer_name,'q_customer_name')
        invoice_data = {
            'invoice_date': invoice_date,
            'pi_number':pi_number,
            'invoice_payment_terms':request.POST['payment_term'],
            'invoice_customer_name':q_customer_name,
            'invoice_customer':inv_customer_name,
            'invoice_eway_bill_no':request.POST['ewaybill_no'],
            'invoice_supply_place':request.POST['place_of_supply'],
            'invoice_delivery_no':request.POST['order_no'],
            'invoice_destination':request.POST['destination'],
            'invoice_due_date': invoice_due_date_date,
            'invoice_landing_LR_RR_No':request.POST['lrno'],
            'invoice_dispatch':request.POST['transporter_name'],
            'invoice_shipping_address': request.POST.get('shipping_address', None),

            'invoice_sales_person':request.POST['sales_person'],
            'invoice_vehicle_no':request.POST['vehicle_no'],
            'invoice_gst_no':request.POST['gst_no'],
            'invoice_buyer_order_no':request.POST['buyer_order_no'],
            'invoice_buyer_order_date':invoice_buyerorder_date,
            'invoice_dispatch':transporter.objects.filter(id=request.POST['transporter_name']).first(),
            'invoice_sub_total':request.POST['subtotal'],
            'invoice_cgstval':request.POST['cgst'],
            'invoice_sgstval':request.POST['sgst'],
            'invoice_igstval':request.POST['igst'],
            'invoice_adjustment':request.POST['adjustment'],
            'invoice_sale_of_good':request.POST['sale_of_good'],
            'invoice_note':request.POST['note'],
            'invoice_total':request.POST['totalamt'],
            'invoice_due': request.POST['totalamt'],
            'gst_option':request.POST['gst_option'],
            'cn_packaging_forwording_amount': request.POST.get('packaging_forwording_amount', '0'),
            'cn_packaging_forwording_percentage': request.POST.get('packaging_forwording_percentage', '0'),
            'cn_freight_amount': request.POST.get('freight_amount', '0'),
            'cn_freight_percentage': request.POST.get('freight_percentage', '0'),
            'cn_packaging_forwording_percentage_amt': request.POST.get('packaging_forwording_percentage_amt', '0'),
            'cn_freight_percentage_amt': request.POST.get('freight_percentage_amt', '0'),
            'cn_total_amt_word':request.POST['cn_total_amt_word'],
            'cn_packaging_forwording_amt_amt': request.POST.get('packaging_forwording_amt_amt', '0'),
            'cn_freight_percentage_amt_amt': request.POST.get('freight_amt_amt', '0'),
            'invoice_customer':customer.objects.filter(id=request.POST['customer_id_select']).first(),


        }
        Invoice_object = Performa_Invoice(**invoice_data)
        # cust_data = I_customer_name
        Invoice_object.save()
        latest_invoice_id = Performa_Invoice.objects.latest('id')
        # cust_data.cust_receive_amount += float(latest_invoice_id.invoice_total)
        # cust_data.due_date = latest_invoice_id.invoice_due_date
        # cust_data.save()
        i = 0
        max_row = int(request.POST.get('iid[]',0))
        while i <= max_row:
            current_date = datetime.now().date()  # Get current date

            invoice_item = performa_invoice_items(
                invoice_item_code = request.POST.get(f'itemcode_{i}'),
                invoice_description_goods = request.POST.get(f'item_{i}'),
                invoice_hsn = request.POST.get(f'hsn_{i}'),
                invoice_godown = request.POST.get(f'godown_{i}'),
                invoice_qantity = request.POST.get(f'qty_{i}'),
                invoice_uom = request.POST.get(f'uom_{i}'),
                invoice_unit_price = request.POST.get(f'rate_{i}'),
                invoice_discount = request.POST.get(f'discount_{i}'),
                invoice_tax_rate = request.POST.get(f'taxrate_{i}'),
                invoice_tax_amount = request.POST.get(f'taxamt_{i}'),
                invoice_total = request.POST.get(f'total_{i}'),
                invoice_id = latest_invoice_id.id,
                date = current_date,

                )
        
            invoice_item.save()
            i = i+1

        messages.success(request, 'Proforma Invoice Created Successfully.')

        return redirect('performa_invoice_list')
    

def check_duplicate_performa_invoice_no(request):
    invoice_no = request.GET.get('invoice_no')
    is_duplicate = Performa_Invoice.objects.filter(pi_number=invoice_no).exists()  # Check against the pi_number field
    return JsonResponse({'is_duplicate': is_duplicate})


@login_required  
def performa_edit_invoice_data(request, id):
    if request.method == "GET":
        
        invoice_data = get_object_or_404(Performa_Invoice, id=id)
        all_customer_name = customer.objects.all()
        all_dispatch_through = transporter.objects.all()
        item_data = inventory.objects.all()
        godown_name = godown.objects.all()
        customer_name = invoice_data.invoice_customer_name
        dispatch_through = invoice_data.invoice_dispatch
        item_data = inventory.objects.all()
        all_dispatch_through = transporter.objects.all()
        dc_list = delivery_challan.objects.all()

        invoice_item_data = performa_invoice_items.objects.filter(invoice_id = id)
        len_invoice_item = len(invoice_item_data)
        context ={
            'invoice_data':invoice_data, 
            'all_customer_name' : all_customer_name,
            'all_dispatch_through' : all_dispatch_through,
            'len_invoice_item':len_invoice_item,
            'item_data': item_data,
            'invoice_item_data':invoice_item_data,
            'customer_name':customer_name,
            'dispatch_through':dispatch_through,
            'godown_name': godown_name,
            'dc_list': dc_list
            }
        return render(request, template_path.performa_edit_invoice, context)

    elif request.method == "POST":
        print(request.POST)
        invoice_data = get_object_or_404(Performa_Invoice, id=id)
        id = invoice_data.id
        invoice_date_str = request.POST.get('invoice_date')
        invoice_due_date_str = request.POST.get('due_date')
        invoice_buyer_order_date_str = request.POST.get('buyer_order_date')
        customer_id = request.POST['customer_id']
        if customer_id:
            q_customer_name = delivery_challan.objects.get(id=customer_id)
        else:
            q_customer_name = None

        if request.POST.get('note'):
            note = request.POST['note']
        else:
            note = invoice_data.invoice_note

        invoice_due_date_date = datetime.strptime(invoice_due_date_str, '%d-%m-%Y').date() if invoice_due_date_str else date.today()
        invoice_buyerorder_date = datetime.strptime(invoice_buyer_order_date_str, '%d-%m-%Y').date() if invoice_buyer_order_date_str else date.today()
        invoice_date = datetime.strptime(invoice_date_str, '%d-%m-%Y').date() if invoice_date_str else date.today()
        # Optional: Check if customer_id exists
        customer_id_customer = request.POST.get('customer_id_select', None)

        if customer_id_customer:
            inv_customer_name = customer.objects.filter(id=customer_id_customer).first()
        else:
            inv_customer_name = None
        
        invoice_data = {
            'custom_id': invoice_data.custom_id,
            'id': id,
            'invoice_date': invoice_date,
            'pi_number':request.POST['invoice_no'],
            'invoice_payment_terms':request.POST['payment_term'],
            'invoice_customer_name':q_customer_name,
            'invoice_customer':inv_customer_name,

            'invoice_eway_bill_no':request.POST['ewaybill_no'],
            'invoice_supply_place':request.POST['place_of_supply'],
            'invoice_delivery_no':request.POST['order_no'],
            'invoice_destination':request.POST['destination'],
            'invoice_due_date': invoice_due_date_date,
            'invoice_landing_LR_RR_No':request.POST['lrno'],
            'invoice_dispatch':request.POST['transporter_name'],
            'invoice_shipping_address':request.POST['shipping_address'],
            'invoice_sales_person':request.POST['sales_person'],
            # 'invoice_format_type':request.POST['invoice_format'],
            'invoice_vehicle_no':request.POST['vehicle_no'],
            'invoice_gst_no':request.POST['gst_no'],
            # 'invoice_term_of_delivery':request.POST['invoice_format'],
            'invoice_buyer_order_no':request.POST['buyer_order_no'],
            'invoice_buyer_order_date':invoice_buyerorder_date,
            # ' invoice_packing':request.POST['packing'],
            'invoice_dispatch':transporter.objects.filter(id=request.POST['transporter_name']).first(),
            # 'invoice_freight':request.POST['freight'],
            'invoice_sub_total':request.POST['subtotal'],
            # 'invoice_cgstper':request.POST['cgstper'],
            'invoice_cgstval':request.POST['cgst'],
            # 'invoice_sgstper':request.POST['sgstper'],
            'invoice_sgstval':request.POST['sgst'],
            # 'invoice_igstper':request.POST['igstper'],
            'invoice_igstval':request.POST['igst'],
            'invoice_adjustment':request.POST['adjustment'],
            'invoice_sale_of_good':request.POST['sale_of_good'],
            # 'invoice_bank_name':request.POST['bank_name'],
            'invoice_note':note,
            'invoice_total':request.POST['totalamt'],
             'gst_option':request.POST['gst_option'],
            # 'invoice_ser_type':request.POST['invoice_ser_type'].capitalize()
              'cn_packaging_forwording_amount': request.POST.get('packaging_forwording_amount', '0'),
            'cn_packaging_forwording_percentage': request.POST.get('packaging_forwording_percentage', '0'),
            'cn_freight_amount': request.POST.get('freight_amount', '0'),
            'cn_freight_percentage': request.POST.get('freight_percentage', '0'),
            'cn_packaging_forwording_percentage_amt': request.POST.get('packaging_forwording_percentage_amt', '0'),
            'cn_freight_percentage_amt': request.POST.get('freight_percentage_amt', '0'),
            'cn_total_amt_word':request.POST['totalamt_word'],
            'cn_packaging_forwording_amt_amt': request.POST.get('packaging_forwording_amt_amt', '0'),
            'cn_freight_percentage_amt_amt': request.POST.get('freight_amt_amt', '0'),
            # 'inv_Dispatch_document_no': request.POST['inv_Dispatch_document_no'],

        }
        Invoice_object = Performa_Invoice(**invoice_data)
        Invoice_object.save()
        i = 1
        max_row = int(request.POST.get('iid[]',0))
        # print(max_row)
        performa_invoice_items.objects.filter(invoice_id = id).delete()
        # while i <= max_row:
        for i in range(1, max_row + 1 ):
            dc_item_code = request.POST.get(f'itemcode_{i}')

            # Only proceed if dc_item_code is not null or empty
            if dc_item_code:
                current_date = datetime.now().date()  # Get current date
                invoice_item = performa_invoice_items(
                    invoice_item_code = request.POST.get(f'itemcode_{i}'),
                    invoice_description_goods = request.POST.get(f'item_{i}'),
                    invoice_hsn = request.POST.get(f'hsn_{i}'),
                    invoice_qantity = request.POST.get(f'qty_{i}'),
                    invoice_uom = request.POST.get(f'uom_{i}'),
                    invoice_unit_price = request.POST.get(f'rate_{i}'),
                    invoice_discount = request.POST.get(f'discount_{i}'),
                    invoice_tax_rate = request.POST.get(f'taxrate_{i}'),
                    invoice_tax_amount = request.POST.get(f'taxamt_{i}'),
                    invoice_total = request.POST.get(f'total_{i}'),
                    invoice_id = id,
                    date = current_date
                    )
                invoice_item.save()
                i = i+1

        messages.success(request, 'Proforma Invoice Updated Successfully.')

        return redirect('performa_invoice_list')


@login_required
def delete_per_invoice_data(request, id):
    # Get the customer instance based on the provided ID
    invoice_instance = get_object_or_404(Performa_Invoice, id=id)    
    invoice_item_instance = performa_invoice_items.objects.filter(invoice_id = id)
    invoice_instance.delete()
    invoice_item_instance.delete()
    messages.error(request, 'Proforma Invoice Deleted.')

    return redirect('performa_invoice_list')



@login_required
def performa_invoice_show_pdf(request, id):
    invo = get_object_or_404(Performa_Invoice, id=id)
  
    items = performa_invoice_items.objects.filter(invoice_id = id)
    if invo.invoice_customer_name:
        customer_data = invo.invoice_customer_name
        customer_fields = customer_data.dc_customer_name
    else:
        customer_data = invo.invoice_customer
        customer_fields = customer_data

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
        freight_amount = float(invo.cn_freight_amount)
    except (ValueError, TypeError):
        freight_amount = 0.0
    

    i_total_amount = total_amount + freight_amount
   
    context = {
        'invo': invo,
        'items': items,
        'total_amount_in_words': total_amount_in_words,
        'total_amount': total_amount,
        'total_quantity': total_quantity,
        'customer_email': customer_fields.cust_email,
        'customer_contact': customer_fields.contact_number,
        'customer_pincode': customer_fields.pincode,
        'customer_gst': customer_fields.gst_number,
        'bill_street': customer_fields.street,
        'bill_city': customer_fields.city,
        'bill_com_state': customer_fields.com_state,
        'bill_pincode': customer_fields.pincode,
        'bill_gst_uin': customer_fields.gst_uin,
        'bill_contact_number': customer_fields.contact_number,
        'shipping_1_street': customer_fields.shipping_1_street,
        'shipping_1_city': customer_fields.shipping_1_city,
        'shipping_1_state': customer_fields.shipping_1_state,
        'shipping_1_pincode': customer_fields.shipping_1_pincode,
        'shipping_1_gst_uin': customer_fields.shipping_1_gst_uin,
        'shipping_1_contact_number': customer_fields.shipping_1_contact_number,
        'company_name': customer_fields.company_name,
        'total_amount_in_words': total_amount_in_words,
        'bank_name': customer_fields.bank_name,
        'account_number': customer_fields.account_number,
        'branch_name': customer_fields.branch_name,
        'ifsc_code': customer_fields.ifsc_code,
        'tax_inv_id': tax_inv_id,
        'hsn_totals': dict(hsn_totals),
        'hsn_tax_details': hsn_tax_details,
        'i_total_amount': i_total_amount,
        'count_page': list(range(1, count_page + 1)),
        'item_list': combined_chunks,
    }


    return render(request, template_path.performa_invoice_pdf,context)


def download__performa_invoice_show_pdf(request, id):
    invo = get_object_or_404(Performa_Invoice, id=id)
    items = performa_invoice_items.objects.filter(invoice_id = id)
    if invo.invoice_customer_name:
        customer_data = invo.invoice_customer_name
        customer_fields = customer_data.dc_customer_name
    else:
        customer_data = invo.invoice_customer
        customer_fields = customer_data

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
        freight_amount = float(invo.cn_freight_amount)
    except (ValueError, TypeError):
        freight_amount = 0.0

    i_total_amount = total_amount + freight_amount

    template = get_template('purchase/performa_invoice/pdf.html')


    context = {
        'invo': invo,
        'items': items,
        'total_amount_in_words': total_amount_in_words,
        'total_amount': total_amount,
        'total_quantity': total_quantity,
        'customer_email': customer_fields.cust_email,
        'customer_contact': customer_fields.contact_number,
        'customer_pincode': customer_fields.pincode,
        'customer_gst': customer_fields.gst_number,
        'bill_street': customer_fields.street,
        'bill_city': customer_fields.city,
        'bill_com_state': customer_fields.com_state,
        'bill_pincode': customer_fields.pincode,
        'bill_gst_uin': customer_fields.gst_uin,
        'bill_contact_number': customer_fields.contact_number,
        'shipping_1_street': customer_fields.shipping_1_street,
        'shipping_1_city': customer_fields.shipping_1_city,
        'shipping_1_state': customer_fields.shipping_1_state,
        'shipping_1_pincode': customer_fields.shipping_1_pincode,
        'shipping_1_gst_uin': customer_fields.shipping_1_gst_uin,
        'shipping_1_contact_number': customer_fields.shipping_1_contact_number,
        'company_name': customer_fields.company_name,
        'total_amount_in_words': total_amount_in_words,
        'bank_name': customer_fields.bank_name,
        'account_number': customer_fields.account_number,
        'branch_name': customer_fields.branch_name,
        'ifsc_code': customer_fields.ifsc_code,
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
    response['Content-Disposition'] = 'attachment; filename="ProformaInvoice.pdf"'

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
    

@login_required
def autocomplete_invoice_name(request):
    term = request.GET.get('term', '')
    customers = customer.objects.filter(customer__icontains=term)
    results = [{'id': customer.id, 'label': customer.customer, 'value': customer.customer} for customer in customers]
    return JsonResponse(results, safe=False)

@require_POST
@login_required
def get_customer_details(request):
    try:
        customer_id = int(request.POST.get('customer_id'))
    except (TypeError, ValueError):
        return HttpResponseBadRequest("Invalid customer_id")
    Customer = get_object_or_404(customer, id=customer_id)
    response_data = {
        'billing_attention': Customer.attention,
        'billing_street': Customer.street,
        'billing_city': Customer.city,
        'billing_state': Customer.com_state,
        'billing_pincode': Customer.pincode,
        'gst_no': Customer.gst_number,
        'bank_name':Customer.bank_name,
        'shipping_addresses': [
            {
                'attention': Customer.shipping_1_attention,
                'street': Customer.shipping_1_street,
                'city': Customer.shipping_1_city,
                'state': Customer.shipping_1_state,
                'pincode': Customer.shipping_1_pincode,
            },
            {
                'attention': Customer.shipping_2_attention,
                'street': Customer.shipping_2_street,
                'city': Customer.shipping_2_city,
                'state': Customer.shipping_2_state,
                'pincode': Customer.shipping_2_pincode,
            },
            {
                'attention': Customer.shipping_3_attention,
                'street': Customer.shipping_3_street,
                'city': Customer.shipping_3_city,
                'state': Customer.shipping_3_state,
                'pincode': Customer.shipping_3_pincode,
            },
            {
                'attention': Customer.shipping_4_attention,
                'street': Customer.shipping_4_street,
                'city': Customer.shipping_4_city,
                'state': Customer.shipping_4_state,
                'pincode': Customer.shipping_4_pincode,
            },
        ],
    }
    return JsonResponse(response_data)

@login_required
def update_Instatus_view(request, id):
    if request.method == 'POST':
        invoice_data = get_object_or_404(Performa_Invoice, id=id)  # Get the Sales Order instance
        update_status = request.POST.get('invoice_status', None)  # Update the status based on the submitted form data
        if update_status:
            invoice_data.invoice_status = update_status
            invoice_data.save()
    return redirect('invoice_list')

@login_required
def download_csv_invoice(request):
   if request.method == 'POST':
        startDate = request.POST['startDate']
        endDate = request.POST['endDate']
        if startDate and endDate:
            invoice_lists = Performa_Invoice.objects.filter(invoice_date__gte=startDate, invoice_date__lte=endDate)
        else:
            invoice_lists = Performa_Invoice.objects.filter()
        data_list = []
        headers_list = ["Date","Invoice Number","Delivery Challan no","Customer Name","Due Date","Amount","Due Amount","Service Type","Status"]  
        
        data_list.append(headers_list)
        for invoice in invoice_lists:
                data_list.append([invoice.invoice_date,invoice.custom_id,invoice.invoice_delivery_no,invoice.invoice_customer_name.customer,invoice.invoice_due_date,invoice.invoice_sub_total,invoice.invoice_total, invoice.invoice_status])
        response = HttpResponse(content_type='application/csv')
        response['Content-Disposition'] = 'attachment; filename="invoice.csv"'
        writer = csv.writer(response)
        writer.writerows(data_list)
        return response
    
def autocomplete_customer_name(request):
    term = request.GET.get('term', '')
    customers = customer.objects.filter(customer__icontains=term)
    results = [{'id': customer, 'label': customer.customer} for customer in customers]
    return JsonResponse(results, safe=False)


def get_customer_details(request):
    try:
        customer_id = int(request.POST.get('customer_id'))
    except (TypeError, ValueError):
        return HttpResponseBadRequest("Invalid customer_id")
    Customer = get_object_or_404(customer, id=customer_id)
    response_data = {
        'billing_attention': Customer.attention,
        'billing_street': Customer.street,
        'billing_city': Customer.city,
        'billing_state': Customer.com_state,
        'billing_pincode': Customer.pincode,
        'gst_no': Customer.gst_number,
        'bank_name':Customer.bank_name,
        'shipping_addresses': [
            {
                'attention': Customer.shipping_1_attention,
                'street': Customer.shipping_1_street,
                'city': Customer.shipping_1_city,
                'state': Customer.shipping_1_state,
                'pincode': Customer.shipping_1_pincode,
            },
            {
                'attention': Customer.shipping_2_attention,
                'street': Customer.shipping_2_street,
                'city': Customer.shipping_2_city,
                'state': Customer.shipping_2_state,
                'pincode': Customer.shipping_2_pincode,
            },
            {
                'attention': Customer.shipping_3_attention,
                'street': Customer.shipping_3_street,
                'city': Customer.shipping_3_city,
                'state': Customer.shipping_3_state,
                'pincode': Customer.shipping_3_pincode,
            },
            {
                'attention': Customer.shipping_4_attention,
                'street': Customer.shipping_4_street,
                'city': Customer.shipping_4_city,
                'state': Customer.shipping_4_state,
                'pincode': Customer.shipping_4_pincode,
            },
        ],
    }
    return JsonResponse(response_data)


def update_Instatus_view(request, id):
    if request.method == 'POST':
        invoice_data = get_object_or_404(Performa_Invoice, id=id)  # Get the Sales Order instance
        update_status = request.POST.get('invoice_status', None)  # Update the status based on the submitted form data
        if update_status:
            invoice_data.invoice_status = update_status
            invoice_data.save()
    return redirect('invoice_list')

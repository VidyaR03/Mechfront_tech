import base64
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db.models import Q
from datetime import datetime

import inflect
from core.modules import template_path
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect,HttpResponse
from core.models import Credit_Notes, credit_notes_items, customer, transporter, inventory,godown,Debit_Notes,debit_notes_items
from core.modules.login.login import login_required
from django.contrib import messages


@login_required
def debit_notes_list_view(request):
    credit_note_list = Debit_Notes.objects.all().order_by('-id')
    context = {
        'credit_note_list':credit_note_list
        }
    return render(request,template_path.debit_notes_list,context)



@login_required
def add_debit_notes_data(request):
    if request.method == "GET":
        customer_name = customer.objects.all()
        dispatch_through = transporter.objects.all()
        godown_list  = godown.objects.all()
        item_data = inventory.objects.all()
        current_date = datetime.today().strftime('%d-%m-%Y')

        context ={ 
            'customer_name' : customer_name,
            'dispatch_through' : dispatch_through,
            'item_data': item_data,
            'godown_list':godown_list,
            'current_date':current_date
            }

        return render(request, template_path.add_debit_notes, context)
    elif request.method == "POST":
        cn_date_str = request.POST['credit_note_date']
        cn_dispatch_date_str = request.POST['dispatch_date']
        cn_buyer_order_str = request.POST['buyer_date']
        cn_buyer_order_date = datetime.strptime(cn_buyer_order_str, '%d-%m-%Y').date()
        cn_date = datetime.strptime(cn_date_str, '%d-%m-%Y').date()
        cn_dispatch_date = datetime.strptime(cn_dispatch_date_str, '%d-%m-%Y').date()
        credit_notes = {
            'cn_date':cn_date,
            'cn_invoice_no':request.POST['invoice_no'],
            'cn_customer_name':customer.objects.filter(id=request.POST['customer_id']).first(),
            'cn_supply_place':request.POST['place_of_supply'],
            'cn_destination_supply':request.POST['destination_of_supply'],
            # 'cn_delivery_type':request.POST['delivery_type'],
            'cn_buyer_order_no':request.POST['buyer_order_no'],
            'cn_buyer_order_date':cn_buyer_order_date,
            'cn_dispatch':transporter.objects.filter(id=request.POST['transporter_name']).first(),
            'cn_dispatch_date':cn_dispatch_date,
            'cn_delivery_term':request.POST['delivery_term'],
            'cn_landing_LR_RR_No':request.POST['lrno'],
            'cn_shipping_address':request.POST['shipping_address'],
            # 'cn_freight':request.POST['freight'],
            'cn_sub_total':request.POST['subtotal'],
            # 'cn_cgstper':request.POST['cgstper'],
            'cn_cgstval':request.POST['cgst'],
            # 'cn_sgstper':request.POST['sgstper'],
            'cn_sgstval':request.POST['sgst'],
            # 'cn_igstper':request.POST['igstper'],
            'cn_igstval':request.POST['igst'],
            'cn_adjustment':request.POST['adjustment'],
            # 'cn_sale_of_good':request.POST['sale_of_good'],
            'cn_note':request.POST['note'],
            'cn_total':request.POST['totalamt'],
            # 'cn_ser_type':request.POST['cn_ser_type'].capitalize(),
            'gst_option':request.POST['gst_option'],
            'cn_packaging_forwording_amount': request.POST.get('packaging_forwording_amount', '0'),
            'cn_packaging_forwording_percentage': request.POST.get('packaging_forwording_percentage', '0'),
            'cn_freight_amount': request.POST.get('freight_amount', '0'),
            'cn_freight_percentage': request.POST.get('freight_percentage', '0'),
            'cn_packaging_forwording_percentage_amt': request.POST.get('packaging_forwording_percentage_amt', '0'),
            'cn_freight_percentage_amt': request.POST.get('freight_percentage_amt', '0'),
            'cn_total_amt_word':request.POST['totalamt_word'],
            'cn_packaging_forwording_amt_amt': request.POST.get('packaging_forwording_amt_amt', '0'),
            'cn_freight_amt_amt': request.POST.get('freight_amt_amt', '0'),


        }
        credit_notes_object = Debit_Notes(**credit_notes)
        credit_notes_object.save()
        latest_credit_notes_id = Debit_Notes.objects.latest('id')
        i = 0
        max_row = int(request.POST.get('iid[]',0))
        while i <= max_row:
            cn_item = debit_notes_items(
                cn_item_code = request.POST.get(f'itemcode_{i}'),
                cn_description_goods = request.POST.get(f'item_{i}'),
                cn_hsn = request.POST.get(f'hsn_{i}'),
                cn_godown = request.POST.get(f'godown_{i}'),
                cn_qantity = request.POST.get(f'qty_{i}'),
                cn_uom = request.POST.get(f'uom_{i}'),
                cn_unit_price = request.POST.get(f'rate_{i}'),
                cn_discount = request.POST.get(f'discount_{i}'),
                cn_tax_rate = request.POST.get(f'taxrate_{i}'),
                cn_tax_amount = request.POST.get(f'taxamt_{i}'),
                cn_total = request.POST.get(f'total_{i}'),
                credit_notes_id = latest_credit_notes_id.id
            )
            cn_item.save()
            i = i+1
        messages.success(request, 'Debit Note Created Successfully.')

        return redirect('debitnotes_list')
    

@login_required
def edit_debit_notes_data(request, id):
    if request.method == "GET":
        creditnotes_data = get_object_or_404(Debit_Notes, id=id)
        all_customer_name = customer.objects.all()
        godown_list  = godown.objects.all()

        all_dispatch_through = transporter.objects.all()
        credit_notes_items_data = debit_notes_items.objects.filter(credit_notes_id = id)
        item_data = inventory.objects.all()
        context ={ 
            'credit_notes_items_data':credit_notes_items_data,
            'len_credit_notes_items': len(credit_notes_items_data),
            'creditnotes_data':creditnotes_data,
            'all_customer_name' : all_customer_name,
            'all_dispatch_through' : all_dispatch_through,
            'item_data': item_data,
            'godown_list':godown_list
            }

        return render(request, template_path.edit_debit_notes, context)
    elif request.method == "POST":
        creditnotes_data = get_object_or_404(Debit_Notes, id=id)
        id = creditnotes_data.id
        cn_date_str = request.POST['credit_note_date']
        cn_dispatch_date_str = request.POST['dispatch_date']
        cn_buyer_order_str = request.POST['buyer_date']
        cn_buyer_order_date = datetime.strptime(cn_buyer_order_str, '%d-%m-%Y').date()
        cn_date = datetime.strptime(cn_date_str, '%d-%m-%Y').date()
        cn_dispatch_date = datetime.strptime(cn_dispatch_date_str, '%d-%m-%Y').date()
        credit_notes = {
            'id': id,
            'cn_date':cn_date,
            'cn_invoice_no':request.POST['invoice_no'],
            'cn_customer_name':customer.objects.filter(id=request.POST['customer_id']).first(),
            'cn_supply_place':request.POST['place_of_supply'],
            'cn_destination_supply':request.POST['destination_of_supply'],
            # 'cn_delivery_type':request.POST['delivery_type'],
            'cn_buyer_order_no':request.POST['buyer_order_no'],
            'cn_buyer_order_date':cn_buyer_order_date,
            'cn_dispatch':transporter.objects.filter(id=request.POST['cn_dispatch']).first(),
            'cn_dispatch_date':cn_dispatch_date,
            'cn_delivery_term':request.POST['delivery_term'],
            'cn_landing_LR_RR_No':request.POST['lrno'],
            'cn_shipping_address':request.POST['cn_shipping_address'],
            # 'cn_freight':request.POST['freight'],
            'cn_sub_total':request.POST['subtotal'],
            # 'cn_cgstper':request.POST['cgstper'],
            'cn_cgstval':request.POST['cgst'],
            # 'cn_sgstper':request.POST['sgstper'],
            'cn_sgstval':request.POST['sgst'],
            # 'cn_igstper':request.POST['igstper'],
            'cn_igstval':request.POST['igst'],
            'cn_adjustment':request.POST['adjustment'],
            # 'cn_sale_of_good':request.POST['sale_of_good'],
            'cn_note':request.POST['note'],
            'cn_total':request.POST['totalamt'],
            # 'cn_ser_type':request.POST['cn_ser_type'].capitalize(),
            'gst_option':request.POST['gst_option'],
            'cn_packaging_forwording_amount': request.POST.get('packaging_forwording_amount', '0'),
            'cn_packaging_forwording_percentage': request.POST.get('packaging_forwording_percentage', '0'),
            'cn_freight_amount': request.POST.get('freight_amount', '0'),
            'cn_freight_percentage': request.POST.get('freight_percentage', '0'),
            'cn_packaging_forwording_percentage_amt': request.POST.get('packaging_forwording_percentage_amt', '0'),
            'cn_freight_percentage_amt': request.POST.get('freight_percentage_amt', '0'),
            'cn_total_amt_word':request.POST['totalamt_word'],
            'cn_packaging_forwording_amt_amt': request.POST.get('packaging_forwording_amt_amt', '0'),
            'cn_freight_amt_amt': request.POST.get('freight_amt_amt', '0'),



        }
        credit_notes_object = Debit_Notes(**credit_notes)
        credit_notes_object.save()
        # latest_credit_notes_id = Credit_Notes.objects.latest('id')
        i = 1
        max_row = int(request.POST.get('iid[]',0))
        debit_notes_items.objects.filter(credit_notes_id = id).delete()
        for i in range(1, max_row + 1):
            cn_item_code = request.POST.get(f'itemcode_{i}')
            if cn_item_code: 
                cn_item = debit_notes_items(
                    cn_item_code = request.POST.get(f'itemcode_{i}'),
                    cn_description_goods = request.POST.get(f'item_{i}'),
                    cn_hsn = request.POST.get(f'hsn_{i}'),
                    cn_godown = request.POST.get(f'godown_{i}'),
                    cn_qantity = request.POST.get(f'qty_{i}'),
                    cn_uom = request.POST.get(f'uom_{i}'),
                    cn_unit_price = request.POST.get(f'rate_{i}'),
                    cn_discount = request.POST.get(f'discount_{i}'),
                    cn_tax_rate = request.POST.get(f'taxrate_{i}'),
                    cn_tax_amount = request.POST.get(f'taxamt_{i}'),
                    cn_total = request.POST.get(f'total_{i}'),
                    credit_notes_id = id
            )
            cn_item.save()
            i = i+1
        messages.success(request, 'Debit Note Updated Successfully.')

        return redirect('debitnotes_list')
    


# def credit_show_pdf(request, id):
#     credit = get_object_or_404(Credit_Notes, id=id)

#     credit_item_data = debit_notes_items.objects.filter(credit_notes_id = id)

#     context = {
#         'credit':credit,
#         'credit_item_data':credit_item_data
#         }
#     return render(request, template_path.credit_note_pdf,context)


@login_required
def delete_debit_data(request, id):
    # Get the customer instance based on the provided ID
    credit_instance = get_object_or_404(Debit_Notes, id=id)    
    credit_item_instance = debit_notes_items.objects.filter(credit_notes_id = id)
    credit_instance.delete()
    credit_item_instance.delete()
    messages.error(request, 'Debit Note Deleted.')

    return redirect('debitnotes_list')
# primes = [num for num in s if num > 1 and all(num % i != 0 for i in range(2, int(num**0.5) + 1))]

# primes = [num for num in s if num > 1 and all(num % i != 0 for i in range(2, num))]

from django.template.loader import get_template
from weasyprint import HTML, CSS

# def generate_debit_note_pdf(request, id):
#     credit = get_object_or_404(Credit_Notes, id=id)

#     credit_item_data = credit_notes_items.objects.filter(credit_notes_id = id)

#     context = {
#         'credit':credit,
#         'credit_item_data':credit_item_data
#     }

#     template_path = "sales/credit_notes/credit_note_pdf_dow.html"
#     template = get_template(template_path)
   
#     html = template.render(context)

   
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = f'attachment; filename="debit_note.pdf"'

#     HTML(string=html).write_pdf(response, stylesheets=[CSS(string='@page { size: A2; margin: 1cm; }')])

#     return response


@login_required
def download_debit_note_pdf(request, id):
   
    credit = get_object_or_404(Debit_Notes, id=id)
    credit_item_data = debit_notes_items.objects.filter(credit_notes_id = id)
    chunk_size = 10
    for index, item in enumerate(credit_item_data, start=1):
        item.sr_no = index
    combined_chunks = [credit_item_data[i:i + chunk_size] for i in range(0, len(credit_item_data), chunk_size)]
    if combined_chunks and len(combined_chunks[-1]) < chunk_size:
        combined_chunks[-1].extend([None] * (chunk_size - len(combined_chunks[-1])))
    list_n = []
    count_page = int(len(credit_item_data) / chunk_size)
    if (len(credit_item_data) % chunk_size) != 0:
        count_page += 1

    
    p = inflect.engine()
    total_amount_in_words = p.number_to_words(credit.cn_total).title().replace(",", "")

    total_amount = sum(float(item.cn_total) for item in credit_item_data)
    template = get_template('sales/debit_notes/pdf.html')
    context = {
        'count_page': list(range(1, count_page + 1)),
        'credit': credit,
        'credit_item_data_': credit_item_data,
        'credit_item_data': combined_chunks,
        'total_amount': total_amount,
        'total_amount_in_words': total_amount_in_words,
        'chunk_size': chunk_size,
    }
    
    html_string = template.render(context)
    base_url = request.build_absolute_uri('/')
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Debit_note.pdf"'

    try:
        # pdf_file = HTML(string=html_string, base_url=base_url).write_pdf()
        # pdf_base64 = base64.b64encode(pdf_file).decode('utf-8')
        # pdf_data_uri = f'data:application/pdf;base64,{pdf_base64}'
        # return render(request, 'sales/credit_notes/pre.html', {'pdf_data_uri': pdf_data_uri})
        HTML(string=html_string, base_url=base_url).write_pdf(response)
        return response

    except Exception as e:
        return HttpResponse(f'Error generating PDF: {str(e)}')
    


# def download_quotation_pdf(request, id):
#     credit = get_object_or_404(Debit_Notes, id=id)

#     credit_item_data = debit_notes_items.objects.filter(credit_notes_id = id)

    
#     template = get_template('sales/debit_notes/debit_note_pdf_download.html')
#     context = {
#         'credit':credit,
#         'credit_item_data':credit_item_data
#     }

#     html_string = template.render(context)

#     # Ensure static files are correctly referenced
#     base_url = request.build_absolute_uri('/')

#     # Create an HTTP response with the PDF content type
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = 'attachment; filename="Debit_Note.pdf"'

#     try:
#         # Generate PDF using WeasyPrint with correct base_url
#         HTML(string=html_string, base_url=base_url).write_pdf(response)
#         return response

#         # pdf_file = HTML(string=html_string, base_url=base_url).write_pdf()
#         # # Encode PDF to base64
#         # pdf_base64 = base64.b64encode(pdf_file).decode('utf-8')
#         # # Render HTML page with PDF preview
#         # return render(request, 'sales/quotation/pdf_preview.html', {'pdf_base64': pdf_base64})

#     except Exception as e:
#         return HttpResponse(f'Error generating PDF: {str(e)}')



@login_required
def debit_show_pdf(request, id):
    credit = get_object_or_404(Debit_Notes, id=id)
    credit_item_data = debit_notes_items.objects.filter(credit_notes_id = id)
    chunk_size = 10
    for index, item in enumerate(credit_item_data, start=1):
        item.sr_no = index
    combined_chunks = [credit_item_data[i:i + chunk_size] for i in range(0, len(credit_item_data), chunk_size)]
    if combined_chunks and len(combined_chunks[-1]) < chunk_size:
        combined_chunks[-1].extend([None] * (chunk_size - len(combined_chunks[-1])))
    list_n = []
    count_page = int(len(credit_item_data) / chunk_size)
    if (len(credit_item_data) % chunk_size) != 0:
        count_page += 1

    
    p = inflect.engine()
    total_amount_in_words = p.number_to_words(credit.cn_total).title().replace(",", "")

    total_amount = sum(float(item.cn_total) for item in credit_item_data)
    template = get_template('sales/debit_notes/pdf.html')
    context = {
        'count_page': list(range(1, count_page + 1)),
        'credit': credit,
        'credit_item_data_': credit_item_data,
        'credit_item_data': combined_chunks,
        'total_amount': total_amount,
        'total_amount_in_words': total_amount_in_words,
        'chunk_size': chunk_size,
    }
    return render(request, template_path.debit_note_pdf,context)

 
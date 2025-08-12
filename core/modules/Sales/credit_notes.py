import base64
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db.models import Q
from datetime import datetime
from core.modules import template_path
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect,HttpResponse
from core.models import Credit_Notes, credit_notes_items, customer, transporter, inventory,godown

from collections import defaultdict

from core.modules.login.login import login_required
from django.contrib import messages


@login_required
def credit_notes_list_view(request):
    credit_note_list = Credit_Notes.objects.all().order_by('-id')
    context = {
        'credit_note_list':credit_note_list
        }
    return render(request,template_path.credits_notes_list,context)



@login_required
def add_credit_notes_data(request):
    if request.method == "GET":
        customer_name = customer.objects.all()
        godown_name = godown.objects.all()
        dispatch_through = transporter.objects.all()
        item_data = inventory.objects.all()
        context ={ 
            'customer_name' : customer_name,
            'dispatch_through' : dispatch_through,
            'item_data': item_data,
            'godown_name':godown_name
            }

        return render(request, template_path.add_credits_notes, context)
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
            'cn_customer_name':customer.objects.filter(id=request.POST['customer_Name']).first(),
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
        credit_notes_object = Credit_Notes(**credit_notes)
        credit_notes_object.save()
        latest_credit_notes_id = Credit_Notes.objects.latest('id')
        i = 0
        max_row = int(request.POST.get('iid[]',0))
        while i <= max_row:
            cn_item = credit_notes_items(
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
        messages.success(request, 'Credit Note Created Successfully.')

        return redirect('creditnotes_list')
    

@login_required
def edit_credit_notes_data(request, id):
    if request.method == "GET":
        creditnotes_data = get_object_or_404(Credit_Notes, id=id)
        all_customer_name = customer.objects.all()
        all_dispatch_through = transporter.objects.all()
        godown_name = godown.objects.all()

        credit_notes_items_data = credit_notes_items.objects.filter(credit_notes_id = id)
        item_data = inventory.objects.all()
        context ={ 
            'credit_notes_items_data':credit_notes_items_data,
            'len_credit_notes_items': len(credit_notes_items_data),
            'creditnotes_data':creditnotes_data,
            'all_customer_name' : all_customer_name,
            'all_dispatch_through' : all_dispatch_through,
            'item_data': item_data,
            'godown_name':godown_name
            }

        return render(request, template_path.edit_credits_notes, context)
    elif request.method == "POST":
        creditnotes_data = get_object_or_404(Credit_Notes, id=id)
        id = creditnotes_data.id
        cn_date_str = request.POST['credit_note_date']
        cn_dispatch_date_str = request.POST['dispatch_date']
        cn_buyer_order_str = request.POST['buyer_date']
        cn_buyer_order_date = datetime.strptime(cn_buyer_order_str, '%d-%m-%Y').date()
        cn_date = datetime.strptime(cn_date_str, '%d-%m-%Y').date()
        cn_dispatch_date = datetime.strptime(cn_dispatch_date_str, '%d-%m-%Y').date()
        credit_notes = {
            'id': id,
            'cn_date': cn_date,
            'cn_invoice_no': request.POST['invoice_no'],
            'cn_customer_name': customer.objects.filter(id=request.POST['customer_Name']).first(),
            'cn_supply_place': request.POST['place_of_supply'],
            'cn_destination_supply': request.POST['destination_of_supply'],
            'cn_buyer_order_no': request.POST['buyer_order_no'],
            'cn_buyer_order_date': cn_buyer_order_date,
            'cn_dispatch': transporter.objects.filter(id=request.POST['transporter_name']).first(),
            'cn_dispatch_date': cn_dispatch_date,
            'cn_delivery_term': request.POST['delivery_term'],
            'cn_landing_LR_RR_No': request.POST['lrno'],
            'cn_shipping_address': request.POST['shipping_address'],
            'cn_sub_total': request.POST['subtotal'],
            'cn_cgstval': request.POST['cgst'],
            'cn_sgstval': request.POST['sgst'],
            'cn_igstval': request.POST['igst'],
            'cn_adjustment': request.POST['adjustment'],
            'cn_note': request.POST['note'],
            'cn_total': request.POST['totalamt'],
            'gst_option': request.POST['gst_option'],
            'cn_packaging_forwording_amount': request.POST.get('packaging_forwording_amount', '0'),
            'cn_packaging_forwording_percentage': request.POST.get('packaging_forwording_percentage', '0'),
            'cn_freight_amount': request.POST.get('freight_amount', '0'),
            'cn_freight_percentage': request.POST.get('freight_percentage', '0'),
            'cn_packaging_forwording_percentage_amt': request.POST.get('packaging_forwording_percentage_amt', '0'),
            'cn_freight_percentage_amt': request.POST.get('freight_percentage_amt', '0'),
            'cn_total_amt_word': request.POST['totalamt_word'],
            'cn_packaging_forwording_amt_amt': request.POST.get('packaging_forwording_amt_amt', '0'),
            'cn_freight_amt_amt': request.POST.get('freight_amt_amt', '0'),
        }
        credit_notes_object = Credit_Notes(**credit_notes)
        credit_notes_object.save()

        credit_notes_items.objects.filter(credit_notes_id=id).delete()
        max_row = int(request.POST.get('iid[]', 0))
        for i in range(1, max_row + 1):
            cn_item_code = request.POST.get(f'itemcode_{i}')
            if cn_item_code:  # Ensure cn_item_code is not empty or None
                cn_item = credit_notes_items(
                    cn_item_code=cn_item_code,
                    cn_description_goods=request.POST.get(f'item_{i}'),
                    cn_hsn=request.POST.get(f'hsn_{i}'),
                    cn_godown=request.POST.get(f'godown_{i}'),
                    cn_qantity=request.POST.get(f'qty_{i}'),
                    cn_uom=request.POST.get(f'uom_{i}'),
                    cn_unit_price=request.POST.get(f'rate_{i}'),
                    cn_discount=request.POST.get(f'discount_{i}'),
                    cn_tax_rate=request.POST.get(f'taxrate_{i}'),
                    cn_tax_amount=request.POST.get(f'taxamt_{i}'),
                    cn_total=request.POST.get(f'total_{i}'),
                    credit_notes_id=id
                )
                cn_item.save()

        messages.success(request, 'Credit Note Updated Successfully.')
        return redirect('creditnotes_list')



# @login_required
# def credit_show_pdf(request, id):
#     credit = get_object_or_404(Credit_Notes, id=id)

#     credit_item_data = credit_notes_items.objects.filter(credit_notes_id = id)

#     context = {
#         'credit':credit,
#         'credit_item_data':credit_item_data
#         }
#     return render(request, template_path.credit_note_pdf,context)


@login_required
def credit_show_pdf(request, id):
    credit = get_object_or_404(Credit_Notes, id=id)
    credit_item_data = credit_notes_items.objects.filter(credit_notes_id=id)
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

    hsn_totals = defaultdict(float)
    for item in credit_item_data:
        try:
            amount = float(item.cn_total)
            hsn_totals[item.cn_hsn] += amount
        except (ValueError, TypeError):
            continue  

    hsn_tax_details = []
   
    for hsn, taxable_value in hsn_totals.items():
        try:
            # Remove '%' symbol and convert to float
            cgst_rate_str = credit.cn_cgstper.strip('%')
            cgst_rate = float(cgst_rate_str)
            cgst_amount = (taxable_value * cgst_rate) / 100
        except Exception as e:
            cgst_rate = cgst_amount = 0.0

    try:
        # Remove '%' symbol and convert to float
        sgst_rate_str = credit.cn_sgstper.strip('%')
        sgst_rate = float(sgst_rate_str)
        sgst_amount = taxable_value * (sgst_rate / 100)
    except Exception as e:
        sgst_rate = sgst_amount = 0.0

    hsn_tax_details.append({
        'hsn': hsn,
        'taxable_value': taxable_value,
        'cgst_rate': cgst_rate,
        'cgst_amount': cgst_amount,
        'sgst_rate': sgst_rate,
        'sgst_amount': sgst_amount
    })

    for detail in credit_item_data:
        if credit.gst_option == 'Interstate':
            detail.half_tax_amount = float(detail.cn_tax_amount)
            detail.half_tax_rate = float(detail.cn_tax_rate)
        else:
            detail.half_tax_amount = float(detail.cn_tax_amount) / 2
            detail.half_tax_rate = float(detail.cn_tax_rate) / 2 


    p = inflect.engine()
    total_amount_in_words = p.number_to_words(credit.cn_total).title().replace(",", "")

    total_amount = sum(float(item.cn_total) for item in credit_item_data)
    context = {
        'count_page': list(range(1, count_page + 1)),
        'credit': credit,
        'credit_item_data_': credit_item_data,
        'credit_item_data': combined_chunks,
        'total_amount': total_amount,
        'total_amount_in_words': total_amount_in_words,
        'chunk_size': chunk_size,
        'hsn_tax_details': hsn_tax_details
        }
    return render(request, template_path.credit_note_pdf,context)
    


from django.template.loader import get_template
from weasyprint import HTML, CSS
from io import BytesIO
import inflect



@login_required
def download_credit_note_pdf(request, id):
    credit = get_object_or_404(Credit_Notes, id=id)
    credit_item_data = credit_notes_items.objects.filter(credit_notes_id=id)
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

    hsn_totals = defaultdict(float)
    for item in credit_item_data:
        try:
            amount = float(item.cn_total)
            hsn_totals[item.cn_hsn] += amount
        except (ValueError, TypeError):
            continue  

    hsn_tax_details = []
   
    for hsn, taxable_value in hsn_totals.items():
        try:
            # Remove '%' symbol and convert to float
            cgst_rate_str = credit.cn_cgstper.strip('%')
            cgst_rate = float(cgst_rate_str)
            cgst_amount = (taxable_value * cgst_rate) / 100
        except Exception as e:
            cgst_rate = cgst_amount = 0.0

        try:
            # Remove '%' symbol and convert to float
            sgst_rate_str = credit.cn_sgstper.strip('%')
            sgst_rate = float(sgst_rate_str)
            sgst_amount = taxable_value * (sgst_rate / 100)
        except Exception as e:
            sgst_rate = sgst_amount = 0.0

        hsn_tax_details.append({
            'hsn': hsn,
            'taxable_value': taxable_value,
            'cgst_rate': cgst_rate,
            'cgst_amount': cgst_amount,
            'sgst_rate': sgst_rate,
            'sgst_amount': sgst_amount
        })

    
    for detail in credit_item_data:
        if credit.gst_option == 'Interstate':
            detail.half_tax_amount = float(detail.cn_tax_amount)
            detail.half_tax_rate = float(detail.cn_tax_rate)
        else:
            detail.half_tax_amount = float(detail.cn_tax_amount) / 2
            detail.half_tax_rate = float(detail.cn_tax_rate) / 2 


    p = inflect.engine()
    total_amount_in_words = p.number_to_words(credit.cn_total).title().replace(",", "")

    total_amount = sum(float(item.cn_total) for item in credit_item_data)
    template = get_template('sales/credit_notes/pdf.html')
    context = {
        'count_page': list(range(1, count_page + 1)),
        'credit': credit,
        'credit_item_data_': credit_item_data,
        'credit_item_data': combined_chunks,
        'total_amount': total_amount,
        'total_amount_in_words': total_amount_in_words,
        'chunk_size': chunk_size,
        'hsn_tax_details': hsn_tax_details
    }
    
    html_string = template.render(context)
    base_url = request.build_absolute_uri('/')
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="CreditNote.pdf"'

    try:
        # pdf_file = HTML(string=html_string, base_url=base_url).write_pdf()
        # pdf_base64 = base64.b64encode(pdf_file).decode('utf-8')
        # pdf_data_uri = f'data:application/pdf;base64,{pdf_base64}'
        # return render(request, 'sales/credit_notes/pre.html', {'pdf_data_uri': pdf_data_uri})
        HTML(string=html_string, base_url=base_url).write_pdf(response)
        return response
    except Exception as e:
        return HttpResponse(f'Error generating PDF: {str(e)}')
    



# def download_credit_note_pdf(request, id):
#     credit = get_object_or_404(Credit_Notes, id=id)
#     credit_item_data = credit_notes_items.objects.filter(credit_notes_id=id)
#     chunk_size = 10
#     for index, item in enumerate(credit_item_data, start=1):
#         item.sr_no = index
#     combined_chunks = [credit_item_data[i:i + chunk_size] for i in range(0, len(credit_item_data), chunk_size)]
#     if combined_chunks and len(combined_chunks[-1]) < chunk_size:
#         combined_chunks[-1].extend([None] * (chunk_size - len(combined_chunks[-1])))
#     list_n = []
#     count_page = int(len(credit_item_data) / chunk_size)
#     if (len(credit_item_data) % 12) != 0:
#         count_page += 1

#     p = inflect.engine()
#     total_amount_in_words = p.number_to_words(credit.cn_total)
#     total_amount_in_words = total_amount_in_words.title()
#     total_amount_in_words = total_amount_in_words.replace(",", "")


#     total_amount = sum(float(item.cn_total) for item in credit_item_data)
#     template = get_template('sales/credit_notes/pdf.html')
#     context = {
#         'count_page': list(range(1, count_page + 1)),
#         'credit': credit,
#         'credit_item_data_': credit_item_data,
#         'credit_item_data': combined_chunks,
#         'total_amount': total_amount,
#         'total_amount_in_words': total_amount_in_words,
#         'chunk_size': chunk_size
#     }
    
#     html_string = template.render(context)

#     # Ensure static files are correctly referenced
#     base_url = request.build_absolute_uri('/')

#     # Create an HTTP response with the PDF content type
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = 'attachment; filename="CreditNote.pdf"'

#     try:
#         # Generate PDF using WeasyPrint with correct base_url
#         # HTML(string=html_string, base_url=base_url).write_pdf(response)
#         # return response
#         pdf_file = HTML(string=html_string, base_url=base_url).write_pdf()
#         pdf_base64 = base64.b64encode(pdf_file).decode('utf-8')
#         return render(request, 'sales/credit_notes/pdf.html', {'pdf_base64': pdf_base64})


#     except Exception as e:
#         return HttpResponse(f'Error generating PDF: {str(e)}')


# def download_credit_note_pdf(request, id):
    
    # credit = get_object_or_404(Credit_Notes, id=id)
    # credit_item_data = credit_notes_items.objects.filter(credit_notes_id=id)

    # context = {
    #     'credit': credit,
    #     'credit_item_data': credit_item_data,
    # }

    # # Render the HTML content
    # template = get_template('sales/credit_notes/pdf.html')
    # html_content = template.render(context)

    # # Create a BytesIO buffer for the PDF
    # pdf_file = BytesIO()

    # # Generate the PDF
    # HTML(string=html_content).write_pdf(pdf_file)

    # # Set the buffer position to the start
    # pdf_file.seek(0)

    # # Create the HTTP response
    # response = HttpResponse(pdf_file, content_type='application/pdf')
    # response['Content-Disposition'] = f'attachment; filename="credit_note_{id}.pdf"'
    # base_url = request.build_absolute_uri('/')

    # pdf_file = HTML(string=html_content, base_url=base_url).write_pdf()
    # pdf_base64 = base64.b64encode(pdf_file).decode('utf-8')
    # return render(request, 'sales/credit_notes/pdf.html', {'pdf_base64': pdf_base64})

    # return response



# def download_credit_note_pdf(request, id):
#     credit = get_object_or_404(Credit_Notes, id=id)
#     credit_item_data = credit_notes_items.objects.filter(credit_notes_id=id)
    
#     context = {
#         'credit': credit,
#         'credit_item_data': credit_item_data,
#     }
    
#     template = get_template('sales/credit_notes/pdf.html')
#     html_string = template.render(context)
    
#     base_url = request.build_absolute_uri('/')
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = 'attachment; filename="CN.pdf"'
    
#     try:
#         # HTML(string=html_string, base_url=base_url).write_pdf(response)
#         # return response
#         pdf_file = HTML(string=html_string, base_url=base_url).write_pdf()
#         pdf_base64 = base64.b64encode(pdf_file).decode('utf-8')
#         return render(request, 'sales/credit_notes/pdf.html', {'pdf_base64': pdf_base64})
#     except Exception as e:
#         return HttpResponse(f'Error generating PDF: {str(e)}')


@login_required
def delete_credit_data(request, id):
    # Get the customer instance based on the provided ID
    credit_instance = get_object_or_404(Credit_Notes, id=id)    
    credit_item_instance = credit_notes_items.objects.filter(credit_notes_id = id)
    credit_instance.delete()
    credit_item_instance.delete()
    messages.error(request, 'Credit Note Deleted.')

    return redirect('creditnotes_list')
from django.shortcuts import render, redirect, get_object_or_404
from core.models import  Performa_Invoice,Debit_Notes,Credit_Notes, customer,Purchase_Invoice,invoice_items, vendor, cash_voucher,sales_order_items, Invoice, inventory, Goods_received_notes,sales_order,Purchase_Invoice_items
from core.modules import template_path
from datetime import datetime
from django.http import JsonResponse
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib import messages
from core.modules.Account.forms import DateRangeForm
import datetime
from datetime import datetime
from django.db.models import Sum
from core.modules.login.login import login_required
from django.urls import reverse
import openpyxl
from openpyxl.styles import Font
from django.utils.dateparse import parse_date
from io import BytesIO
import pandas as pd
from django.db.models import F, IntegerField

#reqired to check

@login_required
def debit_note_report(request):
    context = {
        'start_date': None,
        'end_date': None,
        'items_within_range': None,
        'filtered_items': None,
    }
 
    if request.method == 'POST':
        start_date_str = request.POST.get('start_date')
    
        end_date_str = request.POST.get('end_date')

        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        # print(start_date,'start_date--')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        # print(end_date,'end_date---')

        request.session['start_date'] = start_date_str
        request.session['end_date'] = end_date_str

        # Filter items within the date range
        items_within_range = Debit_Notes.objects.filter(cn_date__range=(start_date, end_date))
        # print("items_within_range",items_within_range)
        filtered_items = list(items_within_range.values(
        'cn_customer_name', 'cn_date', 'cn_invoice_no', 'cn_total','cn_sub_total','cn_igstval','cn_sgstval','cn_cgstval'))
        total_amount = sum(float(item.cn_total or 0) for item in items_within_range)


       
        context.update({
            'items_within_range': items_within_range,
            'filtered_items': filtered_items,
            'start_date': start_date_str,
            'end_date': end_date_str,
            'total_amount':total_amount
        })

       
        return render(request, template_path.rdebit_note, context)
   

    return render(request,template_path.debit_note_date_report,context)


@login_required
def debit_note_date(request):
    return render(request, template_path.debit_note_date_report)
 





@login_required
def credit_note_report(request):
   
    context = {
        'start_date': None,
        'end_date': None,
        'items_within_range': None,
        'filtered_items': None,
    }
 
    if request.method == 'POST':
        start_date_str = request.POST.get('start_date')
    
        end_date_str = request.POST.get('end_date')

        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        # print(start_date,'start_date--')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        # print(end_date,'end_date---')

        request.session['start_date'] = start_date_str
        request.session['end_date'] = end_date_str

        # Filter items within the date range
        items_within_range = Credit_Notes.objects.filter(cn_date__range=(start_date, end_date))
        # print("items_within_range",items_within_range)
        filtered_items = list(items_within_range.values(
        'cn_customer_name', 'cn_date', 'cn_invoice_no', 'cn_total','cn_sub_total','cn_igstval','cn_sgstval','cn_cgstval'))
        total_amount = sum(float(item.cn_total or 0) for item in items_within_range)


       
        context.update({
            'items_within_range': items_within_range,
            'filtered_items': filtered_items,
            'start_date': start_date_str,
            'end_date': end_date_str,
            'total_amount':total_amount
        })

       
        return render(request, template_path.rcredit_note, context)
   

    return render(request,template_path.credit_note_date_report,context)


@login_required
def credit_note_date(request):
    return render(request, template_path.credit_note_date_report)
 


@login_required
def download_credit_note_excel(request):
    start_date_str = request.session.get('start_date')
    end_date_str = request.session.get('end_date')

    # Validate date strings
    if not start_date_str or not end_date_str:
        return HttpResponse("Start date and end date are required.", status=400)

    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    except ValueError:
        return HttpResponse("Invalid date format. Please use YYYY-MM-DD.", status=400)

    # Retrieve data from the database based on the date range
    items_within_range = Credit_Notes.objects.filter(
        cn_date__range=(start_date, end_date)
    ).order_by('cn_date')

    # Extract specific fields for display
    filtered_items = list(items_within_range.values(
        'cn_customer_name', 'cn_date', 'cn_invoice_no',
         'cn_igstval', 'cn_sgstval', 'cn_cgstval','cn_sub_total','cn_total',
    ))

    # Calculate the total amount
    total_amount = sum(float(item['cn_total']) for item in filtered_items)

    # Create an in-memory output file for the new workbook
    output = BytesIO()
    workbook = openpyxl.Workbook()
    sheet = workbook.active

    # Add title and date range
    title = "M/S KEYMECH TECHNOLOGIES"
    subtitle = "Credit Note Summary Report"
    date_range = f"From {start_date_str} To {end_date_str}"

    sheet.merge_cells('A1:I1')
    sheet.merge_cells('A2:I2')
    sheet.merge_cells('A3:I3')

    title_cell = sheet.cell(row=1, column=1)
    subtitle_cell = sheet.cell(row=2, column=1)
    date_range_cell = sheet.cell(row=3, column=1)

    title_cell.value = title
    subtitle_cell.value = subtitle
    date_range_cell.value = date_range

    title_cell.font = Font(size=14, bold=True)
    subtitle_cell.font = Font(size=12, bold=True)
    date_range_cell.font = Font(size=10, bold=True)

    # Write headers
    headers = [ 'Date', 'Invoice No', 'IGST Value', 'SGST Value', 'CGST Value', ' Sub Total', ' Total', ]
    sheet.append([])
    sheet.append(headers)

    # Write data rows
    for item in filtered_items:
        sheet.append([
            # item['cn_customer_name'],
            item['cn_date'],
            item['cn_invoice_no'],
            item['cn_igstval'],
            item['cn_sgstval'],
            item['cn_cgstval'],
            item['cn_sub_total'],

            item['cn_total'],
        ])

    # Write total row
    sheet.append([])
    sheet.append(['', '', '', '','','','Total',total_amount])

    # Set column widths for better visibility
    column_widths = [ 15, 15, 15, 20, 15, 15, 15, 10]
    for i, column_width in enumerate(column_widths, start=1):
        sheet.column_dimensions[openpyxl.utils.get_column_letter(i)].width = column_width

    # Save the workbook to the output file
    workbook.save(output)
    output.seek(0)

    # Create the response
    response = HttpResponse(
        output,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=credit_note_summary.xlsx'
    return response




@login_required
def download_debit_note_excel(request):
    start_date_str = request.session.get('start_date')
    end_date_str = request.session.get('end_date')

    # Validate date strings
    if not start_date_str or not end_date_str:
        return HttpResponse("Start date and end date are required.", status=400)

    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    except ValueError:
        return HttpResponse("Invalid date format. Please use YYYY-MM-DD.", status=400)

    # Retrieve data from the database based on the date range
    items_within_range = Debit_Notes.objects.filter(
        cn_date__range=(start_date, end_date)
    ).order_by('cn_date')

    # Extract specific fields for display
    filtered_items = list(items_within_range.values(
        'cn_customer_name', 'cn_date', 'cn_invoice_no',
         'cn_igstval', 'cn_sgstval', 'cn_cgstval','cn_sub_total','cn_total',
    ))

    # Calculate the total amount
    total_amount = sum(float(item['cn_total']) for item in filtered_items)

    # Create an in-memory output file for the new workbook
    output = BytesIO()
    workbook = openpyxl.Workbook()
    sheet = workbook.active

    # Add title and date range
    title = "M/S KEYMECH TECHNOLOGIES"
    subtitle = "Debit Note Summary Report"
    date_range = f"From {start_date_str} To {end_date_str}"

    sheet.merge_cells('A1:I1')
    sheet.merge_cells('A2:I2')
    sheet.merge_cells('A3:I3')

    title_cell = sheet.cell(row=1, column=1)
    subtitle_cell = sheet.cell(row=2, column=1)
    date_range_cell = sheet.cell(row=3, column=1)

    title_cell.value = title
    subtitle_cell.value = subtitle
    date_range_cell.value = date_range

    title_cell.font = Font(size=14, bold=True)
    subtitle_cell.font = Font(size=12, bold=True)
    date_range_cell.font = Font(size=10, bold=True)

    # Write headers
    headers = [ 'Date', 'Invoice No', 'IGST Value', 'SGST Value', 'CGST Value', ' Sub Total', ' Total', ]
    sheet.append([])
    sheet.append(headers)

    # Write data rows
    for item in filtered_items:
        sheet.append([
            # item['cn_customer_name'],
            item['cn_date'],
            item['cn_invoice_no'],
            item['cn_igstval'],
            item['cn_sgstval'],
            item['cn_cgstval'],
            item['cn_sub_total'],

            item['cn_total'],
        ])

    # Write total row
    sheet.append([])
    sheet.append(['', '', '', '','','','Total',total_amount])

    # Set column widths for better visibility
    column_widths = [ 15, 15, 15, 20, 15, 15, 15, 10]
    for i, column_width in enumerate(column_widths, start=1):
        sheet.column_dimensions[openpyxl.utils.get_column_letter(i)].width = column_width

    # Save the workbook to the output file
    workbook.save(output)
    output.seek(0)

    # Create the response
    response = HttpResponse(
        output,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=debit_note_summary.xlsx'
    return response


@login_required
def inventory_summery(request):  
    companies = vendor.objects.values('company_name').distinct().order_by('company_name')

    return render(request, template_path.inventory_sum, {
        'company': companies,
    })


#  Sales Register
@login_required
def sales_register_date(request):

   
    return render(request, template_path.sales_register_date_report)



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@login_required
def sales_register_remark_ajax(request, id):
    if request.method == 'POST':
        record = get_object_or_404(Invoice, id=id)
        query = request.POST.get('query')
        record.inv_remark = query
        record.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'fail'}, status=400)


@login_required
def display_sales_register_date_range(request):
    if request.method == 'POST':
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')

        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()


        # Store the date range in the session
        request.session['start_date'] = start_date_str
        request.session['end_date'] = end_date_str

        # Filter items within the date range
        sales_register_within_range = Invoice.objects.filter(invoice_date__range=(start_date, end_date))
        for item in sales_register_within_range:
            print(item.inv_number)
        # Calculate totals
        total_invoice = sum(float(item.invoice_due or 0) for item in sales_register_within_range)
        total_cgst = sum(float(item.invoice_cgstval or 0) for item in sales_register_within_range)
        total_sgst = sum(float(item.invoice_sgstval or 0) for item in sales_register_within_range)
        total_igst = sum(float(item.invoice_igstval or 0) for item in sales_register_within_range)
        total_amount = sum(float(item.invoice_total or 0) for item in sales_register_within_range)

        context = {
            'sales_register_within_range': sales_register_within_range,
            'total_cgst': total_cgst,
            'total_sgst': total_sgst,
            'total_igst': total_igst,
            'total_amount': total_amount,
            'start_date': start_date_str,
            'end_date': end_date_str,
            'total_invoice':total_invoice
        }
        return render(request, template_path.sales_register_list_report, context)
    
    return render(request, template_path.sales_register_date_report, {})





@login_required
def purchase_register_date(request):
   
    return render(request, template_path.purchase_register_date_report)



@login_required
def customer_outstanding(request):
    cust = customer.objects.all()
    context = {
        'cust': cust,
    }
    return render(request, template_path.cust_out, context)


from django.db.models import Sum, F, ExpressionWrapper, DurationField, Func
from django.utils import timezone


class Abs(Func):
    function = 'ABS'
    template = '%(function)s(%(expressions)s)'


@login_required
def customer_oustanding_date(request):
    if request.method == 'POST':
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')

        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

        # Filter items within the date range
        items_within_range = Performa_Invoice.objects.filter(invoice_date__range=(start_date, end_date))
        for i in items_within_range:
            print(i.pi_number,'inv_number---')
        # print(items_within_range,'items_within_range---')

        # Calculate Due Days
       # Calculate Due Days as absolute value
        current_date = timezone.now().date()
        items_within_range = items_within_range.annotate(
            due_days=ExpressionWrapper(Abs(current_date - F('invoice_due_date')), output_field=DurationField())
        )

        

        # Calculate totals
        total_invoice_amount = items_within_range.aggregate(Sum('invoice_total'))['invoice_total__sum'] or 0
        total_due_amount = items_within_range.aggregate(Sum('invoice_due'))['invoice_due__sum'] or 0

        context = {
            'sales_register_within_range': items_within_range,
            'total_invoice_amount': total_invoice_amount,
            'total_due_amount': total_due_amount,
        }

        return render(request, template_path.cust_out_date, context)

    return render(request, template_path.cust_out_date)









@login_required
def vendor_outstanding(request):
    vendor_out = vendor.objects.all()
    total_amount = sum(float(t.receive_amount) for t in vendor_out)

    context = {
        'vendor_out': vendor_out,
        'total_amount': total_amount
    }
    
    if request.method == "POST":
        # print(request.POST)
        customer_nm = request.POST['vendor_id']
        from_date_str = request.POST['from_date']
        to_date_str = request.POST['to_date']
        from_date = datetime.strptime(from_date_str, '%d-%m-%Y').date()
        to_date = datetime.strptime(to_date_str, '%d-%m-%Y').date()
        
        if customer_nm != 'all':
            invoices = Purchase_Invoice.objects.filter(
                Q(purchase_invoice_vendor_name=customer_nm) &
                Q(purchase_invoice_date__range=[from_date, to_date])
            )
        else:
            invoices = Purchase_Invoice.objects.filter(
                Q(purchase_invoice_date__range=[from_date, to_date])
            )
        
        ven_entries = []
        for invoice in invoices:
            due_amt = 0
            # # item = payment_in.objects.filter(invoicenumber=invoice.id).first()
            # customer_detail = vendor.objects.get(pk=invoice.purchase_invoice_vendor_name.id)
            # if item:
            #     due_amt = item.dueamount  # Accessing the dueamount attribute correctly

            # print(invoice, '**')
            ven_entries.append({
                'invoice_number': invoice.id,
                'date': invoice.purchase_invoice_date,
                'amount': invoice.purchase_invoice_total,
                'details': invoice,
                'due_date': invoice.purchase_due_date,
                'due_amt': due_amt,
                'due_days': (invoice.purchase_due_date - invoice.purchase_invoice_date).days
            })
        ven_entries.sort(key=lambda x: x['date'])
        return render(request, template_path.vendor_outs_report, {
            'ven_entries': ven_entries,
            'from_date': from_date,
            'to_date': to_date,
        })

    return render(request, template_path.vendor_outs, context)



@login_required
def expenses_report_date(request):
    return render(request, template_path.expense_date_wise)


@login_required
def sales_order_report_date(request):
   
    
    return render(request, template_path.sales_order_report_date)


@login_required
def vendor_order_report_date(request):
   
    
    return render(request, template_path.vendor_outs)





@login_required
def cash_voucher_date(request):
   
    return render(request, template_path.cash_voucher_date)



# @login_required

# def display_items_by_date_range(request):
#     if request.method == 'POST':
#         start_date_str = request.POST.get('start_date')
#         end_date_str = request.POST.get('end_date')

#         start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
#         end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

#         # Filter items within the date range
#         items_within_range = sales_order_items.objects.filter(date__range=(start_date, end_date))

#         # List to store modified items
#         modified_items = []

#         for item in items_within_range:
#             orderid = item.so_sales_order_id
#             try:
#                 so_buyer_order_no_ = sales_order.objects.get(id=orderid)
#                 customer = so_buyer_order_no_.so_customer_name.company_name

#                 buyer_ord_no = so_buyer_order_no_.so_buyer_order_no

#                 # Create a dictionary with the modified values
#                 modified_item = {
#                     'date': item.date,
#                     'company_name': customer,
#                     'so_buyer_order_no': buyer_ord_no,
#                     'so_description_goods': item.so_description_goods,
#                     'so_qantity': item.so_qantity,
#                     'so_uom': item.so_uom,
#                 }

#                 # Add the modified item to the list
#                 modified_items.append(modified_item)
#             except sales_order.DoesNotExist:
#                 # Handle the case where the related sales_order is not found
#                 pass

#         # Calculate total amount
#         total_amount = items_within_range.aggregate(total_amount=Sum('so_qantity'))['total_amount'] or 0



#         return render(request, template_path.sales_order_list_report, {'filtered_items': modified_items,'total_amount':total_amount})

#     return render(request, template_path.sales_order_date_report)


@login_required
def display_items_by_date_range(request):
    if request.method == 'POST':
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')

        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

        # Filter items within the date range
        items_within_range = sales_order_items.objects.filter(date__range=(start_date, end_date))

        # List to store modified items
        modified_items = []

        for item in items_within_range:
            orderid = item.so_sales_order_id
            try:
                so_buyer_order_no_ = sales_order.objects.get(id=orderid)
                customer = so_buyer_order_no_.so_customer_name.company_name

                buyer_ord_no = so_buyer_order_no_.so_buyer_order_no

                # Create a dictionary with the modified values
                modified_item = {
                    'date': item.date,
                    'company_name': customer,
                    'so_buyer_order_no': buyer_ord_no,
                    'so_description_goods': item.so_description_goods,
                    'so_qantity': item.so_qantity,
                    'so_uom': item.so_uom,
                }

                # Add the modified item to the list
                modified_items.append(modified_item)
            except sales_order.DoesNotExist:
                # Handle the case where the related sales_order is not found
                pass

        # Calculate total quantity
        total_quantity = sum(float(item.so_qantity) for item in items_within_range if item.so_qantity)

        # Pass the start_date and end_date to the template
        context = {
            'filtered_items': modified_items,
            'total_quantity': total_quantity,
            'start_date': start_date_str,
            'end_date': end_date_str
        }

        return render(request, template_path.sales_order_list_report, context)

    return render(request, template_path.sales_order_date_report)


@login_required
def display_cash_voucher_by_date_range(request):
    start_date = None
    end_date = None
    if request.method == 'POST':
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')

        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

        # Filter items within the date range
        items_within_range = cash_voucher.objects.filter(date__range=(start_date, end_date))

        # Extract specific fields for display
        filtered_items = items_within_range.values(
            'date', 'bill_no', 'voucher_number', 'amount', 'particular', 'pay_to'
        )

        # Calculate total amount
        total_amount = items_within_range.aggregate(total_amount=Sum('amount'))['total_amount'] or 0

        return render(request, template_path.cash_voucher_list_report, {
            'filtered_items': filtered_items,
            'total_amount': total_amount ,
             'start_date': start_date,
        'end_date': end_date, # Include total_amount in the context
        })
   

    return render(request, template_path.cash_voucher_date_report)


# def display_cash_voucher_by_date_range(request):
#     if request.method == 'POST':
#         start_date_str = request.POST.get('start_date')
#         end_date_str = request.POST.get('end_date')

#         start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
#         end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

#         # Filter items within the date range
#         items_within_range = cash_voucher.objects.filter(date__range=(start_date, end_date))

#         # Extract specific fields for display
#         filtered_items = items_within_range.values(
#             'date', 'bill_no', 'voucher_number', 'amount', 'particular', 'pay_to'
#         )

#         return render(request, template_path.cash_voucher_list_report, {'filtered_items': filtered_items})

#     return render(request, template_path.cash_voucher_date_report)



@login_required
def display_invoice_by_date_range(request):
    start_date = None
    end_date = None
    if request.method == 'POST':
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')

        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

        # Filter items within the date range
        # invoice_items_within_range = Invoice.objects.filter(invoice_date__range=(start_date, end_date))
        invoice_items_within_range = Invoice.objects.filter(invoice_date__range=(start_date, end_date)).select_related('invoice_customer_name_customer')
        # Extract specific fields for display
        filtered_items = invoice_items_within_range.values(
            'invoice_customer_name_customer__customer', 'invoice_gst_no', 'invoice_gst_no', 'id', 'invoice_date', 'invoice_sub_total','invoice_cgstval','invoice_sgstval','invoice_igstval','invoice_total'
        )

        # Calculate total amount
        total_amount = invoice_items_within_range.aggregate(total_amount=Sum('invoice_total'))['total_amount'] or 0

        return render(request, template_path.invoice_list_report, {
            'filtered_purchase_items': filtered_items,
            'total_amount': total_amount ,
             'start_date': start_date,
        'end_date': end_date, # Include total_amount in the context
        })
   

    return render(request, template_path.invoice_date_report)


###@login_required


@login_required
def display_inventory_summenry_date_range(request):
    vendors = vendor.objects.all().order_by('company_name')
    selected_company = ''
    filtered_items = []
    total_amount = 0
    start_date = None
    end_date = None

    if request.method == 'POST':
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')
        selected_company = request.POST.get('company_name', '').strip()

        # Save to session if you want to remember last search
        request.session['start_date'] = start_date_str
        request.session['end_date'] = end_date_str
        request.session['company_name'] = selected_company

        # Convert date strings to date objects
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

            items_within_range = inventory.objects.filter(
                date__range=(start_date, end_date)
            )

            # Filter by company if selected
            if selected_company:
                items_within_range = items_within_range.filter(
                    vendor_name__company_name__icontains=selected_company
                )

            items_within_range = items_within_range.annotate(
                item_code_int=Cast('item_code', IntegerField())
            ).order_by('item_code_int')

            # Prepare result data
            filtered_items = list(items_within_range.values(
                'item_code','vendor_name__company_name', 'inventory_name', 'opening_stock_quantity', 'purchase_rate'
            ))

            for item in filtered_items:
                try:
                    qty = float(item['opening_stock_quantity'])
                    rate = float(item['purchase_rate'])
                except (ValueError, TypeError):
                    qty, rate = 0, 0
                item['amount'] = qty * rate
                total_amount += item['amount']

    return render(request, template_path.inventory_summery_list_report, {
        'vendors': vendors,
        'selected_company': selected_company,
        'filtered_items': filtered_items,
        'total_amount': total_amount,
        'start_date': start_date,
        'end_date': end_date
    })



def get_companies_by_date(request):
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    if not start_date or not end_date:
        return JsonResponse([], safe=False)

    try:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        return JsonResponse([], safe=False)

    # Get vendor names from inventory records in the date range
    companies = (
        inventory.objects.filter(date__range=(start_date_obj, end_date_obj))
        .values_list("vendor_name__company_name", flat=True)
        .distinct()
    )

    return JsonResponse(list(companies), safe=False)


###

# @login_required
# def display_inventory_summenry_date_range(request):
#     if request.method == 'POST':
#         start_date_str = request.POST.get('start_date')
#         end_date_str = request.POST.get('end_date')

#         start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
#         end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

#         # Store the date range in the session
#         request.session['start_date'] = start_date_str
#         request.session['end_date'] = end_date_str


#         items_within_range = inventory.objects.filter(
#             date__range=(start_date, end_date)
#         ).annotate(
#             item_code_int=Cast('item_code', IntegerField())
#         ).order_by('item_code_int')

        
#         # Extract specific fields for display
#         filtered_items = list(items_within_range.values(
#             'item_code', 'inventory_name', 'opening_stock_quantity', 'purchase_rate'
#         ))

#         total_amount = 0
#         for item in filtered_items:
#             item['amount'] = float(item['opening_stock_quantity']) * float(item['purchase_rate'])
#             total_amount += item['amount']

#         context = {
#             'filtered_items': filtered_items,
#             'total_amount': total_amount,
#             'start_date': start_date,
#             'end_date': end_date
#         }

#         return render(request, template_path.inventory_summery_list_report, context)

#     return render(request, template_path.inventory_summery_date_report)





# @login_required
# def display_purchase_register_date_range(request):
#     if request.method == 'POST':
#         purchase_items_within_range = Purchase_Invoice.objects.all()

#         # Calculate totals
#         total_cgst = sum(float(item.purchase_invoice_cgstval or 0) for item in purchase_items_within_range)
#         print(total_cgst,'total_cgst---')
#         total_sgst = sum(float(item.purchase_invoice_sgstval or 0) for item in purchase_items_within_range)
#         total_igst = sum(float(item.purchase_invoice_igstval or 0) for item in purchase_items_within_range)
#         total_amount = sum(float(item.purchase_invoice_sub_total or 0) for item in purchase_items_within_range)
#         print(total_amount,'total_amount')
#         total_invoice = sum(float(item.purchase_invoice_total or 0) for item in purchase_items_within_range)
#         start_date_str = request.POST.get('start_date')
#         end_date_str = request.POST.get('end_date')

#         start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
#         end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

#         # Filter items within the date range
#         purchase_items_within_range = Purchase_Invoice.objects.filter(purchase_invoice_date__range=(start_date, end_date))


#         context = {
#             'purchase_items_within_range': purchase_items_within_range,
#             'total_cgst': total_cgst,
#             'total_sgst': total_sgst,
#             'total_igst': total_igst,
#             'total_amount': total_amount,
#             'total_invoice': total_invoice,
#         }
#         return render(request, template_path.purchase_register_list_report,context)

#     return render(request, template_path.purchase_register_date_report,context)


@login_required
def display_purchase_register_date_range(request):
    if request.method == 'POST':
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')

        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

        # Filter items within the date range
        purchase_items_within_range = Purchase_Invoice.objects.filter(purchase_invoice_date__range=(start_date, end_date))

        # Save the date range in the session
        request.session['start_date'] = start_date_str
        request.session['end_date'] = end_date_str

        # Calculate totals
        total_cgst = sum(float(item.purchase_invoice_cgstval or 0) for item in purchase_items_within_range)
        total_sgst = sum(float(item.purchase_invoice_sgstval or 0) for item in purchase_items_within_range)
        total_igst = sum(float(item.purchase_invoice_igstval or 0) for item in purchase_items_within_range)
        total_amount = sum(float(item.purchase_invoice_sub_total or 0) for item in purchase_items_within_range)
        total_invoice = sum(float(item.purchase_invoice_total or 0) for item in purchase_items_within_range)

        context = {
            'purchase_items_within_range': purchase_items_within_range,
            'total_cgst': total_cgst,
            'total_sgst': total_sgst,
            'total_igst': total_igst,
            'total_amount': total_amount,
            'total_invoice': total_invoice,
            'start_date': start_date_str,
            'end_date': end_date_str,
        }
        return render(request, template_path.purchase_register_list_report, context)

    return render(request, template_path.purchase_register_date_report)



#  HSN Wise Report
@login_required
def hsn_wise_date(request):
    return render(request, template_path.hsn_wise_date_report)

@login_required
def hsn_wise_by_date_range(request):
    start_date = None
    end_date = None
    if request.method == 'POST':
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')

        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

        request.session['start_date'] = start_date_str
        request.session['end_date'] = end_date_str


        

        # Filter items within the date range
        items_within_range = invoice_items.objects.filter(date__range=(start_date, end_date))

        # Extract specific fields for display
        filtered_items = items_within_range.values(
            'invoice_hsn', 'invoice_description_goods',  'invoice_godown','invoice_qantity','invoice_unit_price'
        )

        # Calculate total amount
        total_amount = items_within_range.aggregate(total_amount=Sum('invoice_tax_rate'))['total_amount'] or 0

        return render(request, template_path.hsn_wise_report, {
            'filtered_items': filtered_items,
            'total_amount': total_amount ,
            'start_date': start_date,
            'end_date': end_date,
        })
   

    return render(request, template_path.hsn_wise_date_report)


@login_required
def download_hsn_wise_excel(request):
    start_date_str = request.session.get('start_date')
    end_date_str = request.session.get('end_date')

    # Validate date strings
    if not start_date_str or not end_date_str:
        return HttpResponse("Start date and end date are required.", status=400)

    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    except ValueError:
        return HttpResponse("Invalid date format. Please use YYYY-MM-DD.", status=400)

    # Retrieve data from the database based on the date range
    items_within_range = invoice_items.objects.filter(date__range=(start_date, end_date))

    # Create an in-memory output file for the new workbook
    output = BytesIO()
    workbook = openpyxl.Workbook()
    sheet = workbook.active

    # Add title and date range
    title = "SUPREENO METALS PVT LTD"
    subtitle = "HSN Wise Report"
    date_range = f"From {start_date_str} To {end_date_str}"

    sheet.merge_cells('A1:E1')
    sheet.merge_cells('A2:E2')
    sheet.merge_cells('A3:E3')

    title_cell = sheet.cell(row=1, column=1)
    subtitle_cell = sheet.cell(row=2, column=1)
    date_range_cell = sheet.cell(row=3, column=1)

    title_cell.value = title
    subtitle_cell.value = subtitle
    date_range_cell.value = date_range

    title_cell.font = Font(size=14, bold=True)
    subtitle_cell.font = Font(size=12, bold=True)
    date_range_cell.font = Font(size=10, bold=True)

    # Write headers
    headers = ['HSN Code', 'Description', 'Godown', 'Quantity', 'Unit Price']
    sheet.append([])
    sheet.append(headers)

    total_amount = 0.0  # Initialize total amount

    # Write data rows
    for item in items_within_range:
        sheet.append([
            item.invoice_hsn,
            item.invoice_description_goods,
            item.invoice_godown,
            item.invoice_qantity,
            float(item.invoice_unit_price or 0)  # Convert to float
        ])
        total_amount += float(item.invoice_tax_rate or 0)  

    # Add total amount at the end
    sheet.append([])  # Empty row for spacing
    sheet.append(['', '', '', 'Total Amount', total_amount])

    # Set column widths for better visibility
    column_widths = [15, 30, 20, 15, 15]
    for i, column_width in enumerate(column_widths, start=1):
        sheet.column_dimensions[openpyxl.utils.get_column_letter(i)].width = column_width

    # Save the workbook to the output file
    workbook.save(output)
    output.seek(0)

    # Create the response
    response = HttpResponse(
        output,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=hsn_wise_report.xlsx'

    return response


# def inventory_division(request):
#     return render(request, template_path.hsn_wise_date_report)
from django.db.models import Sum, Q, F, FloatField


from django.db.models.functions import Cast


@login_required
def inventory_division_date(request):
    inventory_list = inventory.objects.all()  
    # print(inventory_list, 'inventory_list---') 
    return render(request, template_path.inventory_division_date_report, {'inventory_list': inventory_list})




@login_required
def display_inventory_division_date_range(request):
    inventory_name = None

    if request.method == 'POST':
        inventory_name = request.POST.get('inventory_name')

        # Filter items by inventory name
        items_within_range = inventory.objects.filter(
            inventory_name__icontains=inventory_name
        ).order_by('inventory_name')

        # Extract specific fields for display
        filtered_items = list(items_within_range.values(
            'item_code', 'inventory_name', 'units', 'opening_stock_quantity', 'purchase_rate','hsn'
        ))

        # Calculate the amount for each item and total amount
        total_amount = 0
        for item in filtered_items:
            item['amount'] = float(item['opening_stock_quantity']) * float(item['purchase_rate'])
            total_amount += item['amount']

        return render(request, template_path.inventory_division_list_report, {
            'filtered_items': filtered_items,
            'total_amount': total_amount,
            'inventory_name': inventory_name,
        })


    return render(request, template_path.inventory_division_date_report)



@login_required
def download_excel(request):
    start_date_str = request.session.get('start_date')
    end_date_str = request.session.get('end_date')

    # Validate date strings
    if not start_date_str or not end_date_str:
        return HttpResponse("Start date and end date are required.", status=400)

    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    except ValueError:
        return HttpResponse("Invalid date format. Please use YYYY-MM-DD.", status=400)

    # Retrieve data from the database based on the date range
    purchase_items_within_range = Purchase_Invoice.objects.filter(purchase_invoice_date__range=(start_date, end_date))

    # Create an in-memory output file for the new workbook
    output = BytesIO()
    workbook = openpyxl.Workbook()
    sheet = workbook.active

    # Add title and date range
    title = "M/S KEYMECH TECHNOLOGIES"
    subtitle = "Purchase Register Report"
    date_range = f"From {start_date_str} To {end_date_str}"

    sheet.merge_cells('A1:I1')
    sheet.merge_cells('A2:I2')
    sheet.merge_cells('A3:I3')

    title_cell = sheet.cell(row=1, column=1)
    subtitle_cell = sheet.cell(row=2, column=1)
    date_range_cell = sheet.cell(row=3, column=1)

    title_cell.value = title
    subtitle_cell.value = subtitle
    date_range_cell.value = date_range

    title_cell.font = Font(size=13, bold=True)
    subtitle_cell.font = Font(size=12, bold=True)
    date_range_cell.font = Font(size=10, bold=True)

    # Write headers
    headers = [
        'Vendor Name', 'Invoice No', 'Invoice Date', 'Amount', 'P&F', 'CGST', 'SGST', 'IGST', 'Total'
    ]
    sheet.append([])  # Add an empty row for spacing
    sheet.append(headers)

    total_amount = 0.0  # Initialize total amount

    # Write data rows
    for item in purchase_items_within_range:
        total = float(item.purchase_invoice_total or 0)  # Convert to float
        sheet.append([
            item.purchase_invoice_vendor_name.contact_person,
            item.purchase_invoice_grn_no,
            item.purchase_invoice_date,
            float(item.purchase_invoice_sub_total or 0),  # Convert to float
            float(item.purchase_freight_amount or 0),    # Convert to float
            float(item.purchase_invoice_cgstval or 0),    # Convert to float
            float(item.purchase_invoice_sgstval or 0),    # Convert to float
            float(item.purchase_invoice_igstval or 0),    # Convert to float
            total
        ])
        total_amount += total  # Add to total amount

    # Add total amount at the end
    sheet.append([])  # Empty row for spacing
    sheet.append(['', '', '', '', '', '', '', 'Total', total_amount])

    # Set column widths
    column_widths = [20, 15, 15, 15, 10, 10, 10, 10, 15]
    for col_num, width in enumerate(column_widths, 1):
        column_letter = openpyxl.utils.get_column_letter(col_num)
        sheet.column_dimensions[column_letter].width = width

    # Save the workbook to the output file
    workbook.save(output)
    output.seek(0)

    # Create the response
    response = HttpResponse(
        output,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=purchase_register.xlsx'
    response['Total-Amount'] = total_amount  # Optionally add total amount to response headers

    return response


@login_required
def download_sales_excel(request):
    start_date_str = request.session.get('start_date')
    end_date_str = request.session.get('end_date')

    # Validate date strings
    if not start_date_str or not end_date_str:
        return HttpResponse("Start date and end date are required.", status=400)

    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    except ValueError:
        return HttpResponse("Invalid date format. Please use YYYY-MM-DD.", status=400)

    # Retrieve data from the database based on the date range
    sales_register_within_range = Invoice.objects.filter(invoice_date__range=(start_date, end_date))


    output = BytesIO()
    workbook = openpyxl.Workbook()
    sheet = workbook.active

    # Add title and date range
    title = "KEYMECH TECHNOLOGIES"
    subtitle = "Sales Register Report"
    date_range = f"From {start_date_str} To {end_date_str}"

    sheet.merge_cells('A1:K1')
    sheet.merge_cells('A2:K2')
    sheet.merge_cells('A3:K3')

    title_cell = sheet.cell(row=1, column=1)
    subtitle_cell = sheet.cell(row=2, column=1)
    date_range_cell = sheet.cell(row=3, column=1)

    title_cell.value = title
    subtitle_cell.value = subtitle
    date_range_cell.value = date_range

    title_cell.font = Font(size=14, bold=True)
    subtitle_cell.font = Font(size=12, bold=True)
    date_range_cell.font = Font(size=10, bold=True)

    # Write headers
    headers = [
        'Date', 'Customer Name', 'GST No', 'PO No', 'Invoice No', 'Invoice Date',
        'Invoice Amount', 'CGST', 'SGST', 'IGST', 'Total'
    ]
    sheet.append([])
    sheet.append(headers)

    total_amount = 0.0  # Initialize total amount

    # Write data rows
    for item in sales_register_within_range:
        total = float(item.invoice_total or 0)  # Convert to float
        sheet.append([
            item.invoice_date,
            item.invoice_customer_name.dc_customer_name.customer,
            item.invoice_gst_no,
            item.invoice_buyer_order_no,
            item.inv_number,
            item.invoice_date,
            float(item.invoice_due or 0),        # Convert to float
            float(item.invoice_cgstval or 0),    # Convert to float
            float(item.invoice_sgstval or 0),    # Convert to float
            float(item.invoice_igstval or 0),    # Convert to float
            total
        ])
        total_amount += total  # Add to total amount

    # Add total amount at the end
    sheet.append([])  # Empty row for spacing
    sheet.append(['', '', '', '', '', '', '', '', '', 'Total', total_amount])

    # Set column widths for better visibility
    column_widths = [15, 20, 20, 20, 10, 15, 20, 10, 10, 20, 15]
    for i, column_width in enumerate(column_widths, start=1):
        sheet.column_dimensions[openpyxl.utils.get_column_letter(i)].width = column_width

    # Save the workbook to the output file
    workbook.save(output)
    output.seek(0)

    # Create the response
    response = HttpResponse(
        output,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=sales_register.xlsx'
    response['Total-Amount'] = total_amount  # Optionally add total amount to response headers

    return response


@login_required
def download_inventory_excel(request):
    start_date_str = request.session.get('start_date')
    end_date_str = request.session.get('end_date')
    selected_company = request.session.get('company_name', '').strip()

    # Validate date strings
    if not start_date_str or not end_date_str:
        return HttpResponse("Start date and end date are required.", status=400)

    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    except ValueError:
        return HttpResponse("Invalid date format. Please use YYYY-MM-DD.", status=400)

    # Retrieve data from the database based on the date range
    items_within_range = inventory.objects.filter(
        date__range=(start_date, end_date)
    )

    # Filter by selected company if provided
    if selected_company:
        items_within_range = items_within_range.filter(
            vendor_name__company_name__icontains=selected_company
        )

    items_within_range = items_within_range.order_by('date')

    # Extract fields including company name
    filtered_items = list(items_within_range.values(
        'vendor_name__company_name',
        'item_code',
        'inventory_name',
        'opening_stock_quantity',
        'purchase_rate'
    ))

    # Calculate amount
    total_amount = 0
    for item in filtered_items:
        try:
            qty = float(item['opening_stock_quantity'])
            rate = float(item['purchase_rate'])
        except (ValueError, TypeError):
            qty, rate = 0, 0
        item['amount'] = qty * rate
        total_amount += item['amount']

    # Create Excel
    output = BytesIO()
    workbook = openpyxl.Workbook()
    sheet = workbook.active

    # Titles
    title = "M/S KEYMECH TECHNOLOGIES"
    subtitle = "Inventory Summary Report"
    if selected_company:
        subtitle += f" - {selected_company}"
    date_range = f"From {start_date_str} To {end_date_str}"

    sheet.merge_cells('A1:F1')
    sheet.merge_cells('A2:F2')
    sheet.merge_cells('A3:F3')

    sheet.cell(row=1, column=1, value=title).font = Font(size=14, bold=True)
    sheet.cell(row=2, column=1, value=subtitle).font = Font(size=12, bold=True)
    sheet.cell(row=3, column=1, value=date_range).font = Font(size=10, bold=True)

    # Headers
    headers = ['Company Name', 'Item Code', 'Item', 'Quantity', 'Rate', 'Amount']
    sheet.append([])
    sheet.append(headers)

    # Data rows
    for item in filtered_items:
        sheet.append([
            item['vendor_name__company_name'],
            item['item_code'],
            item['inventory_name'],
            item['opening_stock_quantity'],
            item['purchase_rate'],
            item['amount']
        ])

    # Total row
    sheet.append([])
    sheet.append(['', '', '', '', 'Total', total_amount])

    # Column widths
    column_widths = [30, 15, 30, 15, 15, 20]
    for i, width in enumerate(column_widths, start=1):
        sheet.column_dimensions[openpyxl.utils.get_column_letter(i)].width = width

    workbook.save(output)
    output.seek(0)

    response = HttpResponse(
        output,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=inventory_summary.xlsx'
    return response

# @login_required
# def download_inventory_excel(request):
#     start_date_str = request.session.get('start_date')
#     end_date_str = request.session.get('end_date')

#     # Validate date strings
#     if not start_date_str or not end_date_str:
#         return HttpResponse("Start date and end date are required.", status=400)

#     try:
#         start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
#         end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
#     except ValueError:
#         return HttpResponse("Invalid date format. Please use YYYY-MM-DD.", status=400)

#     # Retrieve data from the database based on the date range
#     items_within_range = inventory.objects.filter(
#         date__range=(start_date, end_date),
#     ).order_by('date')

#     # Extract specific fields for display
#     filtered_items = list(items_within_range.values(
#         'item_code', 'inventory_name', 'opening_stock_quantity', 'purchase_rate'
#     ))

#     # Calculate the amount for each item and total amount
#     total_amount = 0
#     for item in filtered_items:
#         item['amount'] = float(item['opening_stock_quantity']) * float(item['purchase_rate'])
#         total_amount += item['amount']

#     # Create an in-memory output file for the new workbook
#     output = BytesIO()
#     workbook = openpyxl.Workbook()
#     sheet = workbook.active

#     # Add title and date range
#     title = "M/S KEYMECH TECHNOLOGIES"
#     subtitle = "Inventory Summary Report"
#     date_range = f"From {start_date_str} To {end_date_str}"

#     sheet.merge_cells('A1:E1')
#     sheet.merge_cells('A2:E2')
#     sheet.merge_cells('A3:E3')

#     title_cell = sheet.cell(row=1, column=1)
#     subtitle_cell = sheet.cell(row=2, column=1)
#     date_range_cell = sheet.cell(row=3, column=1)

#     title_cell.value = title
#     subtitle_cell.value = subtitle
#     date_range_cell.value = date_range

#     title_cell.font = Font(size=14, bold=True)
#     subtitle_cell.font = Font(size=12, bold=True)
#     date_range_cell.font = Font(size=10, bold=True)

#     # Write headers
#     headers = ['Item Code', 'Item', 'Quantity', 'Rate', 'Amount']
#     sheet.append([])
#     sheet.append(headers)

#     # Write data rows
#     for item in filtered_items:
#         sheet.append([
#             item['item_code'],
#             item['inventory_name'],
#             item['opening_stock_quantity'],
#             item['purchase_rate'],
#             item['amount']
#         ])

#     # Write total row
#     sheet.append([])
#     sheet.append(['', '', '', 'Total', total_amount])

#     # Set column widths for better visibility
#     column_widths = [15, 30, 15, 15, 20]
#     for i, column_width in enumerate(column_widths, start=1):
#         sheet.column_dimensions[openpyxl.utils.get_column_letter(i)].width = column_width

#     # Save the workbook to the output file
#     workbook.save(output)
#     output.seek(0)

#     # Create the response
#     response = HttpResponse(
#         output,
#         content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
#     )
#     response['Content-Disposition'] = 'attachment; filename=inventory_summary.xlsx'
#     return response


@login_required
def purchase_register_detail(request, id):
    invoice = get_object_or_404(Purchase_Invoice, id=id)
    items = Purchase_Invoice_items.objects.filter(purchase_invoice_id=id)

    context = {
        'invoice': invoice, 
        

    }
    return render(request, 'Report/purchase_register_view.html', {'invoice': invoice, 'items': items})
    # return render(request, template_path.purchase_register_detail,context)


@login_required
def sales_display_items_by_date_range(request):
    if request.method == 'POST':
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')

        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

        # Filter items within the date range
        items_within_range = Invoice.objects.filter(invoice_date__range=(start_date, end_date))

        return render(request, template_path.sales_register_list_report, {'items_within_range': items_within_range})

    return render(request, template_path.sales_register_date_report)



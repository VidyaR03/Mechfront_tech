from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db.models import Q
from datetime import datetime
from core.modules import template_path
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect,HttpResponse
from django.core import serializers
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder
from core.models import  customer, Account_Expense, inventory, vendor, Invoice, expense_advice, expense_advice_item,acc_expense
from core.modules.login.login import login_required
import inflect
from django.db.models import DecimalField
from django.db.models.functions import Cast

from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.template.loader import get_template
from weasyprint import HTML


# @login_required
def fn_expense_advice_list_View(request):
    expense_advice_list = expense_advice.objects.all().order_by('-ea_date')
    lengt_itr = len(expense_advice_list)
    n = 1
    for i in expense_advice_list:
        i.serial_no = lengt_itr
        lengt_itr -= 1
        # i.serial_no = n
        # n += 1
        
    context = {
        'expense_advice_list':expense_advice_list
        }
    return render(request,template_path.expense_advice_list,context)

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

# @login_required
def delete_expense_advice(request, expense_advice_id):
    expense = get_object_or_404(expense_advice, id=expense_advice_id)

    if request.method == "POST":
        expense.delete()
        messages.success(request, "Expense advice deleted successfully.")
        return redirect('expense_advice_list_View')

    return redirect('expense_advice_list_View')
import re
    
def fnadd_expense_advice(request):
    if request.method == "GET":
        customer_name = customer.objects.all()
        vendor_data = vendor.objects.all()
        latest_expense_advice = expense_advice.objects.latest('id') if expense_advice.objects.exists() else None
        #new_expense_advice_no = int(latest_expense_advice.ea_expense_advice_no) + 1 if latest_expense_advice else 1

        if latest_expense_advice:
            numeric_part = re.search(r'\d+', latest_expense_advice.ea_expense_advice_no)
            if numeric_part:
                new_expense_advice_no = int(numeric_part.group()) + 1
            else:
                new_expense_advice_no = 1
        else:
            new_expense_advice_no = 1
        
            
        context ={ 
            'customer_name': customer_name,
            'vendor_data': vendor_data,
            'new_expense_advice_no': new_expense_advice_no
        }
        return render(request, template_path.add_expense_advice_path, context)

    elif request.method == "POST":
        expense_advice_date_str = request.POST['date']
        expense_advice_check_str = request.POST['cheque_date']
        customer_id = request.POST['customer_Name_id']
        q_customer_name = vendor.objects.filter(id=customer_id).first()

        if expense_advice_check_str is not None and expense_advice_check_str != '':
            expense_advice_check_date = datetime.strptime(expense_advice_check_str, '%d-%m-%Y').date()
        else:
            expense_advice_check_date = None
        
        expense_advice_date = datetime.strptime(expense_advice_date_str, '%d-%m-%Y').date()

        def safe_float_conversion(value):
            try:
                return float(value)
            except (ValueError, TypeError):
                return 0.0  # Default value if conversion fails

        expense_advice_data = {
            'ea_deposit': vendor.objects.filter(id=request.POST['customer_Name_id']).first(),
            'ea_vendor': vendor.objects.filter(id=request.POST['customer']).first(),
            'ea_date': expense_advice_date,
            'ea_payment_mode': request.POST['payment_mode'],
            'ea_mobile': request.POST['mobile'],
            'ea_balance': request.POST.get('balance', 'off'),
            'ea_amount': safe_float_conversion(request.POST['amount']),
            'ea_expense_advice_no': request.POST['paymentreceiptno'],
            'ea_bank_charges': safe_float_conversion(request.POST['bank_charges']),
            'ea_cheque_no': request.POST['cheque_no'],
            'ea_cheque_date': expense_advice_check_date,
            'ea_reference': request.POST.get('reference'),
            'ea_note': request.POST['note'],
            'ea_po_no': request.POST['ea_po_no'],
            'ea_total': safe_float_conversion(request.POST['total']),
            'ea_amount_received': safe_float_conversion(request.POST['amount_received']),
            'ea_amount_used': safe_float_conversion(request.POST['amount_used']),
            'ea_amount_excess': safe_float_conversion(request.POST['amount_excess']),
            'ea_advice_no': request.POST['ea_advice_no']
        }

        expense_advice_object = expense_advice(**expense_advice_data)
        expense_advice_object.save()

        i = 0
        max_row = int(request.POST.get('row_count'))
        latest_id = expense_advice.objects.latest('id')

        while max_row:
            payment = safe_float_conversion(request.POST.get(f'payment{i}'))
            id = request.POST.get(f'id_i_{i}')                 
            invoiceamount = safe_float_conversion(request.POST.get(f'invoiceamount{i}'))
            dueamount = invoiceamount - payment
            purchase_invoice_item = expense_advice_item(
                ea_date=request.POST.get(f'invoicedate{i}'),
                vendor=request.POST.get(f'customername{i}'),
                ea_invoice_no=request.POST.get(f'invoiceno{i}'),
                ea_invoice_amt=invoiceamount,
                ea_payment_receive=request.POST.get(f'paymentreceiptno{i}'),
                ea_due_amount=dueamount,
                ea_payment=payment,
                ex_expense_adv_id=latest_id.id                
            )
            purchase_invoice_item.save()
            exp = Account_Expense.objects.get(id=id)
            exp.ae_due_amount = float(exp.ae_due_amount) - payment
            exp.save()

            max_row -= 1
            i += 1

        return redirect('expense_advice_list_View')



@csrf_exempt
def get_vendor_expenses(request):
    try:
        if request.method == 'POST':
            customer_id = request.POST.get('customer')
            data = Account_Expense.objects.annotate(
                due_amount_numeric=Cast('ae_due_amount', DecimalField(max_digits=10, decimal_places=2))
            ).filter(
                ae_vendor_name=customer_id,
                ae_due_amount__isnull=False,
                due_amount_numeric__gt=0
            ).values(
                'id', 'ae_invoice_date', 'ae_vendor_name', 'ae_invoice_no', 'all_total', 'ae_due_amount'
            )
            data_list = list(data)
            print("00000000000000", data_list)
            return JsonResponse(data_list, safe=False, encoder=DjangoJSONEncoder)
    except Exception as e:
        print(e, "DDDD")
    return JsonResponse({'error': 'Invalid request method'})


# @login_required
def payment_pdf(request, id):
    payment = get_object_or_404(expense_advice, id=id)
    company_name = payment.ea_deposit.company_name
    deposit_to = payment.ea_deposit.company_name

    payment_item_data = expense_advice_item.objects.filter(ex_expense_adv_id = id)
    for i in payment_item_data:
        print(i.ea_due_amount)
    
    context = {
        'deposit_name':company_name.upper(),
        'deposit_to':deposit_to.upper(),
        'payment':payment,
        'date':i.ea_date,
        'invoice_amt':i.ea_invoice_amt,
        'dueamount':i.ea_due_amount,
        'payment_item_data':payment_item_data
        }
    return render(request, template_path.expense_advice,context)



def expense_pdf_download(request, id):
    ex_advice = get_object_or_404(expense_advice, id=id)

    # Only fully paid items (ea_due_amount == 0.0)
    expense_advice_items = expense_advice_item.objects.filter(
        ex_expense_adv_id=id,
        ea_due_amount='0.0'  # string compare because ea_due_amount is probably CharField
    )

    # ✅ Convert total amount to words
    p = inflect.engine()
    total_amount_in_words = p.number_to_words(ex_advice.ea_amount).title()

    # ✅ Calculate totals
    subtotal_invoice_amount = sum(
        float(item.ea_invoice_amt) for item in expense_advice_items if item.ea_invoice_amt
    )
    subtotal_due_amount = sum(
        float(item.ea_due_amount) for item in expense_advice_items if item.ea_due_amount
    )

    context = {
        'ex_advice': ex_advice,
        'total_amount_in_words': total_amount_in_words,
        'expense_advice_items': expense_advice_items,
        'subtotal_invoice_amount': subtotal_invoice_amount,
        'subtotal_due_amount': subtotal_due_amount,
    }

    # ✅ Render and generate PDF
    template = get_template('Account/pdf.html')  # 👈 Change this if needed
    html_string = template.render(context)
    base_url = request.build_absolute_uri('/')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="expense_advice.pdf"'

    try:
        HTML(string=html_string, base_url=base_url).write_pdf(response)
        return response
    except Exception as e:
        return HttpResponse(f'Error generating PDF: {str(e)}')


def fnedit_expense_advice(request, expense_advice_id):
    # Fetch the main object and related items
    expense_advice_object = get_object_or_404(expense_advice, id=expense_advice_id)
    payment_advice_item_data = expense_advice_item.objects.filter(ex_expense_adv_id=expense_advice_id)

    if request.method == "GET":
        # Fetch related data for the dropdowns
        customer_name = customer.objects.all()
        vendor_data = vendor.objects.all()

        # Pass data to the template
        context = {
            'expense_advice_object': expense_advice_object,
            'customer_name': customer_name,
            'vendor_data': vendor_data,
            'payment_advice_item_data': payment_advice_item_data,
        }
        return render(request, template_path.expense_advice_edit_path, context)

    elif request.method == "POST":
        # Helper function for float conversion
        def safe_float_conversion(value):
            try:
                return float(value)
            except (ValueError, TypeError):
                return 0.0
        
        mobile = request.POST.get("ea_mobile")
    
        if not mobile.isdigit() or len(mobile) != 10:
            messages.error(request, "Mobile number must be exactly 10 digits.")
            return redirect(request.path)

        # Update the main expense_advice record
        expense_advice_date_str = request.POST.get('ea_date')
        expense_advice_date = datetime.strptime(expense_advice_date_str, '%d-%m-%Y').date()

        # Update fields
        expense_advice_object.ea_deposit = vendor.objects.filter(id=request.POST['customer_Name_id']).first()
        expense_advice_object.ea_vendor = vendor.objects.filter(id=request.POST['ea_vendor']).first()
        expense_advice_object.ea_date = expense_advice_date
        expense_advice_object.ea_payment_mode = request.POST['ea_payment_mode']
        expense_advice_object.ea_mobile = request.POST['ea_mobile']
        expense_advice_object.ea_amount = safe_float_conversion(request.POST['ea_amount'])
        expense_advice_object.ea_bank_charges = safe_float_conversion(request.POST['ea_bank_charges'])
        expense_advice_object.ea_note = request.POST['note']
        expense_advice_object.ea_po_no = request.POST['ea_po_no']
        expense_advice_object.ea_total = safe_float_conversion(request.POST['total'])
        expense_advice_object.ea_amount_received = safe_float_conversion(request.POST['amount_received'])
        expense_advice_object.ea_amount_used = safe_float_conversion(request.POST['amount_used'])
        expense_advice_object.ea_amount_excess = safe_float_conversion(request.POST['amount_excess'])
        expense_advice_object.ea_advice_no = request.POST['ea_advice_no']
        expense_advice_object.ea_reference = request.POST['reference']

        expense_advice_object.save()

        # Handle associated items
        max_row = int(request.POST.get('row_count'))
        updated_item_ids = []
        for i in range(1, max_row + 1):
            item_id = request.POST.get(f'id_i_{i}')
            if not item_id:  # Skip if item ID is not present
                continue

            # Fetch or create the item
            item = expense_advice_item.objects.filter(id=item_id).first() or expense_advice_item()
            item.ex_expense_adv_id = expense_advice_object.id

            # Update fields
            item.ea_date = datetime.strptime(request.POST.get(f'invoicedate{i}'), '%Y-%m-%d').date()
            item.vendor = request.POST.get(f'customername{i}')
            item.ea_invoice_no = request.POST.get(f'invoiceno{i}')
            item.ea_invoice_amt = safe_float_conversion(request.POST.get(f'invoiceamount{i}'))
            item.ea_due_amount = safe_float_conversion(request.POST.get(f'dueamount{i}'))
            item.ea_payment = safe_float_conversion(request.POST.get(f'payment{i}'))

            item.save()
            updated_item_ids.append(str(item.id))

        # Delete items removed from the form
        for item in payment_advice_item_data:
            if str(item.id) not in updated_item_ids:
                item.delete()

        # Redirect to the list view after saving
        return redirect('expense_advice_list_View')


def autocomplete_accexpense(request):
    term = request.GET.get('term', '')
    customers = customer.objects.filter(customer__icontains=term)
    results = [{'id': customer.id, 'label': customer.customer, 'value': customer.customer} for customer in customers]
    return JsonResponse(results, safe=False)


    

def show_expense_advise(request, id):
    ex_advice = get_object_or_404(expense_advice, id=id)
    expense_advice_items = expense_advice_item.objects.filter(ex_expense_adv_id=id)
    # for i in expense_advice_items:
    #     print('@#$%^&*',i.ea_invoice_amt)


    p = inflect.engine()
    total_amount_in_words = p.number_to_words(ex_advice.ea_amount)
    total_amount_in_words = total_amount_in_words.title()

    subtotal_invoice_amount = sum(float(item.ea_invoice_amt) for item in expense_advice_items if item.ea_invoice_amt)
    subtotal_due_amount = sum(float(item.ea_due_amount) for item in expense_advice_items if item.ea_due_amount)





    context = {
        'ex_advice':ex_advice,
        'total_amount_in_words':total_amount_in_words,
        'expense_advice_items': expense_advice_items,
        'subtotal_invoice_amount': subtotal_invoice_amount,
        'subtotal_due_amount': subtotal_due_amount,
        'subtotal_invoice_amount' : sum(float(item.ea_invoice_amt) for item in expense_advice_items if item.ea_invoice_amt),
        'subtotal_due_amount' : sum(float(item.ea_due_amount) for item in expense_advice_items if item.ea_due_amount)




        }
    return render(request, template_path.expense_advice,context)



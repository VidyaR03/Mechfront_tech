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
from core.models import  customer, transporter, inventory, vendor, Invoice, expense_advice, expense_advice_item,acc_expense,expense_vendor
from core.modules.login.login import login_required
from django.contrib import messages

@login_required
def fn_expense_advice_list_View(request):
    expense_advice_list = expense_advice.objects.all().order_by('-id')
    context = {
        'expense_advice_list':expense_advice_list
        }
    return render(request,template_path.expense_advice_list,context)


def delete_expenses_advice(request, advice_id):
    # Get the customer instance based on the provided ID
    expense_advice_data = get_object_or_404(expense_advice, id=advice_id)    
    expense_advice_data.delete()
    messages.error(request,'Expense Deleted.')

    return redirect('expense_advice_list_View') 


@login_required
def fnadd_expense_advice(request):
    if request.method == "GET":
        customer_name = customer.objects.all()
        vendor_data = vendor.objects.all()
        context ={ 
            'customer_name' : customer_name,
            'vendor_data' : vendor_data,
            }
        return render(request, template_path.add_expense_advice_path, context)
    elif request.method == "POST":
        expense_advice_date_str = request.POST['date']
        expense_advice_check_str = request.POST['cheque_date']
        if expense_advice_check_str is not None and expense_advice_check_str != '':
            expense_advice_check_date = datetime.strptime(expense_advice_check_str, '%d-%m-%Y').date()
        else:
            expense_advice_check_date = None
        expense_advice_date = datetime.strptime(expense_advice_date_str, '%d-%m-%Y').date()
        expense_advice_data = {
            'ea_deposit':vendor.objects.filter(id=request.POST['deposite']).first(),
            'ea_vendor':vendor.objects.filter(id=request.POST['customer']).first(),
            'ea_date':expense_advice_date,
            # 'expense_advice_expiry_date':expense_advice_expiry_date,
            'ea_payment_mode':request.POST['payment_mode'],
            'ea_mobile':request.POST['mobile'],
            'ea_balance': request.POST.get('balance', 'off'),
            'ea_amount':request.POST['amount'],
            'ea_expense_advice_no':request.POST['paymentreceiptno'],
            'ea_bank_charges':request.POST['bank_charges'],
            'ea_cheque_no':request.POST['cheque_no'],
            'ea_cheque_date':expense_advice_check_date,
            'ea_reference':request.POST['reference'],
            'ea_note':request.POST['note'],
            # 'ea_po_no':request.POST['ea_po_no'],
            'ea_total':request.POST['total'],
            'ea_amount_received':request.POST['amount_received'],
            'ea_amount_used':request.POST['amount_used'],
            'ea_amount_excess':request.POST['amount_excess'],
        }
        expense_advice_object = expense_advice(**expense_advice_data)
        expense_advice_object.save()
        i = 0
        max_row = int(request.POST.get('row_count'))
        latest_id = expense_advice.objects.latest('id')
        while max_row:
            payment = request.POST.get(f'payment{i}')
            invoiceamount = request.POST.get(f'invoiceamount{i}')
            dueamount = float(invoiceamount) -  float(payment)

            purchase_invoice_item = expense_advice_item(
                ea_date = request.POST.get(f'invoicedate{i}'),
                vendor = request.POST.get(f'customername{i}'),
                ea_invoice_no = request.POST.get(f'invoiceno{i}'),
                ea_invoice_amt = request.POST.get(f'invoiceamount{i}'),
                ea_payment_receive = request.POST.get(f'paymentreceiptno{i}'),
                ea_due_amount = dueamount,
                ea_payment = request.POST.get(f'payment{i}'),
                ex_expense_adv_id = latest_id.id                
            )
            purchase_invoice_item.save()
            max_row = max_row-1
            i = i + 1
        messages.success(request,'Expense Advice Added Successfully')

        return redirect('expense_advice_list_View')
    
    



# @csrf_exempt
# def get_customer_invoice_details(request):
#     if request.method == 'POST':
#         customer_id = request.POST.get('customer')
#         data = Invoice.objects.filter(invoice_customer_name = customer_id).values(
#                 'invoice_date', 'invoice_customer_name', 'id', 'invoice_total'
#         )
#         data_list = list(data)

#         # Convert list to JSON using DjangoJSONEncoder to handle datetime fields
#         json_data = json.dumps(data_list, cls=DjangoJSONEncoder)

#         return JsonResponse(json_data, safe=False)

#     return JsonResponse({'error': 'Invalid request method'})


@csrf_exempt
@login_required
def get_vendor_expenses(request):
    if request.method == 'POST':
        customer_id = request.POST.get('customer')
        # Assuming YourModel has fields like 'invoice_date', 'customer_name', 'invoice_no', 'totalamt', 'payments'
        data = expense_vendor.objects.filter(ex_vendor_name = customer_id).values(
                'ex_invoice_date', 'ex_vendor_name', 'id', 'all_total'
        )
        # Convert QuerySet to a list of dictionaries
        data_list = list(data)
        print("00000000000000",data_list)
        return JsonResponse(data_list, safe=False, encoder=DjangoJSONEncoder)
    return JsonResponse({'error': 'Invalid request method'})




@login_required
def payment_pdf(request, id):
    payment = get_object_or_404(expense_advice, id=id)
    company_name = payment.expense_advice_deposite.company_name
    deposit_to = payment.expense_advice_customer.company_name

    payment_item_data = expense_advice_item.objects.filter(expense_advice_id = id)
    for i in payment_item_data:
        pass
    
    context = {
        'deposit_name':company_name.upper(),
        'deposit_to':deposit_to.upper(),
        'payment':payment,
        'date':i.invoicedate,
        'invoice_amt':i.invoiceamount,
        'dueamount':i.dueamount,
        'payment_item_data':payment_item_data
        }
    return render(request, template_path.expense_advice_pdf,context)

@login_required
def fnedit_expense_advice(request, advice_id):
    expense_advice_object = get_object_or_404(expense_advice, id=advice_id)
    if request.method == "GET":
        customer_name = customer.objects.all()
        vendor_data = vendor.objects.all()
        context = {
            'customer_name': customer_name,
            'vendor_data': vendor_data,
            'expense_advice_object': expense_advice_object
        }
        return render(request, template_path.expense_advice_edit_path, context)
    elif request.method == "POST":
        print(request.POST)
        expense_advice_date_str = request.POST.get('date')
        expense_advice_check_str = request.POST.get('cheque_date')

        print(expense_advice_date_str, expense_advice_check_str, "lllllllllllll")
        if expense_advice_check_str:
            expense_advice_check_date = datetime.strptime(expense_advice_check_str, '%Y-%m-%d').date()
        else:
            expense_advice_check_date = None
        
        if expense_advice_date_str:
            expense_advice_date = datetime.strptime(expense_advice_date_str, '%Y-%m-%d').date()
        else:
            expense_advice_date = None

        expense_advice_data = {
            'ea_deposit': vendor.objects.filter(id=request.POST.get('ea_deposit')).first(),
            'ea_vendor': vendor.objects.filter(id=request.POST.get('ea_vendor')).first(),
            'ea_date': expense_advice_date,
            'ea_payment_mode': request.POST.get('ea_payment_mode'),
            'ea_mobile': request.POST.get('ea_mobile'),
            'ea_balance': request.POST.get('balance', 'off'),
            'ea_amount': request.POST.get('ea_amount'),
            'ea_expense_advice_no': request.POST.get('ea_expense_advice_no'),
            'ea_bank_charges': request.POST.get('ea_bank_charges'),
            'ea_cheque_no': request.POST.get('ea_cheque_no'),
            'ea_cheque_date': expense_advice_check_date,
            'ea_reference': request.POST.get('ea_reference'),
            'ea_total': request.POST.get('ea_total'),
            'ea_amount_received': request.POST.get('amount_received'),
            'ea_amount_used': request.POST.get('amount_used'),
            'ea_amount_excess': request.POST.get('amount_excess'),
        }
        
        # Update existing object instead of creating a new one
        for key, value in expense_advice_data.items():
            setattr(expense_advice_object, key, value)
        
        expense_advice_object.save()

        # Handle purchase invoice items
        row_count_str = request.POST.get('row_count')
        try:
            max_row = int(row_count_str)
        except (TypeError, ValueError):
            max_row = 0

        latest_id = expense_advice_object.id
        for i in range(max_row):
            payment = request.POST.get(f'payment{i}')
            invoiceamount = request.POST.get(f'invoiceamount{i}')
            if payment is not None and invoiceamount is not None:
                try:
                    dueamount = float(invoiceamount) - float(payment)
                except ValueError:
                    dueamount = 0.0

                purchase_invoice_item = expense_advice_item(
                    ea_date=request.POST.get(f'invoicedate{i}'),
                    vendor=request.POST.get(f'customername{i}'),
                    ea_invoice_no=request.POST.get(f'invoiceno{i}'),
                    ea_invoice_amt=request.POST.get(f'invoiceamount{i}'),
                    ea_payment_receive=request.POST.get(f'paymentreceiptno{i}'),
                    ea_due_amount=dueamount,
                    ea_payment=request.POST.get(f'payment{i}'),
                    ex_expense_adv_id=latest_id
                )
                purchase_invoice_item.save()
        messages.success(request,'Expense Advice Updated Successfully')

        return redirect('expense_advice_list_View')

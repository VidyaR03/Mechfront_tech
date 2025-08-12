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
from core.models import  customer, transporter, inventory, vendor, Invoice, payment_received, payment_received_item
from core.modules.login.login import login_required
from django.contrib import messages


@login_required
def paymentreceived_list_view(request):
    payment_received_list = payment_received.objects.all().order_by('-id')
    context = {
        'payment_received_list':payment_received_list
        }
    return render(request,template_path.paymentreceived_list,context)


@login_required
def delete_payment_received_data(request, id):
    # Get the customer instance based on the provided ID
    payment_received_data = get_object_or_404(payment_received, id=id)    
    payment_received_data.delete()
    messages.error(request, 'Payment Received Record Deleted.')

    return redirect('payment_received_list') 


@login_required
def add_payment_received_data(request):
    if request.method == "GET":
        customer_name = customer.objects.all()
        vendor_data = vendor.objects.all()
        context ={ 
            'customer_name' : customer_name,
            'vendor_data' : vendor_data,
            }
        return render(request, template_path.add_paymentreceived, context)
    elif request.method == "POST":
        payment_received_date_str = request.POST['date']
        payment_received_check_str = request.POST['cheque_date']
        if payment_received_check_str is not None and payment_received_check_str != '':
            payment_received_check_date = datetime.strptime(payment_received_check_str, '%d-%m-%Y').date()
        else:
            payment_received_check_date = None
        payment_received_date = datetime.strptime(payment_received_date_str, '%d-%m-%Y').date()
        payment_received_data = {
            # 'payment_received_deposite':vendor.objects.filter(id=request.POST['deposite']).first(),
            'payment_received_customer':customer.objects.filter(id=request.POST['customer']).first(),
            'payment_received_date':payment_received_date,
            'payment_received_bank_name':request.POST['payment_received_bank_name'],
            # 'payment_received_expiry_date':payment_received_expiry_date,
            'payment_received_payment_mode':request.POST['payment_mode'],
            'payment_received_mobile':request.POST['mobile'],
            'payment_received_balance':request.POST.get('balance', 'off'),
            'payment_received_amount':request.POST['amount'],
            'payment_received_payment_receipt_no':request.POST['paymentreceiptno'],
            'payment_received_bank_charges':request.POST['bank_charges'],
            'payment_received_cheque_no':request.POST['cheque_no'],
            'payment_received_cheque_date':payment_received_check_date,
            'payment_received_reference':request.POST['reference'],
            'payment_received_note':request.POST['note'],
            # 'payment_received_payment':request.POST['packing']
            'payment_received_total':request.POST['total'],
            'payment_received_amount_received':request.POST['amount_received'],
            'payment_received_amount_used':request.POST['amount_used'],
            'payment_received_amount_excess':request.POST['amount_excess'],
        }
        payment_received_object = payment_received(**payment_received_data)
        payment_received_object.save()
        i = 0
        max_row = int(request.POST.get('row_count'))
        latest_id = payment_received.objects.latest('id')
        while max_row:
            payment = request.POST.get(f'payment{i}')
            invoiceamount = request.POST.get(f'invoiceamount{i}')
            dueamount = float(invoiceamount) -  float(payment)

            purchase_invoice_item = payment_received_item(
                invoicedate = request.POST.get(f'invoicedate{i}'),
                customer = request.POST.get(f'customername{i}'),
                invoicenumber = request.POST.get(f'invoiceno{i}'),
                invoiceamount = request.POST.get(f'invoiceamount{i}'),
                paymentreceivedno = request.POST.get(f'paymentreceiptno{i}'),
                dueamount = dueamount,
                payment = request.POST.get(f'payment{i}'),
                payment_received_id = latest_id.id                
            )
            purchase_invoice_item.save()
            max_row = max_row-1
            i = i + 1
        messages.success(request, 'Payment Received Created Successfully.')

        return redirect('payment_received_list')
    
    
def edit_payment_received_data(request, id):
    payment_received_instance = get_object_or_404(payment_received, id=id)
    payment_received_item_data = payment_received_item.objects.filter(payment_received_id=id)
    if request.method == "GET":
        customer_name = customer.objects.all()
        vendor_data = vendor.objects.all()
        payment_received_item_data = payment_received_item.objects.filter(payment_received_id=id)
        context ={ 
            'customer_name' : customer_name,
            'vendor_data' : vendor_data,
            'payment_received_instance': payment_received_instance,
            'payment_received_item_data': payment_received_item_data,
            'len_payment_received_item_data': len(payment_received_item_data)
            }
        return render(request, template_path.edit_paymentreceived, context)
    elif request.method == "POST":
        print(request.POST)
      
        total_due = request.POST['amount_received']
        payment_received_date_str = request.POST['date']
        payment_received_check_str = request.POST['cheque_date']
        if payment_received_check_str is not None and payment_received_check_str != '':
            payment_received_check_date = datetime.strptime(payment_received_check_str, '%d-%m-%Y').date()
        else:
            payment_received_check_date = None
        payment_received_date = datetime.strptime(payment_received_date_str, '%d-%m-%Y').date()
        
        if request.POST.get('note'):
            note = request.POST['note']
        else:
            note = payment_received_instance.payment_received_note
        payment_received_data = {
            # 'custom_id': payment_received_instance.custom_id,
            'id': id,
            # 'payment_received_deposite':vendor.objects.filter(id=request.POST['deposite']).first(),
            'payment_received_customer':customer.objects.filter(id=request.POST['customer_id']).first(),
            'payment_received_date':payment_received_date,
            # 'payment_received_expiry_date':payment_received_expiry_date,
            'payment_received_bank_name':request.POST['payment_received_bank_name'],
            'payment_received_payment_mode':request.POST['payment_mode'],
            'payment_received_mobile':request.POST['mobile'],
            'payment_received_balance':request.POST.get('balance', 'off'),
            'payment_received_amount':request.POST['amount'],
            'payment_received_payment_receipt_no':request.POST['paymentreceiptno'],
            'payment_received_bank_charges':request.POST['bank_charges'],
            'payment_received_cheque_no':request.POST['cheque_no'],
            'payment_received_cheque_date':payment_received_check_date,
            'payment_received_reference':request.POST['reference'],
            'payment_received_note':note,
            # 'payment_received_payment':request.POST['packing']
            'payment_received_total':request.POST['total'],
            'payment_received_amount_received':request.POST['amount_received'],
            'payment_received_amount_used':request.POST['amount_used'],
            'payment_received_amount_excess':request.POST['amount_excess'],
            # 'payment_ser_type':request.POST['payment_ser_type'].capitalize(),
        }
        payment_received_object = payment_received(**payment_received_data)
        payment_received_object.save()
        i = 1
        total = 0.0
        due_list = []
        max_row = request.POST.get('iid[]')
        payment_received_item_data.delete()
        while max_row:
            payment = request.POST.get(f'payment{i}')
            invoiceamount = request.POST.get(f'invoiceamount{i}')
            due_amt = request.POST.get(f'dueamount{i}')
            dueamount = (float(invoiceamount)- 100) -  float(payment) 
            print(due_amt,total,'_____')
            total += float(due_amt)
            inv_amt = Invoice.objects.get(id=request.POST.get(f'invoiceno{i}'))
            purchase_invoice_item = payment_received_item(
                invoicedate = request.POST.get(f'invoicedate{i}'),
                customer = request.POST.get(f'customername{i}'),
                invoicenumber = request.POST.get(f'invoiceno{i}'),
                invoiceamount = request.POST.get(f'invoiceamount{i}'),
                paymentreceivedno = request.POST.get(f'paymentreceiptno{i}'),
                dueamount = dueamount,
                payment = request.POST.get(f'payment{i}'),
                payment_received_id = id               
            )
            purchase_invoice_item.save()
            inv_amt.invoice_due = dueamount
            due_list.append(dueamount)
            print(due_amt,payment, '%3333')
            if due_amt == payment:
                inv_amt.invoice_status = 'Received'
            else:
                inv_amt.invoice_status = 'Pending'
            inv_amt.save()

            # max_row = max_row-1
            max_row = int(max_row) - 1

            i = i + 1
        print('*************',total)    
        payment_received_object.payment_received_due_amount = total
        payment_received_object.save()
        return redirect('payment_received_list')


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
def get_customer_invoice_details(request):
    if request.method == 'POST':
        customer_id = request.POST.get('customer')
        print(customer_id,"customer_id........")
        # Assuming YourModel has fields like 'invoice_date', 'customer_name', 'invoice_no', 'totalamt', 'payments'
        # data = Invoice.objects.filter(invoice_customer_name = customer_id).values(
        #         'invoice_date', 'invoice_customer_name', 'id', 'invoice_total'
        # )
        data = Invoice.objects.filter(invoice_customer_name_customer = customer_id).values(
            'invoice_date', 'invoice_customer_name', 'id', 'invoice_total'
        )
        print(data,"-------------------------------------")
        # Convert QuerySet to a list of dictionaries
        data_list = list(data)
        print(data_list,">>>>>>>>>>>>>>>>")
        return JsonResponse(data_list, safe=False, encoder=DjangoJSONEncoder)
    return JsonResponse({'error': 'Invalid request method'})



@login_required
def payment_pdf(request, id):
    payment = get_object_or_404(payment_received, id=id)
    print(payment,"ppppppppppppppppp")
    company_name = payment.payment_received_customer.company_name
    deposit_to = payment.payment_received_customer.company_name

    payment_item_data = payment_received_item.objects.get(payment_received_id = id)

    
    context = {
        'deposit_name':company_name.upper(),
        'deposit_to':deposit_to.upper(),
        'payment':payment,
        'date':payment_item_data.invoicedate,
        'invoice_amt':payment_item_data.invoiceamount,
        'dueamount':payment_item_data.dueamount,
        'payment_item_data':payment_item_data
        }
    return render(request, template_path.payment_received_pdf,context)
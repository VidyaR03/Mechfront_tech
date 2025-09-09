from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db.models import Q
from datetime import datetime
from core.modules import template_path
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect,HttpResponse
from core.models import expense_vendor, customer, transporter,vendor,expense_item
import datetime
from django.views.decorators.csrf import csrf_protect
from decimal import Decimal
from core.modules.login.login import login_required
from django.db.models import Sum

 
@login_required
def expense_vendor_list(request):
    expense_vendor_list = expense_vendor.objects.all().order_by('-id')
    context = {
        'expense_vendor_list':expense_vendor_list
        }
    return render(request,template_path.expense_vendor_list,context)
 
 
# @login_required
#def add_expense_vendor_data(request):
#     if request.method == "GET":
#         vendor_name = vendor.objects.all()
#         dispatch_through = transporter.objects.all()
#         context ={
#             'vendor_name' : vendor_name,
#             'dispatch_through' : dispatch_through,
#             }
 
#         return render(request, template_path.add_expense_vendor_path, context)
#     elif request.method == "POST":
#         current_date1 = datetime.date.today()
#         context = {'current_date':current_date1}

#         expense_vendor_data = {
#             'expense_vendor_list':request.POST['date'],
#             'ex_vendor_name':vendor.objects.filter(id=request.POST['ex_vendor_name']).first(),
#             'ex_gst_number':request.POST['ex_gst_number'],
#             'ex_freight':request.POST['ex_freight'],
            
#         }
#         expense_vendor_object = expense_vendor(**expense_vendor_data)
#         expense_vendor_object.save()
#         latest_expense_vendor_id = expense_vendor.objects.latest('id')
#         i = 0
#         max_row = int(request.POST.get('iid[]',0))
#         while i <= max_row:
#             ex_item = expense_item(
#                 ex_item_code = request.POST.get(f'itemcode_{i}'),
#                 ex_description_goods = request.POST.get(f'item_{i}'),
#                 ex_hsn = request.POST.get(f'hsn_{i}'),
#                 ex_qantity = request.POST.get(f'qty_{i}'),
#                 ex_uom = request.POST.get(f'uom_{i}'),
#                 ex_unit_price = request.POST.get(f'rate_{i}'),
#                 ex_discount = request.POST.get(f'discount_{i}'),
#                 ex_tax_rate = request.POST.get(f'taxrate_{i}'),
#                 ex_tax_amount = request.POST.get(f'taxamt_{i}'),
#                 ex_total = request.POST.get(f'total_{i}'),
#                 ex_expense_id = latest_expense_vendor_id.id
#             )
 
#             ex_item.save()
#             i = i+1
#         return redirect('expense_vendor_list')
    
#########################



@login_required
def add_expense_vendor_data(request):
    if request.method == "GET":
        # Retrieve vendor and transporter data\
        current_date1 = datetime.date.today()

        vendor_name = vendor.objects.all()
        dispatch_through = transporter.objects.all()
        context = {
            'vendor_name': vendor_name,
            'dispatch_through': dispatch_through,
            'current_date':current_date1
        }
        return render(request, template_path.add_expense_vendor_path, context)
    
    elif request.method == "POST":
        # Handle the form submission

        # Assuming 'expense_vendor' is a model with fields similar to these
        expense_vendor_data = {
            'ex_invoice_date': request.POST['acc_date'],
            'ex_vendor_name': vendor.objects.filter(company_name=request.POST['ac_vendor']).first(),
            'ex_gst_number': request.POST['acc_gst'],
            'ex_freight': request.POST['freight'],
            'all_total' : request.POST['totalamt']
        }

        expense_vendor_object = expense_vendor(**expense_vendor_data)
        expense_vendor_object.save()

        latest_expense_vendor_id = expense_vendor.objects.latest('id')
        i = 0
        max_row_str = int(request.POST.get('iid[]'))
        # max_row = Decimal(max_row_str) if max_row_str and max_row_str.isdigit() else Decimal('0')

        # total_sum = Decimal('0')  # Initialize total_sum to calculate all_total

        while i <= max_row_str:
            ex_item = expense_item(
                ex_item_code=request.POST.get(f'itemcode_{i}'),
                ex_description_goods=request.POST.get(f'item_{i}'),
                ex_hsn=request.POST.get(f'hsn_{i}'),
                ex_qantity=request.POST.get(f'qty_{i}'),
                ex_uom=request.POST.get(f'uom_{i}'),
                ex_unit_price=request.POST.get(f'rate_{i}'),
                ex_discount=request.POST.get(f'discount_{i}'),
                ex_tax_rate=request.POST.get(f'taxrate_{i}'),
                ex_tax_amount=request.POST.get(f'taxamt_{i}'),
                ex_total=request.POST.get(f'total_{i}'),
                ex_expense_id=latest_expense_vendor_id.id
            )

            ex_item.save()
            i = i+1
        return redirect('expense_vendor_list')
    



from django.shortcuts import render, redirect, get_object_or_404
from decimal import Decimal
import datetime

# Assume these are your models




@login_required
def edit_expense_vendor_data(request, id):
    if request.method == "GET":
        expense_data = get_object_or_404(expense_vendor, id=id)
        vendor_name = expense_data.ex_vendor_name       
        all_dispatch_through = transporter.objects.all()
        all_customer_name = customer.objects.all()
        expense_item_data = expense_item.objects.filter(ex_expense_id = id)
        len_expense_item = len(expense_item_data)
        context ={ 
            'customer_name' : vendor_name,
            'all_customer_name':all_customer_name,
            'expense_item_data':expense_item_data,
            'expense_data': expense_data,
            'all_dispatch_through':all_dispatch_through,
            'len_expense_item':len_expense_item
            }

        return render(request, template_path.expense_vendor_edit_path, context)
    elif request.method == "POST":
        expense_data = get_object_or_404(expense_vendor, id=id)
        id = expense_data.id
        q_date_str = request.POST['acc_date']
        # q_date = datetime.strptime(q_date_str, '%d-%m-%Y').date()
        # q_date = datetime.datetime.strptime(q_date_str, '%d-%m-%Y').date()
        expense_data = {
            'id':id,
            'ex_invoice_date':request.POST['acc_date'],
            'ex_vendor_name': vendor.objects.filter(id=request.POST['ac_vendor']).first(),
            'ex_gst_number':request.POST['acc_gst'],
            'ex_freight':request.POST['acc_freight'],
          
        }
        expense_object = expense_vendor(**expense_data)
        expense_object.save()
        i = 1
        max_row = int(request.POST.get('iid[]',0))
        expense_item.objects.filter(ex_expense_id = id).delete()

        while i <= max_row:
            q_item = expense_item(
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
                q_quotation_id = id
            )
            q_item.save()
            i = i+1
        return redirect('expense_vendor_list')
    

@login_required
def delete_expense_vendor_data(request,expense_vendor_id):
    '''
    This view function for delete the specifice project.
    '''
    obj = get_object_or_404(expense_vendor, id=expense_vendor_id)

    obj.delete()
    return redirect('expense_vendor_list')

# @login_required
# def delete_expense_vendor_data(request, expense_vendor_id):
#     expense_vendor_obj = get_object_or_404(expense_vendor, id=expense_vendor_id)

#     if request.method == "POST":
#         # Delete associated expense items first
#         expense_item.objects.filter(ex_expense_id=expense_vendor_id).delete()

#         # Then delete the expense vendor object
#         expense_vendor_obj.delete()

#         return redirect('expense_vendor_list')  # Redirect to the expense vendor list view

#     # Optionally, you can render a confirmation page for GET requests
#     return render(request, 'confirm_expense_vendor_delete.html', {'expense_vendor': expense_vendor_obj})


import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt  # Use this decorator if CSRF protection is enabled
@login_required
def getitemscodedetails_1(request):
    if request.method == 'POST':
        try:
            # Assuming the data is sent as JSON
            data = json.loads(request.body)
            item_code = data.get('itemCode')

            # print(item_code)
            item_details = expense_item.objects.filter(item_code__startswith=item_code)
            itemCode = [i.ex_item_code for i in item_details]
            # print("PPPPPPPP",itemCode)
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
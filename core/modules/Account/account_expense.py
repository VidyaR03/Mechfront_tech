from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db.models import Q
from datetime import datetime
from core.modules import template_path
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect,HttpResponse
from core.models import Account_Expense, Account_Expense_Item, vendor, transporter, inventory
from core.modules.login.login import login_required


# @login_required
def account_expense_list_view(request):
    accexp_list = Account_Expense.objects.all().order_by('-ae_invoice_date')
    n = 0
    lengt_itr = len(accexp_list)
    for i in accexp_list:
        i.serial_no = lengt_itr
        lengt_itr -= 1
        # i.serial_no = n
        # n += 1
        
    context = {
        'accexp_list':accexp_list
        }
    return render(request,template_path.acc_expense_list,context)


# @login_required
def add_account_expense_data(request):
    if request.method == "GET":
        vendor_name = vendor.objects.all()
        dispatch_through = transporter.objects.all().order_by('name')
        item_data = inventory.objects.all()
        current_date = datetime.today().strftime('%d-%m-%Y')
        context ={ 
            'vendor_name' : vendor_name,
            'dispatch_through' : dispatch_through,
            'item_data': item_data,
            'current_date':current_date
            }

        return render(request, template_path.add_account_expense, context)
    elif request.method == "POST":
        q_date_str = request.POST['invoice_date']
        q_date = datetime.strptime(q_date_str, '%d-%m-%Y').date()
        expense_data = {
            'ae_invoice_date':q_date,
            'ae_vendor_name':vendor.objects.filter(id=request.POST['vendor_Name']).first(),
            'ae_gst_number':request.POST['acc_gst'],
            'ae_freight':request.POST['freight'],
            'ae_sub_total':request.POST['subtotal'],
            'ae_cgstper':request.POST['cgstper'],
            'ae_cgstval':request.POST['cgst'],
            'ae_sgstper':request.POST['sgstper'],
            'ae_sgstval':request.POST['sgst'],
            'ae_igstper':request.POST['igstper'],
            'ae_igstval':request.POST['igst'],
            'ae_adjustment':request.POST['adjustment'],
            'ae_sale_of_good':request.POST['sale_of_good'],
            'ae_note':request.POST['note'],
            'all_total':request.POST['all_total'],
            'ae_cost_center':request.POST['ae_cost_center'],
            'ae_upload_file':request.FILES.get('ae_upload_file'),
            'ae_due_amount':request.POST.get('all_total'),
            'ae_invoice_no':request.POST.get('ae_invoice_no'),





           
        }
        expense_object = Account_Expense(**expense_data)
        expense_object.save()
        # print(expense_object)
        latest_quotation_id = Account_Expense.objects.latest('id')
        i = 0
        max_row = int(request.POST.get('iid[]'))
        while i <= max_row:
            ae_item = Account_Expense_Item(
                ae_item_code = request.POST.get(f'itemcode_{i}'),
                ae_description_goods = request.POST.get(f'item_{i}'),
                ae_hsn = request.POST.get(f'hsn_{i}'),
                ae_qantity = request.POST.get(f'qty_{i}'),
                ae_uom = request.POST.get(f'uom_{i}'),
                ae_unit_price = request.POST.get(f'rate_{i}'),
                ae_discount = request.POST.get(f'discount_{i}',0),
                ae_tax_rate = request.POST.get(f'taxrate_{i}'),
                ae_tax_amount = request.POST.get(f'taxamt_{i}'),
                ae_total = request.POST.get(f'total_{i}'),
                ae_quotation_id = latest_quotation_id.id
            )
            # print(ae_item)

            ae_item.save()
            i = i+1
        return redirect('accexpense_list')
    

# @login_required
def edit_account_expense(request, id):
    if request.method == "GET":
        account_expense_data = get_object_or_404(Account_Expense, id=id)
        vendor_name = account_expense_data.ae_vendor_name
        # quotation_data = quotation.objects.filter(id = id).first()
        # customer_name = customer.objects.filter(id = quotation_data.q_customer_name_id.id)
        # dispatch_through = transporter.objects.filter(id = quotation_data.q_dispatch_id.id)
        item_data = inventory.objects.all()
        all_dispatch_through = transporter.objects.all().order_by('name')
        all_vendor_name = vendor.objects.all()
        account_expense_item_data = Account_Expense_Item.objects.filter(ae_quotation_id = id)
        len_quotation_item = len(account_expense_item_data)
        context ={ 
            'vendor_name' : vendor_name,
            'all_vendor_name':all_vendor_name,
            'item_data': item_data,
            'account_expense_item_data':account_expense_item_data,
            'account_expense_data': account_expense_data,
            'all_dispatch_through':all_dispatch_through,
            'len_quotation_item':len_quotation_item
            }

        return render(request, template_path.edit_account_expense, context)
    elif request.method == "POST":
        account_expense_data = get_object_or_404(Account_Expense, id=id)
        id = account_expense_data.id
        ae_invoice_date = request.POST['invoice_date']

        total_due = float(account_expense_data.all_total) - float(account_expense_data.ae_due_amount) + float(request.POST.get('totalamt',0))
       
        ae_date = datetime.strptime(ae_invoice_date, '%d-%m-%Y').date()
        account_expense_data = {
            'id':id,
            'ae_invoice_date':ae_date,
            'ae_vendor_name':vendor.objects.filter(id=request.POST['vendor_Name']).first(),
            'ae_gst_number':request.POST['ae_gst_number'],
            'ae_freight': request.POST['freight'],
            'ae_sub_total':request.POST['subtotal'],
            'ae_cgstper':request.POST['cgstper'].replace("%",""),
            'ae_cgstval':request.POST['cgst'],
            'ae_sgstper':request.POST['sgstper'].replace("%",""),
            'ae_sgstval':request.POST['sgst'],
            'ae_igstper':request.POST['igstper'].replace("%",""),
            'ae_igstval':request.POST['igst'],
            'ae_adjustment':request.POST['adjustment'],
            'ae_sale_of_good':request.POST['sale_of_good'],
            'ae_note':request.POST['note'],
            'all_total':request.POST['totalamt'],
            'ae_cost_center':request.POST['ae_cost_center'],
            'ae_upload_file':request.FILES.get('ae_upload_file'),
            'ae_due_amount':total_due,
            'ae_invoice_no':request.POST.get('ae_invoice_no'),


           
        }
        acc_expense_object = Account_Expense(**account_expense_data)
        acc_expense_object.save()
        i = 1
        max_row = int(request.POST.get('iid[]'))
        Account_Expense_Item.objects.filter(ae_quotation_id = id).delete()
        for i in range(1, max_row + 1):
            item_code = request.POST.get(f'itemcode_{i}')
            if item_code:  # Ensure item_code is not empty or None
                ae_item = Account_Expense_Item(
                    ae_item_code = request.POST.get(f'itemcode_{i}'),
                    ae_description_goods = request.POST.get(f'item_{i}'),
                    ae_hsn = request.POST.get(f'hsn_{i}'),
                    ae_qantity = request.POST.get(f'qty_{i}'),
                    ae_uom = request.POST.get(f'uom_{i}'),
                    ae_unit_price = request.POST.get(f'rate_{i}'),
                    ae_discount = request.POST.get(f'discount_{i}',0),
                    ae_tax_rate = request.POST.get(f'taxrate_{i}'),
                    ae_tax_amount = request.POST.get(f'taxamt_{i}'),
                    ae_total = request.POST.get(f'total_{i}'),
                    ae_quotation_id = id
                )
                ae_item.save()
        return redirect('accexpense_list')
    

@login_required
@csrf_exempt
@require_POST
def acget_item_code_details(request):
    name_starts_with = request.POST.get('name_startsWith', '')
    # items_details = request.POST.getlist('itemsdetails[]', '')
    items = inventory.objects.filter(item_code__istartswith=name_starts_with)

    data = []
    for item in items:
        item_data = (
            f"{item.item_code}|{item.inventory_name}|{item.hsn}|1|"
            f"{item.default_discount}|{item.intrastate_gst}|{item.interstate_gst}|{item.sales_rate}|{item.sku}|{item.units}"
        )
        data.append(item_data)
    return JsonResponse(data, safe=False)


# @login_required
# def delete_accexpense_data(request, id):
#     # Get the customer instance based on the provided ID
#     quotation_instance = get_object_or_404(Account_Expense, id=id)    
#     quotation_item_instance = Account_Expense_Item.objects.filter(ae_quotation_id = id)
#     # if request.method == 'POST':
#     # quotation_instance.delete()
#     # quotation_item_instance.delete()
#     return redirect('accexpense_list')  # Redirect to a success page or customer list


from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

def delete_accexpense_data(request, id):
    expense = get_object_or_404(Account_Expense, id=id)

    if request.method == "POST":
        # Delete related items first (if not using CASCADE in models)
        Account_Expense_Item.objects.filter(ae_quotation_id=expense.id).delete()

        # Delete expense record
        expense.delete()

        messages.success(request, "Account expense deleted successfully.")
        return redirect('accexpense_list')

    # If GET request, show confirmation page
    return render(request, template_path.acc_expense_list, {'expense': expense})


import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@login_required
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



def purchase_get_item_code_details(request):
    name_starts_with = request.POST.get('name_startsWith', '')
    items = inventory.objects.filter(item_code__istartswith=name_starts_with).order_by("item_code")
    data = []
    for item in items:
        units = item.units if item.units else ''
        item_data = (
            f"{item.item_code}|{item.inventory_name}|{item.hsn}|{item.opening_stock_quantity}|"
            f"{item.default_discount}|{item.purchase_rate}|{item.sku}|{units}"
        )
        data.append(item_data)
    return JsonResponse(data, safe=False)

def autocomplete_vendor_name(request):
    term = request.GET.get('term', '')
    vendors= vendor.objects.filter(contact_person__icontains=term)
    results = [{'id': vendor.id, 'label': vendor.contact_person, 'value': vendor.contact_person} for vendor in vendors]
    return JsonResponse(results, safe=False)



@login_required
def show_acpdf(request, id):
    quo = Account_Expense.objects.filter(id=id).first()

    context={
        'quo':quo,
        
    }


    return render(request, template_path.quo_pdf,context)


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db.models import Q
from datetime import datetime
from core.modules import template_path
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect,HttpResponse
from core.models import Invoice, acc_expense_items, acc_expense, transporter, inventory, godown,vendor


def expense_list_view(request):
    acc_expense_list = acc_expense.objects.all().order_by('-id')
    context = {
        'acc_expense_list':acc_expense_list
        }
    return render(request,template_path.expense_new_list,context)



def add_expense_data(request):
    if request.method == "GET":
        vendor_name = vendor.objects.all()
        dispatch_through = transporter.objects.all()
        item_data = inventory.objects.all()
        godown_name = godown.objects.all()

        context ={ 
            'vendor_name' : vendor_name,
            'dispatch_through' : dispatch_through,
            'item_data': item_data,
            'godown_name': godown_name,
            }

        return render(request, template_path.acc_expense_new, context)
    elif request.method == "POST":
       
        invoice_data = {
            'ac_vendor': vendor.objects.filter(company_name=request.POST.get('ac_vendor')).first(),
            'acc_date':  request.POST.get['acc_date'],
            'acc_gst':request.POST.get['acc_gst'],
            'acc_freight':request.POST.get['acc_freight'],
            
        }
        Invoice_object = acc_expense(**invoice_data)
        Invoice_object.save()
        latest_expense_id = acc_expense.objects.latest('id')
        i = 0
        max_row = int(request.POST.get('iid[]',0))
        while i <= max_row:
             expense_item = acc_expense_items(
                 expense_item_code = request.POST.get(f'itemcode_{i}'),
                 expense_description_goods = request.POST.get(f'item_{i}'),
                 expense_hsn = request.POST.get(f'hsn_{i}'),
                 expense_qantity = request.POST.get(f'qty_{i}'),
                 expense_uom = request.POST.get(f'uom_{i}'),
                 expense_unit_price = request.POST.get(f'rate_{i}'),
                 expense_discount = request.POST.get(f'discount_{i}'),
                 expense_tax_rate = request.POST.get(f'taxrate_{i}'),
                 expense_tax_amount = request.POST.get(f'taxamt_{i}'),
                 expense_total = request.POST.get(f'total_{i}'),
                expense_id = latest_expense_id.id
            )
        expense_item.save()
        i = i+1
        return redirect('expense_vendor_list_new')
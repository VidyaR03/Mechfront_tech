from django.db.models import Q
from core.models import inventory,godown,customer,vendor
from core.modules import template_path
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect,HttpResponse
from datetime import datetime
from django.contrib import messages

from core.modules.login.login import login_required


@login_required
def inventory_list(request):
    # try:
        inventory_list = inventory.objects.all().order_by('-id')
        godown_list = godown.objects.all()

        
        context = {
            "inventory_list": inventory_list,
            'godown_list':godown_list
        }
        return render(request, template_path.inventory_list, context)
    # except Exception as e:
    #     return HttpResponse(e)


@login_required
def inventory_overview(request, id):
    # try:
        inventory_entity_data = inventory.objects.filter(id = id).first()
        customer_data = customer.objects.all()
        
        context = {
            "inventory_entity_data": inventory_entity_data,
            'customer_data':customer_data
        }
        return render(request, template_path.inventory_entity_data, context)


@login_required
def inventory_data_add(request):
    current_date = datetime.now().date()
    godown_name = godown.objects.all()
    company_name = vendor.objects.all()

    context = {'current_date': current_date,'godown_name':godown_name , 'company_name':company_name}  # Initialize context


    try:
        if request.method == "POST":
            # print(request.POST['default_discount'],"&&&&&&")
            if not request.POST['default_discount']:
                 default_discount = 0.0
            else:
                 default_discount = request.POST['default_discount']
                 
            inventory_data = {
            'inventory_name': request.POST['inventory_name'],
            'item_code': request.POST['item_code'],
            'units': request.POST['units'],
            'type': request.POST['type'],
            'tax_type': request.POST['tax_type'],
            # 'intrastate_gst': request.POST['intrastate_gst'],
            # 'interstate_gst': request.POST['interstate_gst'],
            'hsn': request.POST['hsn'],
            'sku': request.POST['sku'],
            'default_discount': default_discount,
            'sales_rate': request.POST['sale_rate'],
            'sales': request.POST['sales_account'],
            'sales_information_description': request.POST['sale_description'],
            # 'sales_information': request.POST['sales_information'],
            'purchase_rate': request.POST['purchase_rate'],
            'purchase': request.POST['purchase_account'],
            'purchase_information_description': request.POST['purchase_description'],
            'opening_stock_quantity':request.POST['opening_stock'],
            'opening_rate':request.POST['opening_rate'],
            # 'stock_account':request.POST['stock_account'],
            'date': current_date,
            # 'gst_option': request.POST['gst_option'],
            'godown_name_old':request.POST['godown'],
            # 'Tax_rate': request.POST['Tax_rate'],
            # 'inventory_godown': request.POST['inv_godown'],
            'inventory_godown':godown.objects.filter(id=request.POST['inv_godown']).first(),
            'vendor_name':vendor.objects.filter(id=request.POST['company_name']).first(),






            }
            inventory_object = inventory(**inventory_data)
            inventory_object.save()
            messages.success(request, 'Inventory created successfully.')

            return redirect("inventory_list_data")
        return render(request, template_path.add_inventory,context)
    except Exception as e:
        # print("0000",e)
        return HttpResponse(e)
    
@login_required
def inventory_edit(request, id):
    inventory_item = get_object_or_404(inventory, id=id)
    godown_name = godown.objects.all()
    company_name = vendor.objects.all()

    if request.method == 'POST':
        try:
            # Vendor selection
            vendor_id = request.POST.get('company_name')
            vendor_obj = vendor.objects.filter(id=vendor_id).first() if vendor_id else None

            # Godown selection
            inv_godown_id = request.POST.get('inv_godown')
            inv_godown_obj = godown.objects.filter(id=inv_godown_id).first() if inv_godown_id else None

            # Update fields
            inventory_item.inventory_name = request.POST['inventory_name']
            inventory_item.item_code = request.POST['item_code']
            inventory_item.units = request.POST['unit']
            inventory_item.type = request.POST['good_type']
            inventory_item.tax_type = request.POST['tax_type']
            inventory_item.hsn = request.POST['hsn']
            inventory_item.sku = request.POST['sku']
            inventory_item.default_discount = request.POST.get('default_discount') or 0
            inventory_item.sales_rate = request.POST['sale_rate']
            inventory_item.sales = request.POST['sales_account']
            inventory_item.sales_information_description = request.POST['sale_description']
            inventory_item.purchase_rate = request.POST['purchase_rate']
            inventory_item.purchase = request.POST['purchase_account']
            inventory_item.purchase_information_description = request.POST['purchase_description']
            inventory_item.opening_stock_quantity = request.POST['opening_stock']
            inventory_item.opening_rate = request.POST['opening_rate']
            inventory_item.vendor_name = vendor_obj
            inventory_item.godown_name_old = request.POST.get('godown') or ''
            inventory_item.inventory_godown = inv_godown_obj

            # Save changes
            inventory_item.save()
            messages.success(request, 'Inventory Updated successfully.')
            return redirect("inventory_list_data")

        except Exception as e:
            messages.error(request, f"Error updating inventory: {e}")

    context = {
        "inventory_item": inventory_item,
        'godown_name': godown_name,
        'company_name': company_name,
        "is_trackable": True if inventory_item.opening_stock_quantity != "0" else False,
        "is_purchase_information": True if inventory_item.purchase_rate != "0" else False

    }
    return render(request, template_path.edit_inventory, context)


# def inventory_data_edit(request, id):
#     try:
#         inventory_item = get_object_or_404(inventory, pk=id)
#         if request.method == "POST":  # Update the inventory item with the new data
#             inventory_item.pk = id
#             inventory_item.inventory_name = request.POST['inventory_name'] 
#             inventory_item.item_code = request.POST['item_code']
#             inventory_item.units = request.POST['units']
#             inventory_item.type = request.POST['type']
#             inventory_item.tax_type = request.POST['tax_type']
#             inventory_item.intrastate_gst = request.POST['intrastate_gst']
#             inventory_item.interstate_gst = request.POST['interstate_gst']
#             inventory_item.hsn = request.POST['hsn']
#             inventory_item.sku = request.POST['sku']
#             inventory_item.default_discount = request.POST['default_discount']
#             inventory_item.sales_rate = request.POST['sales_rate']
#             inventory_item.sales = request.POST['sales']
#             inventory_item.sales_information_description = request.POST['sales_information_description']
#             inventory_item.purchase_information = request.POST['purchase_information']
#             inventory_item.purchase_rate = request.POST['purchase_rate']
#             inventory_item.purchase = request.POST['purchase']
#             inventory_item.purchase_information_description = request.POST['purchase_information_description']
#             inventory_item.save()  # Save the updated inventory item
#             return redirect("inventory_list")
#         context = {
#             "inventory_item": inventory_item
#         }
#         return render(request, template_path.edit_inventory)  # Render the form to edit the inventory item
#     except Exception as e:
#         return HttpResponse(e)


@login_required
def delete_inentory_item(request,id):
    '''
    This view function for delete the inventory item.
    '''
    obj = get_object_or_404(inventory, id=id)

    obj.delete()
    messages.success(request, 'Inventory Deleted successfully.')

    return redirect("inventory_list_data")



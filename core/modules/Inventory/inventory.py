from django.db.models import Q
from core.models import inventory,godown,customer,vendor,Invoice,invoice_items, Purchase_Invoice_items, Purchase_Invoice
from core.modules import template_path
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect,HttpResponse
from datetime import datetime
from django.contrib import messages

from core.modules.login.login import login_required
from datetime import date
from django.utils import timezone

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




def parse_date(date_str):
    for fmt in ('%B %d, %Y', '%Y-%m-%d'):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Date format not recognized: {date_str}")

def get_last_purchase_unit(item_code, start_date, end_date):
    latest_purchase_invoice = Purchase_Invoice.objects.filter(
        id__in=Purchase_Invoice_items.objects.filter(
            purchase_invoice_item_code=item_code
        ).values_list('purchase_invoice_id', flat=True),
        purchase_invoice_date__range=(start_date, end_date)
    ).order_by('-purchase_invoice_date').first()

    if not latest_purchase_invoice:
        print("No latest purchase invoice found.")
        return None

    print(latest_purchase_invoice.id, "latest_purchase_invoice.id")

    purchase_invoice_items_data = Purchase_Invoice_items.objects.filter(
        purchase_invoice_item_code=item_code,
        purchase_invoice_id=latest_purchase_invoice.id
    ).last()

    if purchase_invoice_items_data:
        # print(purchase_invoice_items_data.purchase_invoice_uom, "purchase_invoice_items_data.purchase_invoice_uom")
        return purchase_invoice_items_data.purchase_invoice_uom
    else:
        print("No purchase invoice item data found.")
        return None






def inventory_overview(request, id):
    inventory_entity_data = get_object_or_404(inventory, id=id)
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    opening_stock_quantity_os = request.GET.get('os')

    if start_date_str and end_date_str:
        # Parse to date objects
        start_date = parse_date(start_date_str)
        end_date = parse_date(end_date_str)
    else:
        # Default to full range
        start_date = date(2000, 1, 1)
        end_date = timezone.now().date()

    try:
        opening_stock_quantity = float(inventory_entity_data.opening_stock_quantity)
    except ValueError:
        opening_stock_quantity = 0  # Handle invalid data gracefully

    if opening_stock_quantity_os:
        try:
            opening_stock_quantity = float(opening_stock_quantity_os)
        except ValueError:
            opening_stock_quantity = 0

    current_stock = opening_stock_quantity
    invoices = Invoice.objects.filter(
    id__in=invoice_items.objects.filter(invoice_item_code=inventory_entity_data.item_code).values_list('invoice_id', flat=True),
    invoice_date__range=(start_date, end_date)
    )

    invoice_items_data = invoice_items.objects.filter(
        invoice_item_code=inventory_entity_data.item_code,
        invoice_id__in=invoices.values_list('id', flat=True)
    )


    
    total_quantity = sum(float(item.invoice_qantity) for item in invoice_items_data)
 
    combined_data = []
    invoice_data = []
    purchase_invoice_data = []

    # Process sales data
    for invoice in invoices:
        try:

            items = invoice_items.objects.filter(
            invoice_item_code=inventory_entity_data.item_code,
            invoice_id=invoice.id)

            for item in items:
                quantity = float(item.invoice_qantity)
                total_rate = item.invoice_unit_price
                average_rate = total_rate

                invoice_data.append({
                    'invoice': invoice,
                    'total_quantity_used': quantity,
                    'average_rate': average_rate,
                    'total_quantity':total_quantity,
                    # 'unit':inventory_entity_data.units,
                    'unit': get_last_purchase_unit(inventory_entity_data.item_code, start_date,end_date) or inventory_entity_data.units,
                    'balance': current_stock,
                })
                combined_data.append({
                    'particular': 'Sales',
                    'date': invoice.invoice_date,
                    'invoice_no': invoice.formatted_id,
                    'customer_vendor': invoice.invoice_customer_name.customer,
                    'rate': average_rate,
                    # 'unit': inventory_entity_data.units,
                    'unit': get_last_purchase_unit(inventory_entity_data.item_code, start_date,end_date) or inventory_entity_data.units,
                    'quantity': quantity,  # Keep original quantity
                    'balance': current_stock  # Add current balance
                })

        except Exception as e:
            print(f"Error processing invoice {invoice.id}: {e}")
            # Handle the error as needed, e.g., log it or set a default value
            continue
    
    # Process purchase data
    purchase_invoices = Purchase_Invoice.objects.filter(
    id__in=Purchase_Invoice_items.objects.filter(
        purchase_invoice_item_code=inventory_entity_data.item_code
    ).values_list('purchase_invoice_id', flat=True),
    purchase_invoice_date__range=(start_date, end_date)
    )

    purchase_invoice_items_data = Purchase_Invoice_items.objects.filter(
        purchase_invoice_item_code=inventory_entity_data.item_code,
        purchase_invoice_id__in=purchase_invoices.values_list('id', flat=True)
    )
    for purchase_invoice in purchase_invoices:
        items =  Purchase_Invoice_items.objects.filter(
        purchase_invoice_item_code=inventory_entity_data.item_code,
        purchase_invoice_id=purchase_invoice.id
        )

        for item in items:
            total_purchase_quantity = float(item.purchase_invoice_qantity)
            total_rate = item.purchase_invoice_unit_price
            average_rate = total_rate

            purchase_invoice_data.append({
                'purchase_invoice': purchase_invoice,
                'invoice_date': purchase_invoice.purchase_invoice_date,
                'voucher': 'Bill',
                'vendor': purchase_invoice.purchase_invoice_vendor_name,
                'quantity': total_purchase_quantity,
                'unit':item.purchase_invoice_uom,
                'rate': average_rate,
                'balance': current_stock  

            })

            combined_data.append({
                'particular': 'Purchase',
                'date': purchase_invoice.purchase_invoice_date,
                'customer_vendor': purchase_invoice.purchase_invoice_vendor_name.company_name,
                'rate': average_rate,
                'unit': item.purchase_invoice_uom,
                'quantity': total_purchase_quantity,  # Keep original quantity
                'balance': current_stock  # Add current balance
            })

    # Sort combined data by date and priority ('Sales' comes after 'Purchase')
    combined_data = sorted(combined_data, key=lambda x: (x['date'], 0 if x['particular'] == 'Purchase' else 1))

    # Recalculate balance for each entry
    balance_stock = opening_stock_quantity
    for entry in combined_data:
        if entry['particular'] == 'Purchase':
            # Add quantity to balance for purchases
            balance_stock += float(entry['quantity'])
        elif entry['particular'] == 'Sales':
            # Subtract quantity from balance for sales
            balance_stock -= float(entry['quantity'])

        # Update the new balance in the entry without changing the original quantity field
        entry['balance'] = balance_stock

    available_quantity = balance_stock  # Final balance after processing all transactions

    context = {
        "inventory_entity_data": inventory_entity_data,
        "gstEnabled": True,
        "invoice_data":invoice_data,
        "purchase_invoice_data": purchase_invoice_data,
        "combined_data": combined_data,
        "available_quantity": available_quantity,
        "opening_stock_quantity": opening_stock_quantity,
        "total_quantity": total_quantity,
        "purchase_total_quantity": sum(float(item.purchase_invoice_qantity) for item in purchase_invoice_items_data),
       
    }
    return render(request, template_path.inventory_entity_data, context)



# @login_required
# def inventory_overview(request, id):
#     # try:
#         inventory_entity_data = inventory.objects.filter(id = id).first()
#         customer_data = customer.objects.all()
        
#         context = {
#             "inventory_entity_data": inventory_entity_data,
#             'customer_data':customer_data
#         }
#         return render(request, template_path.inventory_entity_data, context)


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



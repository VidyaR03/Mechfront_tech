from django.shortcuts import render, redirect, get_object_or_404
from core.models import vendor
from core.modules import template_path
import re
from django.db.models import Q
from django.db import IntegrityError
from django.http import HttpResponse

from core.modules.login.login import login_required
from django.contrib import messages



gst_no_pattern = re.compile(r'^([0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}[Z]{1}[0-9A-Z]{1})$')



import pdb

@login_required
def add_vendor(request):
    # pdb.set_trace()
    if request.method == 'POST':
        vendor_data = {
            'gender' : request.POST['gender'],
            'contact_person': request.POST['contact_person'],
            'vendor_email': request.POST['vendor_email'],
            'company_name': request.POST['company_name'],
            'phone': request.POST['phone'],           
            'display_name': request.POST['display_name'],
            'website': request.POST['website'],
            'mobile': request.POST['mobile'],
            
            'gst_treatment': request.POST['gst_treatment'],
            'gst_number': request.POST['gst_number'],
            'state': request.POST['state'],
            'balance': request.POST['balance'],
            'pan_number': request.POST['pan_number'],
                        
            'delivery_company_name': request.POST['delivery_company_name'],
            'street': request.POST['street'],
            'city': request.POST['city'],
            'delivery_state': request.POST['delivery_state'],
            'pincode': request.POST['pincode'],
            'gst_uin': request.POST['gst_uin'],
            'contact_number': request.POST['contact_number'],

            'vendor_company_name': request.POST['vendor_company_name'],
            'vendor_street': request.POST['vendor_street'],
            'vendor_city': request.POST['vendor_city'],
            'vendor_state': request.POST['vendor_state'],
            'vendor_pincode': request.POST['vendor_pincode'],
            'vendor_gst_uin': request.POST['vendor_gst_uin'],
            'vendor_contact_number': request.POST['vendor_contact_number'],

            'bank_name': request.POST['bank_name'],
            'account_number': request.POST['account_number'],
            'branch_name': request.POST['branch_name'],
            'ifsc_code': request.POST['ifsc_code'],
            'licence_no': request.POST['licence_no'],
        }

        gst_number = request.POST['gst_number']
        if not validate_gst_number(gst_number):
            error_message = "Enter a valid GST number (e.g., 12ABCDE1234F1Z5)."
            return render(request, template_path.Vendor_path, {'error_message': error_message})

        try:
            # Check for existing vendor with the same GST number
            # existing_vendor = vendor.objects.filter(gst_number=gst_number).first()
            # if existing_vendor:
            #     error_message = "GST number already exists. Please use a different GST number."
            #     return render(request, template_path.Vendor_path, {'error_message': error_message})

            # Create a new vendor instance and save it
            vendor_instance = vendor(**vendor_data)
            vendor_instance.save()
            messages.success(request, 'Vendor created successfully.')

            return redirect('fn_vendor_List_View')  # Redirect to vendor list view upon successful creation
        except IntegrityError as e:
            # Handle IntegrityError (if any)
            return HttpResponse(f"Error: {e}")

    return render(request, template_path.Vendor_path)


def validate_gst_number(gst_number):
    if gst_number.strip() == '':
        return True  # Allow empty value

    # Update the regular expression to Python syntax
    gst_no_pattern = re.compile(r'^([0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}[Z]{1}[0-9A-Z]{1})$')
    return bool(gst_no_pattern.match(gst_number))


@login_required
def fn_vendor_List_View(request):
    form = vendor.objects.all().order_by('-id')
    context = {'form':form}
    return render(request,template_path.Vendor_list,context)


@login_required
def edit_vendor(request, vendor_id):
    # Fetch the customer instance based on the customer_id
    vendor_instance = get_object_or_404(vendor, id=vendor_id)

    if request.method == 'POST':
        vendor_instance.gender = request.POST['gender']
        vendor_instance.contact_person = request.POST['contact_person']
        vendor_instance.vendor_email = request.POST['vendor_email']
        vendor_instance.company_name = request.POST['company_name']
        vendor_instance.phone = request.POST['phone']
        vendor_instance.display_name = request.POST['display_name']
        vendor_instance.website = request.POST['website']
        vendor_instance.mobile = request.POST['mobile']

        vendor_instance.gst_treatment = request.POST['gst_treatment']
        vendor_instance.gst_number = request.POST['gst_number']
        vendor_instance.state = request.POST['state']
        vendor_instance.balance = request.POST['balance']
        vendor_instance.pan_number = request.POST['pan_number']
        
        vendor_instance.delivery_company_name = request.POST['delivery_company_name']
        vendor_instance.street = request.POST['street']
        vendor_instance.city = request.POST['city']
        vendor_instance.delivery_state = request.POST['delivery_state']
        vendor_instance.pincode = request.POST['pincode']
        vendor_instance.gst_uin = request.POST['gst_uin']
        vendor_instance.contact_number = request.POST['contact_number']
  
        vendor_instance.vendor_company_name = request.POST['vendor_company_name']
        vendor_instance.vendor_street = request.POST['vendor_street']
        vendor_instance.vendor_city = request.POST['vendor_city']
        vendor_instance.vendor_state = request.POST['vendor_state']
        vendor_instance.vendor_pincode = request.POST['vendor_pincode']
        vendor_instance.vendor_gst_uin = request.POST['vendor_gst_uin']
        vendor_instance.vendor_contact_number = request.POST['vendor_contact_number']
        
        vendor_instance.bank_name = request.POST['bank_name']
        vendor_instance.account_number = request.POST['account_number']
        vendor_instance.branch_name = request.POST['branch_name']
        vendor_instance.ifsc_code = request.POST['ifsc_code']        
        vendor_instance.licence_no = request.POST['licence_no']        

        vendor_instance.save()
        messages.success(request, 'Vendor Updated successfully.')

        # Redirect to the customer details page or any other appropriate page
        return redirect('fn_vendor_List_View')

    # Render the edit customer form with the existing customer data
    return render(request, template_path.Editvendor_path, {'vendor_instance': vendor_instance})



@login_required
def delete_vendor(request,vendor_id):
    '''
    This view function for delete the specifice project.
    '''
    obj = get_object_or_404(vendor, id=vendor_id)
    messages.error(request, 'Vendor Deleted.')

    obj.delete()
    return redirect('fn_vendor_List_View')


@login_required
def show_vendor(request,id):
    vendor_billed_amount = vendor.objects.filter(id=id).first()
    context = {
        'vendor_amount':vendor_billed_amount.receive_amount,
        'date' : vendor_billed_amount.due_date,
        'com':vendor_billed_amount.company_name,
        'vendor':vendor_billed_amount
    }
    return render(request, template_path.show_vendor, context)
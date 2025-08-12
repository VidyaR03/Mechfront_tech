from django.shortcuts import render, redirect, get_object_or_404
from core.models import customer,Leads
from core.modules import template_path
from django.http import HttpResponse
from django.db import IntegrityError
import re
from django.db.models import Q

from core.modules.login.login import login_required
from django.contrib import messages



gst_no_pattern = re.compile(r'^([0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}[Z]{1}[0-9A-Z]{1})$')



@login_required
def add_customer(request):
   
    associated_lead_ids = customer.objects.values_list('lead_id', flat=True)
    # Convert associated_lead_ids to a list of strings (if they are not already)
    associated_lead_ids = list(map(str, associated_lead_ids))

    leads = Leads.objects.exclude(id__in=associated_lead_ids)
    
   
    if request.method == 'POST':
        customer_data = {
            'gender' : request.POST['gender'],
            'customer': request.POST['customer'],
            'cust_email': request.POST['cust_email'],
            'company_name': request.POST['company_name'],
            'phone': request.POST['phone'],           
            'display_name': request.POST['display_name'],
            'website': request.POST['website'],
            'mobile': request.POST['mobile'],
            'lead_id':request.POST['lead_id'],
            
            'gst_treatment': request.POST['gst_treatment'],
            'gst_number': request.POST['gst_number'],
            
            'state': request.POST['state'],
            'balance': request.POST['balance'],
            'pan_number': request.POST['pan_number'],
            'discount': request.POST['discount'],
            'credit_limit': request.POST['credit_limit'],
            
            'attention': request.POST['attention'],
            'street': request.POST['street'],
            'city': request.POST['city'],
            'com_state': request.POST['com_state'],
            'pincode': request.POST['pincode'],
            'gst_uin': request.POST['gst_uin'],
            'contact_number': request.POST['contact_number'],

            'shipping_1_attention': request.POST['shipping_1_attention'],
            'shipping_1_street': request.POST['shipping_1_street'],
            'shipping_1_city': request.POST['shipping_1_city'],
            'shipping_1_state': request.POST['shipping_1_state'],
            'shipping_1_pincode': request.POST['shipping_1_pincode'],
            'shipping_1_gst_uin': request.POST['shipping_1_gst_uin'],
            'shipping_1_contact_number': request.POST['shipping_1_contact_number'],
            
            'shipping_2_attention': request.POST['shipping_2_attention'],
            'shipping_2_street': request.POST['shipping_2_street'],
            'shipping_2_city': request.POST['shipping_2_city'],
            'shipping_2_state': request.POST['shipping_2_state'],
            'shipping_2_pincode': request.POST['shipping_2_pincode'],
            'shipping_2_gst_uin': request.POST['shipping_2_gst_uin'],
            'shipping_2_contact_number': request.POST['shipping_2_contact_number'],
           
            'shipping_3_attention': request.POST['shipping_3_attention'],
            'shipping_3_street': request.POST['shipping_3_street'],
            'shipping_3_city': request.POST['shipping_3_city'],
            'shipping_3_state': request.POST['shipping_3_state'],
            'shipping_3_pincode': request.POST['shipping_3_pincode'],
            'shipping_3_gst_uin': request.POST['shipping_3_gst_uin'],
            'shipping_3_contact_number': request.POST['shipping_3_contact_number'],

            'shipping_4_attention': request.POST['shipping_4_attention'],
            'shipping_4_street': request.POST['shipping_4_street'],
            'shipping_4_city': request.POST['shipping_4_city'],
            'shipping_4_state': request.POST['shipping_4_state'],
            'shipping_4_pincode': request.POST['shipping_4_pincode'],
            'shipping_4_gst_uin': request.POST['shipping_4_gst_uin'],
            'shipping_4_contact_number': request.POST['shipping_4_contact_number'],
           
            'bank_name': request.POST['bank_name'],
            'account_number': request.POST['account_number'],
            'branch_name': request.POST['branch_name'],
            'ifsc_code': request.POST['ifsc_code'],
            'banking_address': request.POST['banking_address'],

        }
        
        gst_number = request.POST['gst_number']
        # if not validate_gst_number(gst_number):
        #     error_message = "Enter a valid GST number (e.g., 12ABCDE1234F1Z5)."
        #     return render(request, template_path.Customer_path, {'error_message': error_message})

        # Check for existing customer with the same email
        cust_email = request.POST['cust_email']
        # existing_customer = customer.objects.filter(Q(cust_email=cust_email) | Q(gst_number=gst_number)).first()
        # if existing_customer:
        #     error_message = "Email or GST number already exists. Please use a different email or GST number."
        #     return render(request, template_path.Customer_path, {'error_message': error_message,'leads': leads})

        try:
            customer_instance = customer(**customer_data)
            customer_instance.save()
            messages.success(request, 'Customer created successfully.')

            return redirect('fn_customer_List_View')  # Redirect to customer list view upon successful creation
        except IntegrityError as e:
            # Handle IntegrityError (if any)
            return HttpResponse(f"Error: {e}")

    return render(request, template_path.Customer_path,{'leads': leads})

from django.views.decorators.csrf import csrf_exempt

# @csrf_exempt
# @login_required

# def check_email_exist(request):
#     email=request.POST.get("email")
#     print(email,"iiiiiiiiiiiiiiii")
#     user_obj=customer.objects.filter(cust_email=email).exists()
#     if user_obj:
#         return HttpResponse(True)
#     else:
#         return HttpResponse(False)


def check_email_exist(request):
    email = request.POST.get("email")
    print(email, "iiiiiiiiiiiiiiii")

    # Allow "NA" or "na" without checking for existence
    if email.lower() == "na":
        return HttpResponse(False)
    
    user_obj = customer.objects.filter(cust_email=email).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)



@csrf_exempt
@login_required
def check_gst_exist(request):
    gst_number = request.POST.get("gst_number")
    print(gst_number, "iiiiiiiiiiiiiiii")
    user_obj = customer.objects.filter(gst_number=gst_number).exists()
    if user_obj:
        return HttpResponse("True")
    else:
        return HttpResponse("False")

@login_required
def validate_gst_number(gst_number):
    if gst_number.strip() == '':
        return True  # Allow empty value

    return bool(gst_no_pattern.match(gst_number))



@login_required
def fn_customer_List_View(request):
    print("<><>1")
    customer_data = customer.objects.all().order_by('-id')
    context = {'customer_data':customer_data}
    return render(request,template_path.Customer_list,context)


@login_required
def edit_customer(request, customer_id):
    # Fetch the customer instance based on the customer_id
    customer_instance = get_object_or_404(customer, id=customer_id)

    if request.method == 'POST':
        customer_instance.gender = request.POST['gender']
        customer_instance.customer = request.POST['customer']
        customer_instance.cust_email = request.POST['cust_email']
        customer_instance.company_name = request.POST['company_name']
        customer_instance.phone = request.POST['phone']
        customer_instance.display_name = request.POST['display_name']
        customer_instance.website = request.POST['website']
        customer_instance.mobile = request.POST['mobile']
        customer_instance.gst_treatment = request.POST['gst_treatment']
        customer_instance.gst_number = request.POST['gst_number']
        customer_instance.state = request.POST['state']
        customer_instance.balance = request.POST['balance']
        customer_instance.pan_number = request.POST['pan_number']
        customer_instance.discount = request.POST['discount']
        customer_instance.credit_limit = request.POST['credit_limit']
        customer_instance.attention = request.POST['attention']
        customer_instance.street = request.POST['street']
        customer_instance.city = request.POST['city']
        customer_instance.state = request.POST['state']
        customer_instance.pincode = request.POST['pincode']
        customer_instance.gst_uin = request.POST['gst_uin']
        customer_instance.com_state = request.POST['com_state']

        customer_instance.contact_number = request.POST['contact_number']
        customer_instance.shipping_1_attention = request.POST['shipping_1_attention']
        customer_instance.shipping_1_street = request.POST['shipping_1_street']
        customer_instance.shipping_1_city = request.POST['shipping_1_city']
        customer_instance.shipping_1_state = request.POST['shipping_1_state']
        customer_instance.shipping_1_pincode = request.POST['shipping_1_pincode']
        customer_instance.shipping_1_gst_uin = request.POST['shipping_1_gst_uin']
        customer_instance.shipping_1_contact_number = request.POST['shipping_1_contact_number']
        

        customer_instance.shipping_2_attention = request.POST['shipping_2_attention']
        customer_instance.shipping_2_street = request.POST['shipping_2_street']
        customer_instance.shipping_2_city = request.POST['shipping_2_city']
        customer_instance.shipping_2_state = request.POST['shipping_2_state']
        customer_instance.shipping_2_pincode = request.POST['shipping_2_pincode']
        customer_instance.shipping_2_gst_uin = request.POST['shipping_2_gst_uin']
        customer_instance.shipping_2_contact_number = request.POST['shipping_2_contact_number']
           
        customer_instance.shipping_3_attention = request.POST['shipping_3_attention']
        customer_instance.shipping_3_street = request.POST['shipping_3_street']
        customer_instance.shipping_3_city = request.POST['shipping_3_city']
        customer_instance.shipping_3_state = request.POST['shipping_3_state']
        customer_instance.shipping_3_pincode = request.POST['shipping_3_pincode']
        customer_instance.shipping_3_gst_uin = request.POST['shipping_3_gst_uin']
        customer_instance.shipping_3_contact_number = request.POST['shipping_3_contact_number']

        customer_instance.shipping_4_attention = request.POST['shipping_4_attention']
        customer_instance.shipping_4_street = request.POST['shipping_4_street']
        customer_instance.shipping_4_city = request.POST['shipping_4_city']
        customer_instance.shipping_4_state = request.POST['shipping_4_state']
        customer_instance.shipping_4_pincode = request.POST['shipping_4_pincode']
        customer_instance.shipping_4_gst_uin = request.POST['shipping_4_gst_uin']
        customer_instance.shipping_4_contact_number = request.POST['shipping_4_contact_number']
           
        customer_instance.bank_name = request.POST['bank_name']
        customer_instance.account_number = request.POST['account_number']
        customer_instance.branch_name = request.POST['branch_name']
        customer_instance.ifsc_code = request.POST['ifsc_code']
        customer_instance.banking_address = request.POST['banking_address']


        
     
        customer_instance.save()
        messages.success(request, 'Customer Updated successfully.')

        return redirect('fn_customer_List_View')

    return render(request, template_path.EditCustomer_path, {'customer_instance': customer_instance})



@login_required
def delete_customer(request,customer_id):
    '''
    This view function for delete the specifice project.
    '''
    # obj = get_object_or_404(customer, id=customer_id)
    obj1=customer.objects.filter(id=customer_id)
    obj1.delete()
    messages.error(request, 'Customer Deleted.')

    return redirect('fn_customer_List_View')


@login_required
def show_customer(request, id):
    customer_instance = customer.objects.filter(id=id).first()

    context={
        # 'customer_received_amount':customer_instance.cust_receive_amount,
        'date':customer_instance.due_date,
        'customer':customer_instance.customer,
        'customer_instance':customer_instance,
    }


    return render(request, template_path.show_customer,context)







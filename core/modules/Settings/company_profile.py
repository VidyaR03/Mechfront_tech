from django.shortcuts import render, redirect, get_object_or_404
from core.models import  employee, leave_type, Hrleaves, employee_salary, Settings
from core.modules import template_path
from datetime import datetime
from django.http import JsonResponse
from django.http import HttpResponse
from django.contrib import messages
from decimal import Decimal

from core.modules.login.login import login_required


@login_required
def add_company_profile(request):
    
    if request.method == 'POST':
        profile_photo = request.FILES.get('profile_photo')
        company_name = request.POST.get('company_name') 
        organization_type = request.POST.get('organization_type') 
        fiscal_year = request.POST.get('fiscal_year') 
        industry = request.POST.get('industry') 
        currency = request.POST.get('currency') 
        address1 = request.POST.get('address1') 
        address2 = request.POST.get('address2') 
        pincode = request.POST.get('pincode') 
        email = request.POST.get('email') 
        phone = request.POST.get('phone') 
        com_website = request.POST.get('com_website') 
        upload_sign = request.FILES.get('upload_sign') 
        upload_QR_code = request.FILES.get('upload_QR_code') 
        status = request.POST.get('status') 
        gst_number = request.POST.get('gst_number') 
        pan_number = request.POST.get('pan_number') 
        tan_number = request.POST.get('tan_number') 
        cin_number = request.POST.get('cin_number') 
        
        
       
        obj = Settings(
            profile_photo = profile_photo,
            company_name = company_name,
            organization_type = organization_type,
            fiscal_year=fiscal_year,
            industry=industry,
            currency=currency,
            address1=address1,
            address2 = address2,
            pincode = pincode,
            email = email,
            phone = phone,
            com_website=com_website,
            upload_sign=upload_sign,
            upload_QR_code=upload_QR_code,
            status=status,
            gst_number=gst_number,
            pan_number = pan_number,
            tan_number = tan_number,
            cin_number = cin_number,
        )
        obj.save()
        return redirect('fn_company_profile_List')
    return render(request,template_path.company_profile_path)


# @login_required(login_url='admin_login_url')
@login_required
def fn_company_profile_List(request):
    form = Settings.objects.all()
    context = {'form':form}
    return render(request,template_path.company_profile_list,context)



@login_required
def edit_company_profile(request, employee_id):
    company_instance = Settings.objects.get(id=employee_id)  
    context = {
        'form':company_instance       
    }
    if request.method == 'POST':
        profile_photo = request.FILES.get('profile_photo')
        upload_sign = request.FILES.get('upload_sign') 
        upload_QR_code = request.FILES.get('upload_QR_code') 
        company_name = request.POST.get('company_name') 
        fiscal_year = request.POST.get('fiscal_year') 
        industry = request.POST.get('industry') 
        currency = request.POST.get('currency') 
        address1 = request.POST.get('address1') 
        address2 = request.POST.get('address2') 
        pincode = request.POST.get('pincode') 
        email = request.POST.get('email') 
        phone = request.POST.get('phone') 
        com_website = request.POST.get('com_website') 
        status = request.POST.get('status') 
        gst_number = request.POST.get('gst_number') 
        pan_number = request.POST.get('pan_number') 
        tan_number = request.POST.get('tan_number') 
        cin_number = request.POST.get('cin_number') 
        organization_type = request.POST.get('organization_type') 

        company_instance.company_name = company_name
        company_instance.fiscal_year = fiscal_year
        company_instance.industry = industry
        company_instance.currency = currency
        company_instance.address1 = address1
        company_instance.address2 = address2
        company_instance.pincode = pincode
        company_instance.email = email
        company_instance.phone = phone
        company_instance.com_website = com_website
        company_instance.status = status
        company_instance.gst_number = gst_number
        company_instance.pan_number = pan_number
        company_instance.tan_number = tan_number
        company_instance.cin_number = cin_number
        company_instance.organization_type = organization_type

        if profile_photo:
            company_instance.profile_photo = profile_photo
        if upload_sign:
            company_instance.upload_sign = upload_sign
        if upload_QR_code:
            company_instance.upload_QR_code = upload_QR_code

        company_instance.save()
        return redirect('fn_company_profile_List')


    return render(request, template_path.comapny_profile_edit_path,context) 


# if request.method == 'POST':
#     profile_photo = request.FILES.get('profile_photo')
#     upload_sign = request.FILES.get('upload_sign')
#     upload_QR_code = request.FILES.get('upload_QR_code')

#     company_name = request.POST.get('company_name') 
#     fiscal_year = request.POST.get('fiscal_year') 
#     industry = request.POST.get('industry') 
#     currency = request.POST.get('currency') 
#     address1 = request.POST.get('address1') 
#     address2 = request.POST.get('address2') 
#     pincode = request.POST.get('pincode') 
#     email = request.POST.get('email') 
#     phone = request.POST.get('phone') 
#     com_website = request.POST.get('com_website') 
#     status = request.POST.get('status') 
#     gst_number = request.POST.get('gst_number') 
#     pan_number = request.POST.get('pan_number') 
#     tan_number = request.POST.get('tan_number') 
#     cin_number = request.POST.get('cin_number') 
#     organization_type = request.POST.get('organization_type') 

#     # Assign non-file fields
#     company_instance.company_name = company_name
#     company_instance.fiscal_year = fiscal_year
#     company_instance.industry = industry
#     company_instance.currency = currency
#     company_instance.address1 = address1
#     company_instance.address2 = address2
#     company_instance.pincode = pincode
#     company_instance.email = email
#     company_instance.phone = phone
#     company_instance.com_website = com_website
#     company_instance.status = status
#     company_instance.gst_number = gst_number
#     company_instance.pan_number = pan_number
#     company_instance.tan_number = tan_number
#     company_instance.cin_number = cin_number
#     company_instance.organization_type = organization_type

#     # Only update images if a new file is uploaded
#     if profile_photo:
#         company_instance.profile_photo = profile_photo
#     if upload_sign:
#         company_instance.upload_sign = upload_sign
#     if upload_QR_code:
#         company_instance.upload_QR_code = upload_QR_code

#     company_instance.save()
#     return redirect('fn_company_profile_List')


@login_required
def delete_company_profile(request,employee_id):
    '''
    This view function for delete the specifice project.
    '''
    obj = get_object_or_404(Settings, id=employee_id)

    obj.delete()
    return redirect('fn_company_profile_List')

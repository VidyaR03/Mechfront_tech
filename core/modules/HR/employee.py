from django.shortcuts import render, redirect, get_object_or_404
from core.models import department, designation, employee, leave_type
from core.modules import template_path
from datetime import datetime

from core.modules.login.login import login_required
from django.contrib import messages


# @login_required(login_url='admin_login_url')
@login_required
def add_employee(request):
    if request.method == 'GET':
        employee_designation =  designation.objects.all()
        employee_department = department.objects.all()
        context={
            'employee_designation':employee_designation,
            'employee_department':employee_department
        }
        return render(request,template_path.employee_path,context)
    if request.method == 'POST':
        current_date = datetime.now().date()

        name = request.POST.get('name')
        email = request.POST.get('email')  
        joining_date_old = request.POST.get('joining_date')      
        joining_date = datetime.strptime(joining_date_old, '%Y-%m-%d').date()  # Convert joining date to datetime object
       
        phone=request.POST.get('phone')
        emp_department = department.objects.filter(name=request.POST.get('department_name')).first()   
        emp_designation = designation.objects.filter(name=request.POST.get('designation_name')).first()   
        address = request.POST.get('address')
        bank_name = request.POST.get('bank_name')        
        account_number = request.POST.get('account_number')
        upload_photo = request.FILES.get('upload_photo')
        status = request.POST.get('status')
        ifsc_code = request.POST.get('ifsc_code') 
        leaves_allocated = request.POST.get('leaves_allocated', 0.00)


        if joining_date.year == current_date.year :    
           
            months_since =  (12 - joining_date.month) 
            # print("months_since",months_since)
            earned_leaves = months_since * 1.5
            casual_leaves = months_since * 0.67
            formatted_casual_leaves = "{:.2f}".format(casual_leaves)

         

      
        obj = employee(
            name=name,
            email=email,
            joining_date=joining_date,
            phone=phone,
            department = emp_department,
            designation=emp_designation,
            address=address,
            bank_name=bank_name,
            account_number=account_number,
            upload_photo=upload_photo,
            status=status,  
            earned_leaves=earned_leaves,
            casual_leaves=formatted_casual_leaves,
            ifsc_code=ifsc_code,
            leaves_allocated=leaves_allocated

            )
        obj.save()
        messages.success(request, 'Employee Added Successfully.')

        return redirect('fn_employee_List_View')







# @login_required(login_url='admin_login_url')
@login_required
def fn_employee_List_View(request):
    form = employee.objects.all().order_by('-id')
    context = {'form':form}
    return render(request,template_path.employee_list,context)



@login_required
def edit_employee(request, employee_id):
    emp_designation = designation.objects.all()
    emp_department = department.objects.all()
    employee_instance = employee.objects.get(id=employee_id)

    context = {
        'emp_designation': emp_designation,
        'emp_department': emp_department,
        'form': employee_instance
    }

    if request.method == 'POST':
        current_date = datetime.now().date()

        name = request.POST.get('name')
        email = request.POST.get('email')  
        joining_date_old = request.POST.get('joining_date')      
        joining_date = datetime.strptime(joining_date_old, '%Y-%m-%d').date()

        phone = request.POST.get('phone')
        emp_department = department.objects.filter(name=request.POST.get('department_name')).first()   
        emp_designation = designation.objects.filter(name=request.POST.get('designation_name')).first()   
        address = request.POST.get('address')
        bank_name = request.POST.get('bank_name')        
        account_number = request.POST.get('account_number')
        upload_photo = request.FILES.get('upload_photo')
        status = request.POST.get('status')
        ifsc_code = request.POST.get('ifsc_code')
        leaves_allocated = request.POST.get('leaves_allocated', 0.00)

        if joining_date.year == current_date.year:    
            months_since = (12 - joining_date.month)
            earned_leaves = months_since * 1.5
            casual_leaves = months_since * 0.67
            formatted_casual_leaves = "{:.2f}".format(casual_leaves)

        else:
            earned_leaves = 0
            formatted_casual_leaves = "0.00"

        # Update employee instance with new data
        employee_instance.name = name
        employee_instance.email = email
        employee_instance.joining_date = joining_date
        employee_instance.phone = phone
        employee_instance.department = emp_department
        employee_instance.designation = emp_designation
        employee_instance.address = address
        employee_instance.bank_name = bank_name
        employee_instance.account_number = account_number
        employee_instance.status = status
        employee_instance.earned_leaves = earned_leaves
        employee_instance.casual_leaves = formatted_casual_leaves
        employee_instance.ifsc_code = ifsc_code
        employee_instance.leaves_allocated = leaves_allocated

        # Update photo if a new one is uploaded
        if upload_photo:
            employee_instance.upload_photo = upload_photo
        
        # Save the updated employee instance
        employee_instance.save()
        messages.success(request, 'Employee Updated Successfully.')


        return redirect('fn_employee_List_View')

    return render(request, template_path.Editemployee_path,context) 









# @login_required(login_url='admin_login_url')
# def edit_employee(request,employee_id):
#     '''
#     This view function for update the specific Consignment.
#     '''
#     emp_designation =  designation.objects.all()
#     emp_department = department.objects.all()
#     form = employee.objects.get(id=employee_id)

#     context={
#         'emp_designation':emp_designation,
#         'emp_department':emp_department,
#         'form':form

#     }    
#     if request.method == 'POST':
#         current_date = datetime.now().date()

#         name = request.POST.get('name')
#         email = request.POST.get('email')  
#         joining_date_old = request.POST.get('joining_date')      
#         joining_date = datetime.strptime(joining_date_old, '%Y-%m-%d').date()  # Convert joining date to datetime object
       
#         phone=request.POST.get('phone')
#         emp_department = department.objects.filter(name=request.POST.get('department_name')).first()   
#         emp_designation = designation.objects.filter(name=request.POST.get('designation_name')).first()   
#         address = request.POST.get('address')
#         bank_name = request.POST.get('bank_name')        
#         account_number = request.POST.get('account_number')
#         upload_photo = request.FILES.get('upload_photo')
#         status = request.POST.get('status') 

#         if joining_date.year == current_date.year :    
           
#             months_since =  (12 - joining_date.month) 
#             print("months_since",months_since)
#             earned_leaves = months_since * 1.5
#             casual_leaves = months_since * 0.67
#             formatted_casual_leaves = "{:.2f}".format(casual_leaves)

         

      
#         obj = employee(
#             id = employee_id,
#             name=name,
#             email=email,
#             joining_date=joining_date,
#             phone=phone,
#             department = emp_department,
#             designation=emp_designation,
#             address=address,
#             bank_name=bank_name,
#             account_number=account_number,
#             upload_photo=upload_photo,
#             status=status,  
#             earned_leaves=earned_leaves,
#             casual_leaves=formatted_casual_leaves

#             )
        
#         obj.save()
#         if upload_photo:
#             employee.upload_photo = upload_photo
        
#         # Save the updated employee instance
#         employee.save()
#         context={
#             'employee':employee
#         }
#         return redirect('fn_employee_List_View')

#     return render(request, template_path.Editemployee_path,context) 



@login_required
def delete_employee(request,employee_id):
    '''
    This view function for delete the specifice project.
    '''
    obj = get_object_or_404(employee, id=employee_id)

    obj.delete()
    messages.error(request, 'Employee Deleted.')

    return redirect('fn_employee_List_View')
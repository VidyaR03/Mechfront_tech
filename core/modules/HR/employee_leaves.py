from django.shortcuts import render, redirect, get_object_or_404
from core.models import  employee, leave_type, Hrleaves
from core.modules import template_path
from datetime import datetime
from django.http import JsonResponse
from django.http import HttpResponse
from django.contrib import messages

from core.modules.login.login import login_required


@login_required
def add_employee_leaves(request):
    if request.method == 'GET':
        employee_name = employee.objects.all()
        # emp_leave_type = leave_type.objects.all()
        context = {
            'employee_name': employee_name,
        }
        return render(request, template_path.hr_leave_path, context)
    
    if request.method == 'POST':
        employee_name = employee.objects.filter(name=request.POST.get('employee_name')).first()
        from_date = datetime.strptime(request.POST.get('from_date'), '%Y-%m-%d').date()
        to_date = datetime.strptime(request.POST.get('to_date'), '%Y-%m-%d').date()
        no_days = (to_date - from_date).days + 1 if from_date and to_date else None
        leave_type = request.POST.get('leave_type')
        leave_reason = request.POST.get('leave_reason')

        if leave_type == "casual":
            if employee_name.casual_leaves >= no_days:
                employee_name.casual_leaves -= no_days  # Deduct casual leaves
                remaining_days = employee_name.casual_leaves + employee_name.earned_leaves
                employee_name.save()  # Save the entire employee object
            else:
                messages.warning(request, "You don't have sufficient casual leaves.")
                return redirect('add_hr_leaves')  # Redirect without saving if insufficient leaves
        else:
            if employee_name.earned_leaves >= no_days:
                employee_name.earned_leaves -= no_days  # Deduct earned leaves
                remaining_days = employee_name.casual_leaves + employee_name.earned_leaves
                employee_name.save()  # Save the entire employee object
            else:
                messages.warning(request, "You don't have sufficient earned leaves.")
                return redirect('add_hr_leaves')  # Redirect without saving if insufficient leaves

        obj = Hrleaves(
            employee_name=employee_name,
            from_date=from_date,
            to_date=to_date,
            no_days=no_days,
            leave_type=leave_type,
            leave_reason=leave_reason,
            remaining_days=remaining_days
        )
        obj.save()
        messages.success(request,"Employee Leave Type Added.")
        return redirect('hr_leaves_List_View')



# def add_employee_leaves(request):
#     if request.method == 'GET':
#         employee_name =  employee.objects.all()
#         # emp_leave_type = leave_type.objects.all()
#         context={
#             'employee_name':employee_name,
            
#         }
#         return render(request,template_path.hr_leave_path,context)
#     if request.method == 'POST':
#         employee_name = employee.objects.filter(name=request.POST.get('employee_name')).first()   
#         from_date = datetime.strptime(request.POST.get('from_date'), '%Y-%m-%d').date()
#         to_date = datetime.strptime(request.POST.get('to_date'), '%Y-%m-%d').date()
#         no_days = (to_date - from_date).days + 1 if from_date and to_date else None
#         leave_type = request.POST.get('leave_type')  
#         leave_reason = request.POST.get('leave_reason')

#         if leave_type == "casual":
#             if employee_name.casual_leaves >= no_days:
#                 employee_name.casual_leaves -= no_days  # Deduct casual leaves
#                 employee_name.save()  # Save the entire employee object
#             else:
#                messages.warning(request,"You don't have sufficient casual leaves.")
#         else:
#             if employee_name.earned_leaves >= no_days:
#                 employee_name.earned_leaves -= no_days  # Deduct earned leaves
#                 employee_name.save()  # Save the entire employee object
#             else:
#                messages.warning(request,"You don't have sufficient earned leaves.")

#         remaining_days = employee_name.casual_leaves + employee_name.earned_leaves      
      
#         obj = Hrleaves(
#             employee_name=employee_name,
#             from_date=from_date,
#             to_date=to_date,
#             no_days = no_days,
#             leave_type = leave_type,            
#             leave_reason=leave_reason,
#             remaining_days=remaining_days
#             )
#         obj.save()
#         return redirect('add_hr_leaves')



# @login_required(login_url='admin_login_url')
@login_required
def fn_employee_leave_List(request):
    form = Hrleaves.objects.all().order_by('-id')
    context = {'form':form}
    return render(request,template_path.hr_leaves_list,context)

# @login_required(login_url='admin_login_url')
@login_required
def edit_employee_leaves(request,id):
    '''
    This view function for update the specific Consignment.
    '''
    form = Hrleaves.objects.get(id=id)
    employee_name =  employee.objects.all()
    context={
            'employee_name':employee_name,
            'form':form
        }  
    if request.method == 'POST':
        employee_name = employee.objects.filter(name=request.POST.get('employee_name')).first()   
        from_date = datetime.strptime(request.POST.get('from_date'), '%Y-%m-%d').date()
        to_date = datetime.strptime(request.POST.get('to_date'), '%Y-%m-%d').date()
        no_days = (to_date - from_date).days + 1 if from_date and to_date else None
        leave_type = request.POST.get('leave_type')  
        leave_reason = request.POST.get('leave_reason')

        if leave_type == "casual":
            if employee_name.casual_leaves >= no_days:
                employee_name.casual_leaves -= no_days  # Deduct casual leaves
                employee_name.save()  # Save the entire employee object
            else:
               messages.warning(request,"You don't have sufficient casual leaves.")
        else:
            if employee_name.earned_leaves >= no_days:
                employee_name.earned_leaves -= no_days  # Deduct earned leaves
                employee_name.save()  # Save the entire employee object
            else:
               messages.warning(request,"You don't have sufficient earned leaves.")

        remaining_days = employee_name.casual_leaves + employee_name.earned_leaves      
      
        obj = Hrleaves(
            id=id,
            employee_name=employee_name,
            from_date=from_date,
            to_date=to_date,
            no_days = no_days,
            leave_type = leave_type,            
            leave_reason=leave_reason,
            remaining_days=remaining_days
            )
        obj.save()
        messages.success(request,"Employee Leave Type Updated.")

        return redirect('hr_leaves_List_View')

    return render(request, template_path.Edit_leaves_path,context) 


@login_required
def delete_employee_leaves(request,id):
    '''
    This view function for delete the specifice project.
    '''
    obj = get_object_or_404(Hrleaves, id=id)

    obj.delete()
    messages.error(request,"Employee Leave Type Deleted.")

    return redirect('hr_leaves_List_View')


# def get_emp_leave(request,emp_name):
#     emp = employee.objects.get(name = emp_name)
   
#     emp_info = {
#         'emp_earned': emp.earned_leaves,
#         'emp_casual': emp.casual_leaves,
#     }
#     return JsonResponse(emp_info)
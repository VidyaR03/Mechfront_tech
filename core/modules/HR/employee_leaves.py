from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from core.models import  employee, leave_type, Hrleaves
from core.modules import template_path
from datetime import datetime
from django.http import JsonResponse
from django.http import HttpResponse
from django.contrib import messages

from core.modules.login.login import login_required
from django.db.models import Sum

from decimal import Decimal
from django.db.models import Sum

@login_required
def add_employee_leaves(request):
    if request.method == 'GET':
        employees = employee.objects.all()
        return render(request, template_path.hr_leave_path, {'employee_name': employees})

    if request.method == 'POST':
        try:
            emp_id = request.POST.get('employee_name')
            emp_obj = employee.objects.filter(id=emp_id).first()
            if not emp_obj:
                messages.error(request, "Selected employee not found.")
                return redirect('add_hr_leaves')

            from_date_str = request.POST.get('from_date')
            to_date_str = request.POST.get('to_date')
            leave_type = request.POST.get('leave_type')
            print("DEBUG => Leave type from form:", leave_type)

            leave_reason = request.POST.get('leave_reason')

            if not from_date_str or not to_date_str or not leave_type or not leave_reason:
                messages.error(request, "Please fill all required fields.")
                return redirect('add_hr_leaves')

            from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
            to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date()

            # ✅ Normalize leave type
            leave_type_clean = leave_type.strip().lower()

            if leave_type_clean in ["half", "half day", "half-day"]:
                if from_date != to_date:
                    messages.error(request, "Half Day leave must be applied for a single date.")
                    return redirect('add_hr_leaves')
                no_days = Decimal("0.5")
            else:
                no_days = Decimal((to_date - from_date).days + 1)



            # ✅ Use Decimal for allocated leaves
            leave_allocate = Decimal(str(emp_obj.leaves_allocated or 0))

            # ✅ Calculate total leaves already taken
            total_taken = Hrleaves.objects.filter(employee_name=emp_obj).aggregate(
                total=Sum('no_days')
            )['total'] or Decimal("0")

            total_taken = Decimal(str(total_taken))

            remaining_leaves = leave_allocate - total_taken

            # 🔍 Debug print here
            print("DEBUG => Allocated:", leave_allocate,
                "Taken:", total_taken,
                "Applied:", no_days,
                "Remaining before applying:", remaining_leaves,
                "Remaining after applying:", remaining_leaves - no_days)

            # Check if sufficient leaves
            if leave_type != "LOP" and no_days > remaining_leaves:
                messages.warning(request, f"Insufficient remaining leaves. Available: {remaining_leaves}")
                return redirect('add_hr_leaves')

            # Remaining days after this leave
            remaining_days = remaining_leaves - no_days if leave_type != "LOP" else remaining_leaves

            # Save leave
            leave_obj = Hrleaves(
                employee_name=emp_obj,
                from_date=from_date,
                to_date=to_date,
                no_days=no_days,
                leave_type=leave_type,
                leave_reason=leave_reason,
                remaining_days=remaining_days if leave_type != "LOP" else Decimal("0")
            )
            leave_obj.save()

            # Fiscal year redirect
            fiscal_year_start = from_date.year if from_date.month >= 4 else from_date.year - 1
            fiscal_year_end = fiscal_year_start + 1
            redirect_url = f'{reverse("hr_leaves_List_View")}?year={fiscal_year_start}-{fiscal_year_end}'
            messages.success(request, "Employee leave saved successfully.")
            return redirect(redirect_url)

        except Exception as e:
            print("Error in add_employee_leaves:", e)
            messages.error(request, f"Error occurred while saving the leave. {e}")
            return redirect('add_hr_leaves')

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
        employee_name = employee.objects.filter(id=request.POST.get('employee_name')).first()   
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


def get_emp_leaves_allocated(request, emp_id):
    emp = employee.objects.filter(id=emp_id).first()
    leaves_allocated = emp.leaves_allocated if emp else 0
    return JsonResponse({'leaves_allocated': leaves_allocated})

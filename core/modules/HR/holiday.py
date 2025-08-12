from django.shortcuts import render, redirect, get_object_or_404
from core.models import department, designation, employee, holiday
from core.modules import template_path
from datetime import datetime

from core.modules.login.login import login_required
from django.contrib import messages

# @login_required(login_url='admin_login_url')
# def fn_holiday_add(request):
#     if request.method == 'POST':
#         holiday_name = request.POST.get('holiday_name')
#         from_date = request.POST.get('joining_date')
#         to_date = request.POST.get('joining_date')
#         no_days = request.POST.get('no_days')

       
        
#         obj = holiday(
#             holiday_name=holiday_name,
#             from_date=from_date,
#             to_date=to_date,
#             no_days=no_days,          
#             )
#         obj.save()
#         return redirect('fn_employee_List_View')


@login_required
def fn_holiday_add(request):
    if request.method == 'POST':
        holiday_name = request.POST.get('holiday_name')
        from_date = datetime.strptime(request.POST.get('from_date'), '%Y-%m-%d').date()
        to_date = datetime.strptime(request.POST.get('to_date'), '%Y-%m-%d').date()
        no_days = (to_date - from_date).days + 1 if from_date and to_date else None

        obj = holiday(
            holiday_name=holiday_name,
            from_date=from_date,
            to_date=to_date,
            no_days=no_days
        )
        obj.save()
        messages.success(request,'Holiday Added Successfully')
        return redirect('holiday_List_View')
    return render(request, template_path.holiday_path)  # Replace 'your_template.html' with your actual template name


@login_required
def fn_holiday_List_View(request):
    form = holiday.objects.all().order_by('-id')
    context = {'form':form}
    return render(request,template_path.holiday_list,context)


@login_required
def fn_holiday_edit(request, holiday_id):
    holiday_instance = get_object_or_404(holiday, pk=holiday_id)

    if request.method == 'POST':
        holiday_name = request.POST.get('holiday_name')
        from_date = datetime.strptime(request.POST.get('from_date'), '%Y-%m-%d').date()
        to_date = datetime.strptime(request.POST.get('to_date'), '%Y-%m-%d').date()
        no_days = (to_date - from_date).days + 1 if from_date and to_date else None

        # Update the existing holiday instance with new data
        holiday_instance.holiday_name = holiday_name
        holiday_instance.from_date = from_date
        holiday_instance.to_date = to_date
        holiday_instance.no_days = no_days
        holiday_instance.save()
        messages.success(request,'Holiday Updated Successfully')

        return redirect('holiday_List_View')

    context = {
        'holiday_instance': holiday_instance,
    }
    return render(request, template_path.Editholiday_path, context)



@login_required
def delete_holiday(request,holiday_id):
    '''
    This view function for delete the specifice project.
    '''
    obj = get_object_or_404(holiday, id=holiday_id)

    obj.delete()
    messages.error(request,'Holiday Deleted')

    return redirect('holiday_List_View')
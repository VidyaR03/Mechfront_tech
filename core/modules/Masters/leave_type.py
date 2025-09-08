from django.db.models import Q
from core.models import leave_type
from core.modules import template_path
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect,HttpResponse

from core.modules.login.login import login_required
from django.contrib import messages


@login_required
def leave_type_list_view(request):
    leave_type_list = leave_type.objects.all().order_by('-id')
    context = {
        'leave_type_list':leave_type_list
        }
    return render(request,template_path.leave_type_list,context)

@login_required
def add_leave_type_data(request):
    if request.method == 'POST':
        name = request.POST['name']
        count = request.POST.get('count')

        leave_type_data = {
            'name': name,
            'count': count
        }

        try:
            leave_obj = leave_type(**leave_type_data)
            leave_obj.save()
            messages.success(request, 'Leave Type Added Successfully.')
        except Exception as e:
            messages.error(request, f"Error: {e}")

        return redirect('leave_type_list')

    return render(request, template_path.leave_type_add)


@login_required
def edit_leave_type_data(request, id):
    leave_type_data = get_object_or_404(leave_type, id=id)

    if request.method == 'POST':
        leave_type_data.name = request.POST['name']
        leave_type_data.count = request.POST.get('count')
        leave_type_data.save()

        messages.success(request, 'Leave Type Updated Successfully.')
        return redirect('leave_type_list')

    context = {
        'leave_type_data': leave_type_data
    }
    return render(request, template_path.leave_type_edit, context)


@login_required
def delete_leave_type_data(request, id):
    '''
    This view function for delete the specifice entry.
    '''
    obj = get_object_or_404(leave_type, id=id)

    obj.delete()
    messages.error(request, 'Leave Type Deleted.')

    return redirect('leave_type_list')
from django.db.models import Q
from core.models import department
from core.modules import template_path
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect,HttpResponse

from core.modules.login.login import login_required
from django.contrib import messages


@login_required
def department_list_view(request):
    department_list = department.objects.all().order_by('-id')
    context = {
        'department_list':department_list
        }
    return render(request,template_path.department_list,context)

@login_required
def add_department_data(request):
    if request.method == 'POST':
        department_data = {
            'name': request.POST['name'],
        }
        godown_object = department(**department_data)
        godown_object.save()
        messages.success(request, 'Department Added Successfully.')

        return redirect('department_list')

    return render(request, template_path.department_add)

@login_required
def edit_department_data(request,id):
    # Fetch the customer instance based on the customer_id
    department_data = get_object_or_404(department, id=id)

    if request.method == 'POST':
        # Update the customer data with the new values
        department_data.name = request.POST['name']
        department_data.save()
        messages.success(request, 'Department Updated Successfully.')


        # Redirect to the customer details page or any other appropriate page
        return redirect('department_list')
    context = {
        'department_data': department_data
        }
    # Render the edit customer form with the existing customer data
    return render(request, template_path.department_edit, context)

@login_required
def delete_department_data(request, id):
    '''
    This view function for delete the specifice entry.
    '''
    obj = get_object_or_404(department, id=id)

    obj.delete()
    messages.error(request, 'Department Deleted.')

    return redirect('department_list')
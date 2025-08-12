from django.db.models import Q
from core.models import designation
from core.modules import template_path
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect,HttpResponse

from core.modules.login.login import login_required
from django.contrib import messages

@login_required
def designation_list_view(request):
    designation_list = designation.objects.all().order_by('-id')
    context = {
        'designation_list':designation_list
        }
    return render(request,template_path.designation_list,context)

@login_required
def add_designation_data(request):
    if request.method == 'POST':
        designation_data = {
            'name': request.POST['name'],
        }
        godown_object = designation(**designation_data)
        godown_object.save()
        messages.success(request, 'Designation Added Successfully.')

        return redirect('designation_list')
    return render(request, template_path.designation_add)

@login_required
def edit_designation_data(request,id):
    # Fetch the customer instance based on the customer_id
    designation_data = get_object_or_404(designation, id=id)

    if request.method == 'POST':
        # Update the customer data with the new values
        designation_data.name = request.POST['name']
        designation_data.save()
        messages.success(request, 'Designation Updated Successfully.')


        # Redirect to the customer details page or any other appropriate page
        return redirect('designation_list')
    context = {
        'designation_data': designation_data
        }
    # Render the edit customer form with the existing customer data
    return render(request, template_path.designation_edit, context)

@login_required
def delete_designation_data(request, id):
    '''
    This view function for delete the specifice entry.
    '''
    obj = get_object_or_404(designation, id=id)

    obj.delete()
    messages.error(request, 'Designation Deleted.')

    return redirect('designation_list')
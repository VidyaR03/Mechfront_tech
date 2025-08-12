from django.db.models import Q
from core.models import godown,inventory
from core.modules import template_path
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect,HttpResponse
from core.modules.login.login import login_required
from django.contrib import messages

@login_required
def godown_list_view(request):
    godown_list = godown.objects.all().order_by('-id')
    context = {
        'godown_list':godown_list
        }
    return render(request,template_path.godown_list,context)

@login_required
def godown_view(request,id):

    inv=inventory.objects.filter(inventory_godown=id)
    god=godown.objects.get(id=id)
    context = {
        'godown_list':inv,
        'god':god
        }
    return render(request,template_path.godown_view,context)
 
 
@login_required
def add_godown_data(request):
    if request.method == 'POST':
        godown_data = {
            # 'name': request.POST['name'],
            'date':request.POST['date'],
            'city_name':request.POST['city_name'],
 
        }
        godown_object = godown(**godown_data)
        godown_object.save()
        messages.success(request, 'Godown created successfully.')

        return redirect('godown_list')
    return render(request, template_path.godown_add)
 
@login_required
def edit_godown_data(request,id):
    # Fetch the customer instance based on the customer_id
    godown_data = get_object_or_404(godown, id=id)
 
    if request.method == 'POST':
        # Update the customer data with the new values
 
        # godown_data.name = request.POST['name']
        godown_data.date = request.POST['date']
        godown_data.city_name = request.POST['city_name']

 
        godown_data.save()
        messages.success(request, 'Godown Updated successfully.')

        # Redirect to the customer details page or any other appropriate page
        return redirect('godown_list')
    context = {
        'godown_data': godown_data
        }
    # Render the edit customer form with the existing customer data
    return render(request, template_path.edit_godown_data, context)
 
@login_required
def delete_godown_data(request, id):
    '''
    This view function for delete the specifice project.
    '''
    obj = get_object_or_404(godown, id=id)
 
    obj.delete()
    messages.success(request, 'Godown Deleted successfully.')

    return redirect('godown_list')    
    
 
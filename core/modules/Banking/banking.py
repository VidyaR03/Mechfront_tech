from django.shortcuts import render, redirect, get_object_or_404
from core.models import banking
from core.modules import template_path
from core.modules.login.login import login_required


@login_required
def add_banking(request):
    if request.method == 'POST':
        banking_data = {
            'account_name': request.POST['account_name'],
            'bank_name': request.POST['bank_name'],
            'ifsc_code': request.POST['ifsc_code'],
            'account_code': request.POST['account_code'],           
            'branch_name': request.POST['branch_name'],
            'description': request.POST['description'],
            'account_number': request.POST['account_number'],            
            'balance': request.POST['balance'],
            'pending': request.POST['pending'],
            'status': request.POST['status'],
            
        }
        banking_instance = banking(**banking_data)
        banking_instance.save()
        return redirect('fn_banking_List_View')
    return render(request, template_path.banking_path)


@login_required
def fn_banking_List_View(request):
    form = banking.objects.all().order_by('-id')
    context = {'form':form}
    return render(request,template_path.banking_list,context)



@login_required
def edit_banking(request, banking_id):
    # Fetch the banking instance based on the banking_id
    banking_instance = get_object_or_404(banking, id=banking_id)

    if request.method == 'POST':
        # Update the banking data with the new values
        banking_instance.account_name = request.POST['account_name']
        banking_instance.bank_name = request.POST['bank_name']
        banking_instance.ifsc_code = request.POST['ifsc_code']
        banking_instance.account_code = request.POST['account_code']
        banking_instance.branch_name = request.POST['branch_name']
        banking_instance.description = request.POST['description']
        banking_instance.account_number = request.POST['account_number']
        banking_instance.balance = request.POST['balance']
        banking_instance.pending = request.POST['pending']
        banking_instance.status = request.POST['status']
        banking_instance.save()

        return redirect('fn_banking_List_View')

    return render(request, template_path.Editbanking_path, {'banking_instance': banking_instance})



@login_required
def delete_banking(request,banking_id):
    '''
    This view function for delete the specifice project.
    '''
    obj = get_object_or_404(banking, id=banking_id)

    obj.delete()
    return redirect('fn_banking_List_View')

import re
from django.shortcuts import render, redirect, get_object_or_404
from core.models import transporter
from core.modules import template_path
from core.modules.login.login import login_required
from django.contrib import messages

@login_required
def add_transporter(request):
    if request.method == 'POST':
        transporter_data = {
            'name': request.POST['name'],
            'address': request.POST['address'],
            'gst_no': request.POST['gst_no'],
            'bank_name': request.POST['bank_name'],           
            'account_number': request.POST['account_number'],
            'branch_name': request.POST['branch_name'],
            'mobile': request.POST['mobile'],            
            'vendor_email': request.POST['vendor_email'],
            'timestamp': request.POST['timestamp'],
            'ifsc_code':request.POST['ifsc_code']
            
        }
        transporter_instance = transporter(**transporter_data)
        transporter_instance.save()
        messages.success(request, 'Transporter created successfully.')

        return redirect('fn_transporter_List_View')
    return render(request, template_path.transporter_path)


@login_required
def fn_transporter_List_View(request):
    form = transporter.objects.all().order_by('-id')
    context = {'form':form}
    return render(request,template_path.transporter_list,context)


@login_required
def edit_transporter(request, transporter_id):
    # Fetch the customer instance based on the customer_id
    transporter_instance = get_object_or_404(transporter, id=transporter_id)

    if request.method == 'POST':
        mobile = request.POST.get('mobile', '').strip()

        # Validate mobile server-side
        if not re.match(r'^[6-9][0-9]{9}$', mobile):
            messages.error(request, 'Mobile number must start with 6-9 and be exactly 10 digits.')
            return render(request, template_path.Edittransporter_path, {'transporter_instance': transporter_instance})

        # Update the customer data with the new values
        transporter_instance.name = request.POST['name']
        transporter_instance.address = request.POST['address']
        transporter_instance.gst_no = request.POST['gst_no']
        transporter_instance.bank_name = request.POST['bank_name']
        transporter_instance.account_number = request.POST['account_number']
        transporter_instance.branch_name = request.POST['branch_name']
        transporter_instance.mobile = mobile
        transporter_instance.vendor_email = request.POST['vendor_email']
        transporter_instance.ifsc_code = request.POST['ifsc_code']
        transporter_instance.save()
        messages.success(request, 'Transporter Updated successfully.')

        # Redirect to the customer details page or any other appropriate page
        return redirect('fn_transporter_List_View')

    # Render the edit customer form with the existing customer data
    return render(request, template_path.Edittransporter_path, {'transporter_instance': transporter_instance})



@login_required
def delete_transporter(request,transporter_id):
    '''
    This view function for delete the specifice project.
    '''
    obj = get_object_or_404(transporter, id=transporter_id)

    obj.delete()
    messages.error(request, 'Transporter Deleted.')
    return redirect('fn_transporter_List_View')

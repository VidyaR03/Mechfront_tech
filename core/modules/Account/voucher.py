from django.shortcuts import render, redirect, get_object_or_404
from core.models import department, designation, employee, cash_voucher
from core.modules import template_path
from datetime import datetime
from core.modules.login.login import login_required
import datetime
from django.contrib import messages


# @login_required(login_url='admin_login_url')
@login_required
def add_cash_voucher(request):
    current_date1 = datetime.date.today()
    context= {'current_date':current_date1}

    
    if request.method == 'POST':       
        voucher_number=request.POST.get('voucher_number')
        date = request.POST.get('date')
        amount = request.POST.get('amount')        
        pay_to = request.POST.get('pay_to')
        particular = request.POST.get('particular')
        cost_centre = request.POST.get('cost_centre')  
        bill_no = request.POST.get('bill_no')        
        bill_date = request.POST.get('bill_date')
        remark = request.POST.get('remark')
        balance = request.POST.get('balance')          

      
        obj = cash_voucher(
            voucher_number=voucher_number,
            date=date,
            amount=amount,
            pay_to=pay_to,
            particular = particular,
            cost_centre=cost_centre,
            bill_no=bill_no,
            bill_date=bill_date,
            remark=remark,
            balance=balance        

            )
        obj.save()
        messages.success(request,'Cash Voucher Added Successfully')

        return redirect('fn_cash_coucher_List_View')
    return render(request,template_path.add_cashvoucher_path,context)




# @login_required(login_url='admin_login_url')
@login_required
def fn_cash_coucher_List_View(request):
    form = cash_voucher.objects.all().order_by('-id')
    context = {'form':form}
    return render(request,template_path.cash_voucher_list,context)



@login_required
def edit_cash_voucher(request, voucher_id):  
    form = cash_voucher.objects.get(id=voucher_id)
    context = {'form':form}

    
    if request.method == 'POST':       
        voucher_number=request.POST.get('voucher_number')
        date = request.POST.get('date')
        amount = request.POST.get('amount')        
        pay_to = request.POST.get('pay_to')
        particular = request.POST.get('particular')
        cost_centre = request.POST.get('cost_centre')  
        bill_no = request.POST.get('bill_no')        
        bill_date = request.POST.get('bill_date')
        remark = request.POST.get('remark')
        balance = request.POST.get('balance')          

      
        obj = cash_voucher(
            id = voucher_id,
            voucher_number=voucher_number,
            date=date,
            amount=amount,
            pay_to=pay_to,
            particular = particular,
            cost_centre=cost_centre,
            bill_no=bill_no,
            bill_date=bill_date,
            remark=remark,
            balance=balance        

            )
        obj.save()
        messages.success(request,'Cash Voucher Updated.')

        return redirect('fn_cash_coucher_List_View')

    return render(request, template_path.cash_voucher_edit_path,context) 




@login_required
def delete_cash_voucher(request,voucher_id):
    '''
    This view function for delete the specifice project.
    '''
    obj = get_object_or_404(cash_voucher, id=voucher_id)

    obj.delete()
    messages.error(request,'Cash Voucher Deleted.')

    return redirect('fn_cash_coucher_List_View')


@login_required
def cvoucher_show_pdf(request, id):
    cvoucher = get_object_or_404(cash_voucher, id=id)


    context = {
        'cvoucher':cvoucher,
        }
    return render(request, template_path.cash_voucher,context)
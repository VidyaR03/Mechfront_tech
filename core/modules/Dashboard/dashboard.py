from django.shortcuts import render, redirect
from core.modules import template_path
from django.db.models import Sum
from django.shortcuts import render
from core.models import customer, vendor, payment_made,Purchase_Invoice, Invoice, Purchase_order, Login_User, payment_received
from datetime import datetime
from core.modules.login.login import login_required

# from django.contrib.auth.decorators import login_required
# from django.contrib.auth import authenticate, login, logout

@login_required
def is_authenticated(user):
    return user.is_authenticated


@login_required
# @user_passes_test(is_authenticated, login_url='')
def admin_home(request):
    total_vendor = vendor.objects.count()
    tcustomer = customer.objects.count()
    tInvoice = Invoice.objects.count()
    bill = Purchase_order.objects.count()
    invoices = Invoice.objects.all()
    pinvoice = Purchase_Invoice.objects.all()
    lattest_invoices = Invoice.objects.order_by('-id')[:10]
    lattest_invoices_pinvoice = Purchase_Invoice.objects.order_by('-id')[:10]

    # total_freight = int(sum(float(invoice.invoice_freight) for invoice in invoices if invoice.invoice_freight) or 0)
    total_sub_total =int(sum(float(invoice.invoice_sub_total) for invoice in invoices if invoice.invoice_sub_total))
    total_amount = int(sum(float(invoice.invoice_total) for invoice in invoices if invoice.invoice_total))

    # Initialize empty lists to store credit and debit data for each month
    credit_data = [0] * 12  # Initialize a list with 12 zeros for 12 months
    debit_data = [0] * 12   # Initialize a list with 12 zeros for 12 months

    # Retrieve credit and debit data month-wise
    payments = payment_received.objects.all()

    for payment in payments:
        month_index = payment.payment_received_date.month - 1  # Month index starts from 0
        # Convert rupees to thousands if needed
        if  payment.payment_received_total:
            payment_received_total = float(payment.payment_received_total)
        else:
            payment_received_total = 0.0
        
        if payment.payment_received_amount_used:
            payment_received_amount_used = float(payment.payment_received_amount_used)
        else:
            payment_received_amount_used = 0.0


        credit = round(float(payment_received_total / 1000 if payment_received_total < 1000 else payment_received_total), 2)
        debit = round(float(payment_received_amount_used / 1000 if payment_received_amount_used < 1000 else payment_received_amount_used), 2)

        credit_data[month_index] += credit or 0.0
        debit_data[month_index] += debit or 0.0


    # Pass the data to the template
    context = {
        'total_vendor': total_vendor,
        'tcustomer': tcustomer,
        'credit_data': credit_data,
        'debit_data': debit_data,
        # 'total_freight':total_freight,
        'total_sub_total':total_sub_total,
        'total_amount':total_amount,
        'tInvoice':tInvoice,
        'bill':bill,
        'pinvoice':lattest_invoices_pinvoice,
        'invoices':lattest_invoices

    }

    return render(request,template_path.Dashboard,context)



# def loginPage(request):
#     if request.method == 'POST':
#         username = request.POST.get('email')
#         password = request.POST.get('password')
#         user = authenticate(username=username, password=password)
#         if user is not None:
#             login(request, user)
#             return redirect('home')  # Replace with your home page
#         else:
#             # Handle invalid credentials
#             return render(request, template_path.login_page_path, {'message':"Wrong Credentials..!"})
        
#     return render(request, 'accounts/login.html')

# def logout_view(request):
#     logout(request)
#     return redirect('login')




def loginPage(request):
    if request.method == 'GET':
        return render(request, template_path.login_page_path)
    elif request.method == 'POST':
        email_ = request.POST.get('email')
        password_ = request.POST.get('password')
        user = Login_User.objects.filter(email=email_).first()
        if user is not None:
            if email_ == user.email and password_ == user.password:
                user.is_authenticate = True
                request.session["user_id"] = user.id
                # request.session["name"] = user.first_name
                # request.session["role"] = user.user_role.r_name
                user.save()
                return redirect('admin_home')
            else:
                return render(request, template_path.login_page_path, {'message':"Wrong Credentials..!"})
        else:
            return render(request,template_path.login_page_path, {'message':"Wrong Credentials..!"})


        

def log_out(request):
    try:
        # print("^^^^^^^^^^^^^",request.session.get["user_id"])
        del request.session["user_id"]
        logout(request)
    except Exception as e:
        return render(request, template_path.login_page_path, {'message':f"Logout Successfully"})
    return redirect('loginPage') 



def dashboard(request):
    return render(request,template_path.dash)



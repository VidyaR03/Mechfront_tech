from django.shortcuts import render, redirect
from core.modules import template_path
from django.db.models import Sum
from django.shortcuts import render
from core.models import customer, vendor, sales_order,Purchase_Invoice, Invoice, Purchase_order, Login_User, payment_received
from datetime import datetime
from core.modules.login.login import login_required
from datetime import datetime,timedelta

# from django.contrib.auth.decorators import login_required
# from django.contrib.auth import authenticate, login, logout

@login_required
def is_authenticated(user):
    return user.is_authenticated

from collections import defaultdict
from django.utils import timezone
from django.db.models.functions import ExtractYear, ExtractMonth, ExtractWeek
from django.db.models import Sum
from datetime import datetime, timedelta
import json

def admin_home(request):
    total_vendor = vendor.objects.count()
    tcustomer = customer.objects.count()
    print(tcustomer,'tcustomer')
    tInvoice = Invoice.objects.count()
    bill = Purchase_Invoice.objects.count()
    salesorder = sales_order.objects.count()

    # Get today's date
    today = timezone.now().date()

    # 🟢 Get Current Financial Year (Apr 1 - Mar 31)
    current_year = today.year if today.month >= 4 else today.year - 1
    start_financial_year = datetime(current_year, 4, 1)
    end_financial_year = datetime(current_year + 1, 3, 31)

    # 🟢 Get Current Month's Start and End Dates
    start_of_month = today.replace(day=1)
    end_of_month = (start_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)

    # 🟢 Get Current Week's Start (Monday) and End (Sunday)
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    invoice_format_data = {
        "yearly": {
            "invoiced": sum(float(invoice.invoice_total) for invoice in Invoice.objects.filter(invoice_date__range=[start_financial_year, end_financial_year]) if invoice.invoice_total),
            # "received": sum(float(invoice.invoice_total) - float(invoice.invoice_due) for invoice in Invoice.objects.filter(invoice_date__range=[start_financial_year, end_financial_year]) if invoice.invoice_total and invoice.invoice_due),
            # "pending": sum(float(invoice.invoice_due) for invoice in Invoice.objects.filter(invoice_date__range=[start_financial_year, end_financial_year]) if invoice.invoice_due),
        },
        "monthly": {
            "invoiced": sum(float(invoice.invoice_total) for invoice in Invoice.objects.filter(invoice_date__range=[start_of_month, end_of_month]) if invoice.invoice_total),
            # "received": sum(float(invoice.invoice_total) - float(invoice.invoice_due) for invoice in Invoice.objects.filter(invoice_date__range=[start_of_month, end_of_month]) if invoice.invoice_total and invoice.invoice_due),
            # "pending": sum(float(invoice.invoice_due) for invoice in Invoice.objects.filter(invoice_date__range=[start_of_month, end_of_month]) if invoice.invoice_due),
        },
        "weekly": {
            "invoiced": sum(float(invoice.invoice_total) for invoice in Invoice.objects.filter(invoice_date__range=[start_of_week, end_of_week]) if invoice.invoice_total),
            # "received": sum(float(invoice.invoice_total) - float(invoice.invoice_due) for invoice in Invoice.objects.filter(invoice_date__range=[start_of_week, end_of_week]) if invoice.invoice_total and invoice.invoice_due),
            # "pending": sum(float(invoice.invoice_due) for invoice in Invoice.objects.filter(invoice_date__range=[start_of_week, end_of_week]) if invoice.invoice_due),
        }
    }


    
    seven_days_ago = datetime.now() - timedelta(days=7)

    # Fetch invoices from the last 7 days
    invoices = Invoice.objects.filter(invoice_date__gte=seven_days_ago).order_by('-invoice_date')

    # If no invoices found, fetch the latest 10
    if not invoices.exists():
        invoices = Invoice.objects.all().order_by('-invoice_date')[:10]

    # Fetch purchase invoices from the last 7 days
    pinvoice = Purchase_Invoice.objects.filter(purchase_due_date__gte=seven_days_ago).order_by('-purchase_due_date')

    # If no purchase invoices found, fetch the latest 10
    if not pinvoice.exists():
        pinvoice = Purchase_Invoice.objects.all().order_by('-purchase_due_date')[:10]
    current_date = timezone.now().date()
    
    # Fetch min & max financial year
    min_year = payment_received.objects.order_by('payment_received_date').values_list('payment_received_date', flat=True).first()
    max_year = payment_received.objects.order_by('-payment_received_date').values_list('payment_received_date', flat=True).first()
    min_year = min_year.year if min_year else datetime.now().year - 2
    max_year = max_year.year if max_year else datetime.now().year
    
    # Yearly Data (Apr–Mar format)
    yearly_data = defaultdict(lambda: {"credit": [0] * 12, "debit": [0] * 12})
    payments = payment_received.objects.annotate(
        year=ExtractYear('payment_received_date'),
        month=ExtractMonth('payment_received_date')
    ).values('year', 'month').annotate(
        total_credit=Sum('payment_received_total'),
        total_debit=Sum('payment_received_amount_used')
    )
    
    for payment in payments:
        year = payment['year']
        month = payment['month'] - 1
        financial_month_index = (month - 3) % 12
        fin_year_label = f"{year-1}/{year}" if month < 3 else f"{year}/{year+1}"
        
        yearly_data[fin_year_label]["credit"][financial_month_index] += float(payment['total_credit'] or 0)
        yearly_data[fin_year_label]["debit"][financial_month_index] += float(payment['total_debit'] or 0)
    
    # Monthly Data (From Apr 22 - Mar 23 for the current year)
    current_financial_year = f"{max_year-1}/{max_year}"
    monthly_credit = yearly_data[current_financial_year]["credit"]
    monthly_debit = yearly_data[current_financial_year]["debit"]
    
    # Weekly Data (Current month broken down by weeks)
    weekly_data = {"credit": [0] * 5, "debit": [0] * 5}
    current_month = timezone.now().month
    payments_weekly = payment_received.objects.filter(payment_received_date__month=current_month).annotate(
        week=ExtractWeek('payment_received_date')
    ).values('week').annotate(
        total_credit=Sum('payment_received_total'),
        total_debit=Sum('payment_received_amount_used')
    )
    
    for payment in payments_weekly:
        week_index = (payment['week'] - 1) % 5  # Restrict to 5 weeks max
        weekly_data["credit"][week_index] += float(payment['total_credit'] or 0)
        weekly_data["debit"][week_index] += float(payment['total_debit'] or 0)
    print(monthly_credit,'monthly_credit')
    print(yearly_data,'yearly_data')
    # Prepare financial data for frontend
    financial_chart_data = {
        "yearly": yearly_data,
        "monthly": {"credit": monthly_credit, "debit": monthly_debit},
        "weekly": weekly_data
    }


    
    context = {
        'total_vendor': total_vendor,
        'tcustomer': tcustomer,
        'financial_chart_data': json.dumps(financial_chart_data),
        'total_freight': sum(float(invoice.inv_freight_amount) for invoice in invoices if invoice.inv_freight_amount),
        'total_sub_total': sum(float(invoice.invoice_sub_total) for invoice in invoices if invoice.invoice_sub_total),
        'total_amount': sum(float(invoice.invoice_total) for invoice in invoices if invoice.invoice_total),
        'tInvoice': tInvoice,
        'bill': bill,
        'pinvoice': pinvoice,
        'invoices': invoices,
        'salesorder': salesorder,
        'invoice_format_data': json.dumps(invoice_format_data), 
        

    }

    return render(request, template_path.Dashboard, context)



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



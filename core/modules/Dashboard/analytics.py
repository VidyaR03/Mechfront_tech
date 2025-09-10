from django.shortcuts import render, redirect
from core.modules import template_path
from django.db.models import Sum
from django.shortcuts import render
from core.models import customer, vendor,Leads, sales_order,quotation, Invoice, PurchaseOrder, followup, PaymentReceived
from datetime import datetime
from django.contrib.auth.decorators import user_passes_test
from datetime import datetime, timedelta, date
import calendar
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth import logout
from datetime import datetime,timedelta
from core.modules.login.login import login_required

# @user_passes_test(is_authenticated, login_url='')

def fn_analytics_view(request):
    total_vendor = vendor.objects.count()
    tcustomer = customer.objects.count()
    Manu_Invoice = Invoice.objects.filter(invoice_ser_type = "Manufacturing").count()


    
    follow_up_lab = followup.objects.filter(follow_ser_type = "Lab").count()
    follow_up_lab_live = followup.objects.filter(follow_ser_type="Lab", status="Live").count()
    follow_up_lab_dead = followup.objects.filter(follow_ser_type="Lab", status="Dead").count()
    follow_up_lab_hot = followup.objects.filter(follow_ser_type="Lab", status="Hot").count()

    follow_up_manufact = followup.objects.filter(follow_ser_type = "Manufacturing").count()
    follow_up_manufact_live = followup.objects.filter(follow_ser_type="Manufacturing", status="Live").count()
    follow_up_manufact_dead = followup.objects.filter(follow_ser_type="Manufacturing", status="Dead").count()
    follow_up_manufact_hot = followup.objects.filter(follow_ser_type="Manufacturing", status="Hot").count()



    sales_order_lab = sales_order.objects.filter(so_ser_type = "Lab").count()
    sales_order_lab_comp = sales_order.objects.filter(so_ser_type="Lab", so_status="Complete").count()
    sales_order_lab_receiv = sales_order.objects.filter(so_ser_type="Lab", so_status="Received").count()
    sales_order_lab_prog = sales_order.objects.filter(so_ser_type="Lab", so_status="InProgress").count()
    sales_order_lab_pen = sales_order.objects.filter(so_ser_type="Lab", so_status="Pending").count()


    sales_order_manufact = sales_order.objects.filter(so_ser_type = "Manufacturing").count()
    sales_order_manufact_comp = sales_order.objects.filter(so_ser_type="Manufacturing", so_status="Complete").count()
    sales_order_manufact_receiv = sales_order.objects.filter(so_ser_type="Manufacturing", so_status="Received").count()
    sales_order_manufact_prog = sales_order.objects.filter(so_ser_type="Manufacturing", so_status="InProgress").count()
    sales_order_manufact_pen = sales_order.objects.filter(so_ser_type="Manufacturing", so_status="Pending").count()


    Invoice_lab = Invoice.objects.filter(invoice_ser_type = "Lab").count()
    Invoice_lab_receiv = Invoice.objects.filter(invoice_ser_type="Lab", invoice_status="Received").count()
    Invoice_lab_pen = Invoice.objects.filter(invoice_ser_type="Lab", invoice_status="Pending").count()


    Invoice_manufact = Invoice.objects.filter(invoice_ser_type = "Manufacturing").count()
    Invoice_manufact_receiv = Invoice.objects.filter(invoice_ser_type="Manufacturing", invoice_status="Received").count()
    Invoice_manufact_pen = Invoice.objects.filter(invoice_ser_type="Manufacturing", invoice_status="Pending").count()



    
    print(f'{Invoice_lab_pen},{Invoice_lab},{Invoice_manufact},{Invoice_manufact_pen}',"PPPPPPPPPP")

    # Pass the data to the template
    context = {
        'total_vendor': total_vendor,
        'tcustomer': tcustomer,
       
        'Manu_Invoice':Manu_Invoice,


        'follow_up_lab':follow_up_lab,
        'follow_up_lab_live':follow_up_lab_live,
        'follow_up_lab_dead':follow_up_lab_dead,
        'follow_up_lab_hot':follow_up_lab_hot,

        'follow_up_manufact':follow_up_manufact,
        'follow_up_manufact_live':follow_up_manufact_live,
        'follow_up_manufact_dead':follow_up_manufact_dead,
        'follow_up_manufact_hot':follow_up_manufact_hot,

        'sales_order_lab':sales_order_lab,
        'sales_order_lab_comp':sales_order_lab_comp,
        'sales_order_lab_prog':sales_order_lab_prog,
        'sales_order_lab_pen':sales_order_lab_pen,
        'sales_order_lab_receiv':sales_order_lab_receiv,

        'sales_order_manufact':sales_order_manufact,
        'sales_order_manufact_comp':sales_order_manufact_comp,
        'sales_order_manufact_receiv':sales_order_manufact_receiv,
        'sales_order_manufact_prog':sales_order_manufact_prog,
        'sales_order_manufact_pen':sales_order_manufact_pen,

        'Invoice_lab' :Invoice_lab,
        'Invoice_lab_receiv':Invoice_lab_receiv,
        'Invoice_lab_pen':Invoice_lab_pen,

        'Invoice_manufact' :  Invoice_manufact,
        'Invoice_manufact_receiv':Invoice_manufact_receiv,
        'Invoice_manufact_pen':Invoice_manufact_pen,


    }
    context['credit_data'] = []
    context['debit_data'] = []
    context['pending_data'] = []
    context['complete_data'] = []
    
    sales_order_data = sales_order.objects.all()
    for i in range(1,13):
        print(i)
        start_date = datetime(2024, i, 1) + timedelta()
        if i != 12:
            print(i, '_____________')
            last_date = datetime(2024, i+1, 1) + timedelta(days=-1)
        else:
            last_date = datetime(2025, 1, 1) + timedelta(days=-1)

        if start_date <= datetime.today():
            credit_count = sales_order_data.filter(so_date__gte=start_date, so_date__lte=last_date).count()
            context['credit_data'].append(credit_count)
            debit_count = sales_order_data.filter(so_status='InProgress',so_date__lte=last_date).count()  
            context['debit_data'].append(debit_count)
            pending_data = sales_order_data.filter(so_status='Pending',so_date__lte=last_date).count()
            context['pending_data'].append(pending_data)
            complete_data = sales_order_data.filter(so_status='Complete',so_date__gte=start_date, so_date__lte=last_date).count()
            context['complete_data'].append(complete_data)
        else:
            context['credit_data'].append(0)
            context['debit_data'].append(0)
            context['pending_data'].append(0)
            context['complete_data'].append(0)
    # context['debit_data'] = [300, 200, 300, 400, 500, 600, 1200, 800, 100, 100, 100, 200]
    # context['pending_data'] = [300, 200, 300, 400, 500, 600, 1200, 800, 100, 100, 100, 200]
    # context['cancel_data'] = [300, 200, 300, 400, 500, 600, 1200, 800, 100, 100, 100, 200]
    context['mont_lbl'] = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    return render(request,template_path.Analytic_view,context)



def get_invoice_data(request):
    service_type = request.GET.get('serviceType')
    # Fetch relevant invoice data based on the service type
    if service_type == 'Lab':
        total = Invoice.objects.filter(invoice_ser_type='Lab').count()
        received = Invoice.objects.filter(invoice_ser_type='Lab', invoice_status='Received').count()
        pending = Invoice.objects.filter(invoice_ser_type='Lab', invoice_status='Pending').count()
    elif service_type == 'Manufacturing':
        total = Invoice.objects.filter(invoice_ser_type='Manufacturing').count()
        received = Invoice.objects.filter(invoice_ser_type='Manufacturing', invoice_status='Received').count()
        pending = Invoice.objects.filter(invoice_ser_type='Manufacturing', invoice_status='Pending').count()
    else:
        # Handle invalid service type
        return JsonResponse({'error': 'Invalid service type'}, status=400)
    
    # Prepare data for the pie chart
    series = [total, received, pending]
    labels = ['Total', 'Received', 'Pending']
    
    return JsonResponse({'series': series, 'labels': labels})



def get_quotation_data(request):
    service_type = request.GET.get('serviceType')
    duration = request.GET.get('duration')
    today = date.today()
    start_date =  today
    end_date = today
    if duration == 'Daily':
        # Daily duration: Start and end date are the same (today)
        start_date =  today
        end_date = today
    elif duration == 'Weekly':
        # Weekly duration:
        # - Start date is the beginning of the current week (Sunday)
        # - End date is 6 days from the start (Saturday)
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
    elif duration == 'Monthly':
        # Monthly duration:
        # - Start date is the 1st day of the current month
        # - End date is the last day of the current month
        start_date = today.replace(day=1)
        _, num_days = calendar.monthrange(start_date.year, start_date.month)
        end_date = start_date + timedelta(days=num_days - 1)
    # Fetch relevant invoice data based on the service type
    print(start_date, end_date)
    total = Leads.objects.all().count()
    if service_type == 'Lab':
        received = quotation.objects.filter(q_ser_type='Lab', q_status='Received', q_date__gte=start_date, q_date__lte=end_date).count()
        sent = quotation.objects.filter(q_ser_type='Lab', q_status='Sent', q_date__gte=start_date, q_date__lte=end_date).count()
    elif service_type == 'Manufacturing':
        received = quotation.objects.filter(q_ser_type='Manufacturing', q_status='Received',q_date__gte=start_date, q_date__lte=end_date).count()
        sent = quotation.objects.filter(q_ser_type='Manufacturing', q_status='Sent',q_date__gte=start_date, q_date__lte=end_date).count()
    else:
        # Handle invalid service type
        return JsonResponse({'error': 'Invalid service type'}, status=400)
    
    # Prepare data for the pie chart
    series = [total, received, sent]
    print(service_type,duration,series)
    labels = ['Total Leads', 'Received', 'Sent']
    
    return JsonResponse({'series': series, 'labels': labels})

from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from core.models import credit_note, payment_made, vendor, cash_voucher
from core.modules import template_path
from datetime import datetime
import datetime
from django.http import HttpResponse
from django.template.loader import get_template
from django.conf import settings
from weasyprint import HTML



from core.modules.Account.forms import DateRangeForm

# from django.shortcuts import render
from .forms import DateRangeForm



from django.shortcuts import render
from .forms import DateRangeForm  # Import your DateRangeForm
from core.modules.login.login import login_required


@login_required
def display_data(request):
    if request.method == 'POST':
        form = DateRangeForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']

            # Query specific fields from CreditNote between start date and end date
            credit_notes = credit_note.objects.filter(
                date__range=(start_date, end_date)
            ).values('date', 'creditnote', 'voucher_type', 'voucher_no', 'credit', 'debit')

            # Query specific fields from PaymentMade between start date and end date
            payments_made = payment_made.objects.filter(
                date__range=(start_date, end_date)
            ).values('date', 'perticularnote', 'voucher_type', 'voucher_no', 'credit', 'debit')

            return render(request, template_path.display_custom, {
                'credit_notes': credit_notes,
                'payments_made': payments_made,
                 'start_date': start_date,
                'end_date': end_date,
            })
    else:
        form = DateRangeForm()

    return render(request, template_path.customer_ledger, {'form': form})



# def display_data(request):
#     if request.method == 'POST':
#         form = DateRangeForm(request.POST)
#         if form.is_valid():
#             start_date = form.cleaned_data['start_date']
#             end_date = form.cleaned_data['end_date']

#             # Query specific fields from credit_note between start date and end date
#             credit_notes = credit_note.objects.filter(
#                 date__range=(start_date, end_date)
#             ).values('date', 'creditnote', 'voucher_type', 'voucher_no', 'credit', 'debit')

#             # Query specific fields from payment_made between start date and end date
#             payments_made = payment_made.objects.filter(
#                 date__range=(start_date, end_date)
#             ).values('date', 'perticularnote', 'voucher_type', 'voucher_no', 'credit', 'debit')

#             return render(request,template_path.display_custom, {
#                 'credit_notes': credit_notes,
#                 'payments_made': payments_made,
#             })
#     else:
#         form = DateRangeForm()

#     return render(request, template_path.customer_ledger, {'form': form})


# def display_data(request):
#     if request.method == 'POST':
#         form = DateRangeForm(request.POST)
#         if form.is_valid():
#             start_date = form.cleaned_data['start_date']
#             end_date = form.cleaned_data['end_date']

#             # Query all data from credit_note between start date and end date
#             credit_notes = credit_note.objects.filter(date__range=(start_date, end_date))

#             # Query all data from payment_made between start date and end date
#             payments_made = payment_made.objects.filter(date__range=(start_date, end_date))

#             return render(request, template_path.display_custom, {
#                 'credit_notes': credit_notes,
#                 'payments_made': payments_made,
#             })
#     else:
#         form = DateRangeForm()

#     return render(request, template_path.customer_ledger, {'form': form})




# def download_pdf(request):
#     credit_notes = credit_note.objects.all()
#     payments_made = payment_made.objects.all()
#     template = get_template(template_path.display_custom)
#     html_content = template.render({'credit_notes': credit_notes, 'payments_made': payments_made})

#     # Generate PDF file
#     pdf_file = HTML(string=html_content, base_url=request.build_absolute_uri()).write_pdf()

#     # Create an HTTP response with PDF attachment
#     response = HttpResponse(pdf_file, content_type='application/pdf')
#     response['Content-Disposition'] = 'attachment; filename="downloaded_file.pdf"'

#     return response

# from django.shortcuts import render
# from django.http import HttpResponse
# from django.template.loader import get_template
# from weasyprint import HTML

# def download_pdf(request):
#     # Fetch credit notes and payments made data from your models
#     credit_notes = credit_note.objects.all()
#     payments_made = payment_made.objects.all()

#     # Render the HTML content with data
#     template = get_template('Account/display_customer.html')
#     context = {
#         'credit_notes': credit_notes,
#         'payments_made': payments_made,
#     }
#     html_content = template.render(context)

#     # Generate PDF file
#     pdf_file = HTML(string=html_content, base_url=request.build_absolute_uri()).write_pdf()

#     # Create an HTTP response with PDF attachment
#     response = HttpResponse(pdf_file, content_type='application/pdf')
#     response['Content-Disposition'] = 'attachment; filename="downloaded_file.pdf"'

#     return response


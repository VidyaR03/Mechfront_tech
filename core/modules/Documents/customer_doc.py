import os
import pandas as pd
import xlsxwriter
from django.db import transaction
from core.modules import template_path
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from core.models import *
from core.modules.login.login import login_required


@login_required
def upload_customer_doc(request):
    if request.method == "POST":
        upload_file = request.FILES['upload_customer_excel']
        df = pd.read_excel(upload_file)
        with transaction.atomic():
            for index, row in df.iterrows():
                ventor_details = vendor(
                    gender = row['gender'],
                    contact_person= row['contact_person'],
                    vendor_email= row['vendor_email'],
                    company_name= row['company_name'],
                    phone= row['phone'],           
                    display_name= row['display_name'],
                    website= row['website'],
                    mobile= row['mobile'],
                    gst_treatment= row['gst_treatment'],
                    gst_number= row['gst_number'],
                    state= row['state'],
                    balance= row['balance'],
                    pan_number= row['pan_number'],      
                    delivery_company_name= row['delivery_company_name'],
                    street= row['street'],
                    city= row['city'],
                    delivery_state= row['delivery_state'],
                    pincode= row['pincode'],
                    gst_uin= row['gst_uin'],
                    contact_number= row['contact_number'],
                    vendor_company_name= row['vendor_company_name'],
                    vendor_street= row['vendor_street'],
                    vendor_city= row['vendor_city'],
                    vendor_state= row['vendor_state'],
                    vendor_pincode= row['vendor_pincode'],
                    vendor_gst_uin= row['vendor_gst_uin'],
                    vendor_contact_number= row['vendor_contact_number'],
                    bank_name= row['bank_name'],
                    account_number= row['account_number'],
                    branch_name= row['branch_name'],
                    ifsc_code= row['ifsc_code'],
                    )
                ventor_details.save()
        return redirect('vendor_doc')
    return render(request, template_path.customer_doc)

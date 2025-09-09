from django.shortcuts import render, redirect, get_object_or_404
from core.models import Leads 
from core.modules import template_path
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from urllib.parse import urlparse
from django.db.models import Max
from core.modules.login.login import login_required
from django.contrib import messages

@login_required
def add_leads_data(request):
    if request.method == 'POST':
        # leads_ser_type = request.POST.get('leads_ser_type')
        # Get the count of Leads objects
        # l_Lid_No = 1 if Leads.objects.count() == 0 else Leads.objects.aggregate(max=Max('l_Lid_No'))["max"]+1
        # # Generate lead_id based on leads_ser_type
        # if leads_ser_type == 'Manufacturing':
        #     lead_id = 'M-' + str(l_Lid_No)
        # elif leads_ser_type == 'Lab':
        #     lead_id = 'L-' + str(l_Lid_No)
        # else:
        #     # Default lead_id if leads_ser_type is not recognized
        #     lead_id = 'Default-' + str(l_Lid_No)
        company_name = request.POST.get('company_name')
        contact_person = request.POST.get('contact_person')
        contact_number = request.POST.get('contact_number')
        email = request.POST.get('email')
        status = request.POST.get('status')
        website = request.POST.get('website')
        source = request.POST.get('source')

        inquiry = request.POST.get('inquiry')
        social_media = request.POST.get('social_media')
        # leads_ser_type = request.POST.get('leads_ser_type')

        lead = Leads.objects.create(
            company_name=company_name,
            contact_person=contact_person,
            contact_number=contact_number,
            email=email,
            # l_LS_NO=lead_id,
            status=status,
            source=source,
            website=website,
            inquiry=inquiry,
            social_media=social_media,
            # l_Lid_No=l_Lid_No,
            # leads_ser_type=leads_ser_type
        )
        lead.save()
        messages.success(request, 'Lead created successfully.')

        return redirect('lead_list')  # Assuming you have a URL named 'lead_list' for listing leads
    return render(request, template_path.add_leads_path)


@login_required
def edit_lead_data(request, lead_id):
    lead = Leads.objects.get(id=lead_id)
    if request.method == 'POST':
        # print(request.POST)
        company_name = request.POST.get('company_name')
        contact_person = request.POST.get('contact_person')
        contact_number = request.POST.get('contact_number')
        email = request.POST.get('email')
        website = request.POST.get('website')
        status = request.POST.get('status')
        source = request.POST.get('source')
        inquiry = request.POST.get('inquiry')
        social_media = request.POST.get('social_media')
        # leads_ser_type = request.POST.get('leads_ser_type')       
        lead.company_name = company_name
        lead.contact_person = contact_person
        lead.contact_number = contact_number
        lead.email = email
        lead.website=website
        lead.status = status
        lead.source = source
        lead.inquiry = inquiry
        lead.social_media = social_media
        # if leads_ser_type != lead.leads_ser_type:
        #     # Update l_LS_NO based on the new leads_ser_type
        #     l_Lid_No = lead.l_Lid_No
        #     if leads_ser_type == 'Manufacturing':
        #         lead_id = 'M-' + str(l_Lid_No)
        #     elif leads_ser_type == 'Lab':
        #         lead_id = 'L-' + str(l_Lid_No)
        #     else:
        #         lead_id = 'Default-' + str(l_Lid_No)
        #     lead.l_LS_NO = lead_id
        #     lead.leads_ser_type = leads_ser_type
        lead.save()
        messages.success(request, 'Lead Updated successfully.')

        return redirect('lead_list')  # Assuming you have a URL named 'lead_list' for listing leads

    return render(request, template_path.Edit_lead_path, {'lead': lead})

@login_required
def lead_list_view(request):
    lead_data = Leads.objects.all().order_by('-id')
    context = {'lead_data': lead_data}
    return render(request,template_path.lead_list,context)


@login_required
def update_status(request):
    if request.method == 'POST':
        lead_id = request.POST.get('lead_id')  # Assuming you're passing lead_id along with the status in the request
        new_status = request.POST.get('status')
        lead = Leads.objects.get(pk=lead_id)
        lead.status = new_status
        lead.save()
        return redirect('lead_list')  # Redirect to the lead list view after saving the status
    else:
        pass



@login_required
def delete_lead_data(request,id):
    '''
    This view function for delete the specifice project.
    '''
    # obj = get_object_or_404(customer, id=customer_id)
    obj1=Leads.objects.filter(id=id)
    obj1.delete()
    messages.error(request, 'Lead Deleted.')

    return redirect('lead_list')


@login_required
def show_lead(request, id):
    lead_instance = Leads.objects.filter(id=id).first()

    context={
        'lead_instance':lead_instance,
     
    }


    return render(request, template_path.lead_list,context)



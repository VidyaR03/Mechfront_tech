from django.shortcuts import render, redirect, get_object_or_404
from core.models import  employee, leave_type, Hrleaves, employee_salary
from core.modules import template_path
from datetime import datetime
from django.http import JsonResponse
from django.http import HttpResponse
from django.contrib import messages
from decimal import Decimal

from decimal import Decimal

from core.modules.login.login import login_required
from django.contrib import messages

# Define a function to calculate salary components based on CTC
# def calculate_salary_components(ctc, days_payable, days_paid):
#     if ctc <= 252000:
#         insurance_premiums = 0
#     else:
#         insurance_premiums = 11000.0

#     variable_component = (ctc * 0.10)
#     total_variable_pay = ctc * 0.10
#     total_fixed_pay = ctc - total_variable_pay - insurance_premiums
#     basic_pay = total_fixed_pay * 0.40
#     employer_pf_contribution = 0.13 * basic_pay
#     hra = 0.50 * basic_pay
#     total_flexible_component = total_fixed_pay - basic_pay - hra - employer_pf_contribution
#     conveyance_allowance = 1600 / days_payable * days_paid
#     professional_tax = 200
#     income_tax = 0

#     basic_salary = basic_pay
#     provident_fund = 0.12 * basic_salary
#     flexible_component = (total_flexible_component / 12) * days_paid / days_payable - conveyance_allowance
#     gross_salary = hra + basic_salary + conveyance_allowance + flexible_component + variable_component
#     other_deductions = 0
#     if ctc <= 252000:
#         esic = (0.0075 * float(gross_salary))
#     else:
#         esic = 0
#     total_deductions = provident_fund + professional_tax + income_tax + other_deductions + esic
#     net_salary = Decimal(gross_salary) - Decimal(total_deductions)

#     return {
#         'basic_salary': basic_salary,
#         'hra': hra,
#         'conveyance_allowance': conveyance_allowance,
#         'flexible_component': flexible_component,
#         'variable_component': variable_component,
#         'gross_salary': gross_salary,
#         'net_salary': net_salary,
#         'provident_fund':provident_fund,
#         'other_deductions':other_deductions,
#         'total_variable_pay':total_variable_pay,
#         'total_fixed_pay':total_fixed_pay,
#         'basic_pay':basic_pay,
#         'employer_pf_contribution':employer_pf_contribution,
#         'total_flexible_component':total_flexible_component,
#         'professional_tax':professional_tax
#     }



# def add_employee_salary(request):
#     if request.method == 'GET':
#         employee_name =  employee.objects.all()
#         context = {
#             'employee_name': employee_name,
#         }
#         return render(request, template_path.emp_salary_path, context)
    
#     if request.method == 'POST':
#         ctc = float(request.POST.get('ctc'))
#         days_payable = int(request.POST.get('days_payable'))
#         days_paid = int(request.POST.get('days_paid'))

#         # Calculate salary components based on CTC
#         salary_components = calculate_salary_components(ctc, days_payable, days_paid)

#         # Retrieve other form data
#         employee_name = employee.objects.filter(name=request.POST.get('name')).first()
#         # Retrieve other form fields here...

#         # Save to the database
#         obj = employee_salary(
#             employee_name=employee_name,
#             ctc=ctc,
#             hra=salary_components['hra'],  # Replace with calculated values
#             # Assign other calculated values similarly
#             # Assign other retrieved form fields as needed
#         )
#         obj.save()
#         return redirect('fn_emp_salary_List')


# @login_required(login_url='admin_login_url')
@login_required
def add_employee_salary(request):
    if request.method == 'GET':
        employee_name =  employee.objects.all()
        context={
            'employee_name':employee_name,
        }
        return render(request,template_path.emp_salary_path,context)
    if request.method == 'POST':
        employee_name = employee.objects.filter(name=request.POST.get('name')).first()  
        ctc = request.POST.get('ctc') 
        hra = request.POST.get('hra') 
        esic = request.POST.get('esic') 
        basic_salary = request.POST.get('basic_salary') 
        conveyance_allowance = request.POST.get('conveyance_allowance') 
        flexible_component = request.POST.get('flexible_component') 
        variable_component = request.POST.get('variable_component') 
        provident_fund = request.POST.get('provident_fund') 
        professional_tax = request.POST.get('professional_tax') 
        income_tax = request.POST.get('income_tax') 
        other_deductions = request.POST.get('other_deductions') 
        gross_salary = request.POST.get('gross_salary') 
        total_deductions = request.POST.get('total_deductions') 
        net_salary = request.POST.get('net_salary') 
        other_allowns = request.POST.get('other_allowns') 
        lwf = request.POST.get('days_payable') 
        days_payable = request.POST.get('days_payable') 
        days_paid = request.POST.get('days_paid') 
        month = request.POST.get('month')
        
        
       
        obj = employee_salary(
            employee_name = employee_name,
            ctc = ctc,
            hra = hra,
            esic=esic,
            basic_salary=basic_salary,
            conveyance_allowance=conveyance_allowance,
            flexible_component=flexible_component,
            variable_component = variable_component,
            provident_fund = provident_fund,
            professional_tax = professional_tax,
            income_tax = income_tax,
            other_deductions=other_deductions,
            gross_salary=gross_salary,
            total_deductions=total_deductions,
            net_salary=net_salary,
            other_allowns=other_allowns,
            lwf = lwf,
            days_payable = days_payable,
            days_paid = days_paid,
            month = month
        )
        obj.save()
        messages.success(request,'Employee Salary Added Successfully')

        return redirect('fn_emp_salary_List')







# @login_required(login_url='admin_login_url')
@login_required
def fn_employee_salary_List(request):
    form = employee_salary.objects.all().order_by('-id')
    context = {'form':form}
    return render(request,template_path.emp_salary_list,context)



@login_required
def edit_employee_salary(request, employee_id):
    emp_name = employee.objects.all()
    form = employee_salary.objects.get(id=employee_id)

    
    context = {
        'emp_name': emp_name,
        'form':form
       
    }
    if request.method == 'POST':
        employee_name = employee.objects.filter(name=request.POST.get('name')).first()  
        ctc = request.POST.get('ctc') 
        hra = request.POST.get('hra') 
        esic = request.POST.get('esic') 
        basic_salary = request.POST.get('basic_salary') 
        conveyance_allowance = request.POST.get('conveyance_allowance') 
        flexible_component = request.POST.get('flexible_component') 
        variable_component = request.POST.get('variable_component') 
        provident_fund = request.POST.get('provident_fund') 
        professional_tax = request.POST.get('professional_tax') 
        income_tax = request.POST.get('income_tax') 
        other_deductions = request.POST.get('other_deductions') 
        gross_salary = request.POST.get('gross_salary') 
        total_deductions = request.POST.get('total_deductions') 
        net_salary = request.POST.get('net_salary') 
        other_allowns = request.POST.get('other_allowns') 
        lwf = request.POST.get('lwf') 
        days_payable = request.POST.get('days_payable') 
        days_paid = request.POST.get('days_paid') 
        month = request.POST.get('month')
        
        
       
        obj = employee_salary(
            id = employee_id,
            employee_name = employee_name,
            ctc = ctc,
            hra = hra,
            esic=esic,
            basic_salary=basic_salary,
            conveyance_allowance=conveyance_allowance,
            flexible_component=flexible_component,
            variable_component = variable_component,
            provident_fund = provident_fund,
            professional_tax = professional_tax,
            income_tax = income_tax,
            other_deductions=other_deductions,
            gross_salary=gross_salary,
            total_deductions=total_deductions,
            net_salary=net_salary,
            other_allowns=other_allowns,
            lwf = lwf,
            days_payable = days_payable,
            days_paid = days_paid,
            month = month
        )
        obj.save()
        messages.success(request,'Employee Salary Updated Successfully')

        return redirect('fn_emp_salary_List')

    return render(request, template_path.emp_salary_edit_path,context) 


@login_required
def delete_employee_salary(request,employee_id):
    '''
    This view function for delete the specifice project.
    '''
    obj = get_object_or_404(employee_salary, id=employee_id)

    obj.delete()
    messages.error(request,'Employee Salary Deleted')

    return redirect('fn_emp_salary_List')



















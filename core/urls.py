from . import views
from django.urls import path

from django.urls import path,re_path
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('',views.loginPage , name="loginPage"),    
    path('logout/',views.log_out , name="logout"),
    path('admin_home/',views.admin_home , name="admin_home"),
    path('add_customer/',views.add_customer , name="add_customer"),
    path('fn_customer_List_View/',views.fn_customer_List_View , name="fn_customer_List_View"),
    path('edit_customer/<int:customer_id>/', views.edit_customer, name='edit_customer'),
    path('delete_customer/<int:customer_id>/', views.delete_customer, name='delete_customer'), 
    path('show_customer/<int:id>/',views.show_customer , name="show_customer"),
    path('check_email_exist', views.check_email_exist,name="check_email_exist"),
    path('check_gst_exist', views.check_gst_exist,name="check_gst_exist"),

    path('dash/',views.dashboard , name="dash"),



    path('add_vendor',views.add_vendor , name="add_vendor"),
    path('fn_vendor_List_View/',views.fn_vendor_List_View , name="fn_vendor_List_View"),
    path('edit_vendor/<int:vendor_id>/', views.edit_vendor, name='edit_vendor'),
    path('delete_vendor/<int:vendor_id>/', views.delete_vendor, name='delete_vendor'),  
    path('show_vendor/<int:id>/',views.show_vendor , name="show_vendor"),


    path('add_transporter',views.add_transporter , name="add_transporter"),
    path('fn_transporter_List_View/',views.fn_transporter_List_View , name="fn_transporter_List_View"),
    path('edit_transporter/<int:transporter_id>/', views.edit_transporter, name='edit_transporter'),
    path('delete_transporter/<int:transporter_id>/', views.delete_transporter, name='delete_transporter'),

    path('godown_list',views.godown_list_view , name="godown_list"),
    path('godown_add',views.add_godown_data , name="godown_add"),
    path('delete_godown/<int:id>/',views.delete_godown_data, name="delete_godown"),
    path('edit_godown/<int:id>/',views.edit_godown_data, name="edit_godown"),
    path('godown_view/<int:id>/',views.godown_view, name="godown_view"),


    path('designation_list', views.designation_list_view, name = "designation_list"),
    path('designation_add', views.add_designation_data, name = "designation_add"),
    path('edit_designation/<int:id>/',views.edit_designation_data, name="edit_designation"),
    path('delete_designation/<int:id>/',views.delete_designation_data, name="delete_designation"),

    path('department_list', views.department_list_view, name = "department_list"),
    path('department_add', views.add_department_data, name = "department_add"),
    path('edit_department/<int:id>/',views.edit_department_data, name="edit_department"),
    path('delete_department/<int:id>/',views.delete_department_data, name="delete_department"),

    path('leave_type_list', views.leave_type_list_view, name = "leave_type_list"),
    path('leave_type_add', views.add_leave_type_data, name = "leave_type_add"),
    path('edit_leave_type/<int:id>/',views.edit_leave_type_data, name="edit_leave_type"),
    path('delete_leave_type/<int:id>/',views.delete_leave_type_data, name="delete_leave_type"),
   
    path('add_banking/',views.add_banking , name="add_banking"),
    path('fn_banking_List_View/',views.fn_banking_List_View , name="fn_banking_List_View"),
    path('edit_banking/<int:banking_id>/', views.edit_banking, name='edit_banking'),
    path('delete_banking/<int:banking_id>/', views.delete_banking, name='delete_banking'),    


    path('add_employee/',views.add_employee , name="add_employee"),
    path('fn_employee_List_View/',views.fn_employee_List_View , name="fn_employee_List_View"),
    path('edit_employee/<int:employee_id>/', views.edit_employee, name='edit_employee'),
    path('delete_employee/<int:employee_id>/', views.delete_employee, name='delete_employee'),

    path('add_holiday/',views.fn_holiday_add , name="add_holiday"),
    path('holiday_List_View/',views.fn_holiday_List_View , name="holiday_List_View"),
    path('edit_holiday/<int:holiday_id>/', views.fn_holiday_edit, name='edit_holiday'),
    path('delete_holiday/<int:holiday_id>/', views.delete_holiday, name='delete_holiday'), 

    path('add_hr_leaves/',views.add_employee_leaves , name="add_hr_leaves"),
    path('hr_leaves_List_View/',views.fn_employee_leave_List , name="hr_leaves_List_View"),
    path('edit_hr_leaves/<int:id>/', views.edit_employee_leaves, name='edit_hr_leaves'),
    path('delete_hr_leaves/<int:id>/', views.delete_employee_leaves, name='delete_hr_leaves'), 
    
   
    path('add_emp_slary/',views.add_employee_salary , name="add_emp_slary"),
    path('fn_emp_salary_List/',views.fn_employee_salary_List , name="fn_emp_salary_List"),
    path('edit_emp_sal/<int:employee_id>/', views.edit_employee_salary, name='edit_emp_sal'),
    path('delete_emp_sal/<int:employee_id>/', views.delete_employee_salary, name='delete_emp_sal'),
     
#Company Profile
    path('add_company_profile/',views.add_company_profile , name="add_company_profile"),
    path('fn_company_profile_List/',views.fn_company_profile_List , name="fn_company_profile_List"),
    path('edit_company_profile/<int:employee_id>/', views.edit_company_profile, name='edit_company_profile'),
    path('delete_company_profile/<int:employee_id>/', views.delete_company_profile, name='delete_company_profile'),
   
    #Cash VOucher
    path('add_cash_voucher/',views.add_cash_voucher , name="add_cash_voucher"),
    path('fn_cash_coucher_List_View/',views.fn_cash_coucher_List_View , name="fn_cash_coucher_List_View"),
    path('edit_cash_voucher/<int:voucher_id>/', views.edit_cash_voucher, name='edit_cash_voucher'),
    path('delete_cash_voucher/<int:voucher_id>/', views.delete_cash_voucher, name='delete_cash_voucher'),
   

    #Expense
    path('add_expense_vendor_data/',views.add_expense_vendor_data , name="add_expense_vendor_data"),
    path('expense_vendor_list/',views.expense_vendor_list , name="expense_vendor_list"),
    path('edit_expense_vendor_data/<int:id>/', views.edit_expense_vendor_data, name='edit_expense_vendor_data'),
    path('delete_expense/<int:expense_vendor_id>/', views.delete_expense_vendor_data, name='delete_expense'),
    # path('getitemscodedetails/', views.get_item_code_details, name='getitemscodedetails'),
    
    
    ###  Expense Advice
    path('add_expense_advice_data/',views.fnadd_expense_advice , name="add_expense_advice_data"),
    path('expense_advice_list_View/',views.fn_expense_advice_list_View , name="expense_advice_list_View"),
    path('edit_expense_advice/<int:advice_id>/', views.fnedit_expense_advice, name='edit_expense_advice'),
    path('delete_expenses_advice/<int:advice_id>/', views.delete_expenses_advice, name='delete_expenses_advice'),
    path('get_related_fields/', views.get_vendor_expenses, name='get_related_fields'),
    path('enter-date/', views.display_data, name='enter_date'),
    # path('download/', views.download_pdf, name='download_pdf'),


    ###Report Url

    path('credit_note/', views.credit_note_report, name='credit_note'),
    path('credit_note_date/', views.credit_note_date, name='credit_note_date'),
    path('download_credit_note_excel/', views.download_credit_note_excel, name='download_credit_note_excel'),



    path('debit_note/', views.debit_note_report, name='debit_note'),
    path('debit_note_date/', views.debit_note_date, name='debit_note_date'),
    path('download_debit_note_excel/', views.download_debit_note_excel, name='download_debit_note_excel'),

    path('inventory_date/', views.inventory_summery, name='inventory_date'),
    path('download_inventory_excel/', views.download_inventory_excel, name='download_inventory_excel'),
    path('sales_register_date/', views.sales_register_date, name='sales_register_date'),
    path('purchase_register_date/', views.purchase_register_date, name='purchase_register_date'),

    path('customer_outstanding/', views.customer_outstanding, name='customer_outstanding'),
    path('vendor_outstanding/', views.vendor_outstanding, name='vendor_outstanding'),
    path('hsn_wise/', views.hsn_wise_date, name='hsn_wise'),
    path('expenses_report_date/', views.expenses_report_date, name='expenses_report_date'),


    path('inventory_division_date/', views.inventory_division_date, name='inventory_division_date'),

    path('cash_voucher_date/', views.cash_voucher_date, name='cash_voucher_date'),

    path('add_quotation/', views.add_quotation_data, name = "add_quotation"),
    path('getitemscodedetails/', views.get_item_code_details, name='getitemscodedetails'),
    path('quotation_list', views.quotation_list_view, name = "quotation_list"),
    path('edit_quotation/<int:id>/', views.edit_quotation_data, name='edit_quotation'),
    path('delete_quotation/<int:id>/', views.delete_quotation_data, name='delete_quotation'),
    path('check_duplicate_quotation_no/', views.check_duplicate_quotation_no, name='check_duplicate_quotation_no'),
    path('check_duplicate_challan_no/', views.check_duplicate_challan_no, name='check_duplicate_challan_no'),


    path('add_sales_order/', views.add_sales_order_data, name = "add_sales_order"),
    path('sales_order_list/', views.sales_order_list_view, name = "sales_order_list"),
    path('edit_sales_order/<int:id>/', views.edit_sales_order_data, name='edit_sales_order'),
    path('delete_sales_order/<int:id>/', views.delete_sales_order_data, name='delete_sales_order'),
    path('download_sales_order_pdf/<int:id>/', views.download_sales_order_pdf, name='download_sales_order_pdf'),
    


    path('delivery_challan_list', views.deliverychallan_list_view, name = "delivery_challan_list"),
    path('add_delivery_challan/', views.add_deliverychallan_data, name = "add_delivery_challan"),
    path('delete_challan/<int:id>/', views.delete_challan_data, name='delete_challan'),
    path('edit_challan/<int:id>/', views.edit_delivery_challan_data, name='edit_challan'),


    path('add_invoice_data/', views.add_invoice_data, name = 'add_invoice_data'),
    path('invoice_list/', views.invoice_list_view, name = 'invoice_list'),
    path('edit_invoice/<int:id>/', views.edit_invoice_data, name='edit_invoice'),
    path('delete_invoice/<int:id>/', views.delete_invoice_data, name='delete_invoice'),
    path('check_duplicate_invoice_no/', views.check_duplicate_invoice_no, name='check_duplicate_invoice_no'),
    
    path('check_inventory_stock/', views.check_inventory_stock, name='check_inventory_stock'),
    path('check_inventory_stock_edit/', views.check_inventory_stock_edit, name='check_inventory_stock_edit'),
    path('check_duplicate_performa_invoice_no/', views.check_duplicate_performa_invoice_no, name='check_duplicate_performa_invoice_no'),


    path('creditnotes_list/', views.credit_notes_list_view, name = 'creditnotes_list'),
    path('add_creditnotes/', views.add_credit_notes_data, name = 'add_creditnotes'),
    path('edit_creditnotes/<int:id>', views.edit_credit_notes_data, name = 'edit_creditnotes'),

    path('payment_received_list/', views.paymentreceived_list_view, name='payment_received_list'),
    path('add_paymentreceived_data/', views.add_payment_received_data, name='paymentreceived_add'),
    path('delete_payment_received/<int:id>/', views.delete_payment_received_data, name='delete_payment_received'),
    path('edit_paymentreceived/<int:id>', views.edit_payment_received_data, name = 'edit_paymentreceived'),
   
    # path('get_emp_leave/<str:emp_name>/', views.get_emp_leave, name='get_emp_leave'),



    path('getitemscodedetails_1/', views.getitemscodedetails_1, name='getitemscodedetails_1'),

    ##########################################################################################

    

    path('purchase_order_list/', views.purchaseorder_list_view, name='purchase_order_list'),
    path('add_purchase_order/', views.add_purchase_order_data, name='add_purchase_order'),
    path('edit_purchase_order/<int:id>', views.edit_purchase_order_data, name='edit_purchase_order'),
    path('delete_purchase_order/<int:id>/', views.delete_purchase_order_data, name='delete_purchase_order'),
    path('check_duplicate_purchase_order_no/', views.check_duplicate_purchase_order_no, name='check_duplicate_purchase_order_no'),


    path('grn_list/', views.grn_list_view, name='grn_list'),
    path('add_good_note/', views.add_good_note_data, name='add_good_note'),
    path('edit_good_note/<int:id>/', views.edit_good_note_data, name='edit_good_note'),


    path('purchase_invoice_list/', views.purchaseinvoice_list_view, name='purchase_invoice_list'),
    path('add_purchase_invoice/', views.add_purchaseinvoice_data, name='add_purchase_invoice'),
    path('edit_purchase_invoice/<int:id>', views.edit_purchaseinvoice_data, name='edit_purchase_invoice'),
    path('delete_purchase_invoice/<int:id>', views.delete_purchaseinvoice_data, name='delete_purchase_invoice'),

    # Del path('expense_vendor_list_new/', views.add_expense_data, name='expense_vendor_list_new'),

    # Del path('expense_new_list/', views.expense_list_view, name='expense_new_list'),

### For sales order report
    path('sales_order_disply/', views.display_items_by_date_range, name='sales_order_disply'),
    path('sales_order_report_date/', views.sales_order_report_date, name='sales_order_report_date'),
### For sales register report
    path('sales_register_disply/', views.sales_display_items_by_date_range, name='sales_register_disply'),
    path('sales_register_report_date/', views.sales_register_date, name='sales_register_report_date'),
    path('check_duplicate_sales_order_no/', views.check_duplicate_sales_order_no, name='check_duplicate_sales_order_no'),


### For Purchase register report
    path('purchase_register_disply/', views.display_purchase_register_date_range, name='purchase_register_disply'),
    path('purchase_register_report_date/', views.purchase_register_date, name='purchase_register_report_date'),

### For HSN wise report
    path('hsn_wise_disply/', views.display_purchase_register_date_range, name='purchase_register_disply'),
    path('hsn_wise_report_date/', views.purchase_register_date, name='purchase_register_report_date'),


### For cash voucher report
    path('cash_voucher_display_report/', views.display_cash_voucher_by_date_range, name='cash_voucher_display_report'),
### For invoice voucher report

    path('invoice_display_report/', views.display_invoice_by_date_range, name='invoice_display_report'),
### For inventory voucher report

    path('inventory_summery_report/', views.display_inventory_summenry_date_range, name='inventory_summery_report'),
### For purchase voucher report
    path("get_companies_by_date/", views.get_companies_by_date, name="get_companies_by_date"),

    path('purchase_voucher_report/', views.display_purchase_register_date_range, name='purchase_voucher_report'),

    # path('add_expense_advice1/',views.add_expence1 , name="add_expense_advice1"),


    # # path('get_emp_leave/<str:emp_name>/', views.get_emp_leave, name='get_emp_leave'),
    path('admin_home/', views.admin_home, name='admin_home'),

    path('vendor_doc/', views.upload_vendor_doc, name = 'vendor_doc'),
    path('inventory_doc/', views.upload_inventory_doc, name = 'inventory_doc'),
    path('customer_doc/', views.upload_customer_doc, name = 'customer_doc'),
    path('get_customerinvoice_data/', views.get_customer_invoice_details, name = 'get_customerinvoice_data'),
#for try
    # path('test/', views.ser_exp, name = 'test'),
###### Foir PDF
    path('show_quo_pdf/<int:id>/', views.quotation_pdf, name='show_quo_pdf'),
    path('download_qou_pdf/<int:id>/', views.download_qou_pdf, name='download_qou_pdf'),
    path('show_pdf/<int:id>/', views.show_pdf, name='quo_pdf'),
    path('sales_show_pdf/<int:id>/', views.show_pdf, name='sales_show_pdf'),
    path('credit_note_pdf/<int:id>/', views.credit_show_pdf, name='credit_note_pdf'),
    path('payment_show_pdf/<int:id>/', views.payment_pdf, name='payment_show_pdf'),
    path('purchase_ord_show_pdf/<int:id>/', views.purchase_show_pdf, name='purchase_ord_show_pdf'),

    path('invoice_show_pdf/<int:id>/', views.invoice_pdf, name='invoice_show_pdf'),
    
    path('delivery_challan_pdf/<int:id>/', views.delivery_chalan_pdf, name='delivery_challan_pdf'),

    path('download_delivery_chalan_pdf/<int:id>/', views.download_delivery_chalan_pdf, name='download_delivery_chalan_pdf'),

    path('cvoucher_show_pdf/<int:id>/', views.cvoucher_show_pdf, name='cvoucher_show_pdf'),

    path('exgetitemscodedetails/', views.getitemscodedetails_1, name = 'exgetitemscodedetails'),    

    # path('getexpenseadvice/', views.get_expense_advice_details, name='getexpenseadvice'),


    path('add_inventory',views.inventory_data_add , name="add_inventory"),
    path('inventory_list_data',views.inventory_list , name="inventory_list_data"),
    path('delete_inv_item/<int:id>/',views.delete_inentory_item , name="delete_inv_item"),
    path('view_inventory_entity/<int:id>/',views.inventory_overview , name="view_inventory_entity"),
    path('edit_inventory/<int:id>/',views.inventory_edit , name="edit_inventory"),

 # purchase performa invoice

    path('performa_add_invoice_data/', views.performa_add_invoice_data, name = 'performa_add_invoice_data'),
    path('performa_invoice_list/', views.performa_invoice_list_view, name = 'performa_invoice_list'),
    path('performa_edit_invoice/<int:id>/', views.performa_edit_invoice_data, name='performa_edit_invoice'),
    path('performa_invoice_show_pdf/<int:id>/', views.performa_invoice_show_pdf, name='performa_invoice_show_pdf'),
    path('download_performa_invoice_show_pdf/<int:id>/', views.download__performa_invoice_show_pdf, name='download_performa_invoice_show_pdf'),
    path('delete_per_invoice_data/<int:id>/', views.delete_per_invoice_data, name='delete_per_invoice_data'),
   

    path('autocomplete/', views.autocomplete_customer_name, name='autocomplete_customer_name'),
    path('get_customer_details/', views.get_customer_details, name='get_customer_details'),
    path('update_invstatus/<int:id>/', views.update_Instatus_view, name='update_invstatus'),
# Debit Note
    path('debitnotes_list/', views.debit_notes_list_view, name = 'debitnotes_list'),
    path('add_debitnotes/', views.add_debit_notes_data, name = 'add_debitnotes'),
    path('edit_debitnotes/<int:id>', views.edit_debit_notes_data, name = 'edit_debitnotes'),
    path('delete_credit/<int:id>/', views.delete_credit_data, name='delete_credit'),
    path('delete_debit_data/<int:id>/', views.delete_debit_data, name='delete_debit_data'),
    path('download_debit_note_pdf/<int:id>/', views.download_debit_note_pdf, name = 'download_debit_note_pdf'),
    path('debit_show_pdf/<int:id>/', views.debit_show_pdf, name='debit_show_pdf'),

####### Leads
    path('add_leads/', views.add_leads_data, name = 'add_leads'),
    path('lead_list/', views.lead_list_view, name = 'lead_list'),
    path('edit_lead/<int:lead_id>/', views.edit_lead_data, name='edit_lead'),
    path('delete_lead/<int:id>/', views.delete_lead_data, name='delete_lead'),
    path('update_status/', views.update_status, name='update_status'),

    path('download_excel/', views.download_excel, name='download_excel'),
    path('customer_oustanding_date/', views.customer_oustanding_date, name='customer_oustanding_date'),
    path('purchase_register_detail/<int:id>/', views.purchase_register_detail, name='purchase_register_detail'),
    path('download_credit_note_pdf/<int:id>/',views.download_credit_note_pdf, name='download_credit_note_pdf'),
    path('download_invoice_pdf/<int:id>/', views.download_invoice_pdf, name='download_invoice_pdf'),
    path('purchsae_download_pdf/<int:id>/', views.purchsae_download_pdf, name='purchsae_download_pdf'),
    

    path('get-quotation-items/<int:quotation_id>/', views.get_quotation_items, name='get_quotation_items'),
    path('get-sales_order-items/<int:quotation_id>/', views.get_sales_order_items, name='get_sales_order_items'),
    path('get_dc_order_items/<int:quotation_id>/', views.get_dc_order_items, name='get_dc_order_items'),
    path('get_shipping_address/', views.get_shipping_address, name='get_shipping_address'),

]


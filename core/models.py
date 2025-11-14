from django.db import models

# Create your models here.
class customer(models.Model):
    gender =  models.CharField(max_length=200, blank=True, null=True)
    customer = models.CharField(max_length=200)
    cust_email = models.EmailField()
    company_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=255)
    display_name = models.CharField(max_length=200,blank=True, null=True)
    website = models.URLField(max_length=200, blank=True, null=True)
    mobile  = models.CharField(max_length=20)
    lead_id = models.CharField(max_length=20,default=0)

    gst_treatment = models.CharField(max_length=200)
    gst_number = models.CharField(max_length=15,blank=True, null=True)
    state = models.CharField(max_length=200)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    pan_number = models.CharField(max_length=10, blank=True, null=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    credit_limit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    attention = models.CharField(max_length=255, blank=True, null=True)
    street = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    com_state = models.CharField(max_length=50, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    gst_uin = models.CharField(max_length=50, blank=True, null=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True)

    shipping_1_attention = models.CharField(max_length=255, blank=True, null=True)
    shipping_1_street = models.CharField(max_length=255, blank=True, null=True)
    shipping_1_city = models.CharField(max_length=50, blank=True, null=True)
    shipping_1_state = models.CharField(max_length=50, blank=True, null=True)
    shipping_1_pincode = models.CharField(max_length=10, blank=True, null=True)
    shipping_1_gst_uin = models.CharField(max_length=50, blank=True, null=True)
    shipping_1_contact_number = models.CharField(max_length=15, blank=True, null=True)
   
    shipping_2_attention = models.CharField(max_length=255, blank=True, null=True)
    shipping_2_street = models.CharField(max_length=255, blank=True, null=True)
    shipping_2_city = models.CharField(max_length=50, blank=True, null=True)
    shipping_2_state = models.CharField(max_length=50, blank=True, null=True)
    shipping_2_pincode = models.CharField(max_length=10, blank=True, null=True)
    shipping_2_gst_uin = models.CharField(max_length=50, blank=True, null=True)
    shipping_2_contact_number = models.CharField(max_length=15, blank=True, null=True)

    shipping_3_attention = models.CharField(max_length=255, blank=True, null=True)
    shipping_3_street = models.CharField(max_length=255, blank=True, null=True)
    shipping_3_city = models.CharField(max_length=50, blank=True, null=True)
    shipping_3_state = models.CharField(max_length=50, blank=True, null=True)
    shipping_3_pincode = models.CharField(max_length=10, blank=True, null=True)
    shipping_3_gst_uin = models.CharField(max_length=50, blank=True, null=True)
    shipping_3_contact_number = models.CharField(max_length=15, blank=True, null=True)
  
    shipping_4_attention = models.CharField(max_length=255, blank=True, null=True)
    shipping_4_street = models.CharField(max_length=255, blank=True, null=True)
    shipping_4_city = models.CharField(max_length=50, blank=True, null=True)
    shipping_4_state = models.CharField(max_length=50, blank=True, null=True)
    shipping_4_pincode = models.CharField(max_length=10, blank=True, null=True)
    shipping_4_gst_uin = models.CharField(max_length=150, blank=True, null=True)
    shipping_4_contact_number = models.CharField(max_length=15, blank=True, null=True)

    bank_name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=20)
    branch_name = models.CharField(max_length=255)
    ifsc_code = models.CharField(max_length=11)
    due_date = models.DateField(null=True)
    banking_address = models.CharField(max_length=200,null=True,blank=True)
    customer_code =models.CharField(max_length=256,verbose_name="Customer Code",null=True,blank=True)
    licence_no = models.CharField(max_length=256,verbose_name="Licence No",null=True,blank=True)

    class Meta:
        db_table = 'customer'

    def get_full_address_customer(self):
        return f"{self.pincode}, {self.city}".strip(", ")

    def save(self,*args,**kwargs):

        if self._state.adding:
            last_emp = customer.objects.order_by('-id').first()
            if last_emp and last_emp.customer_code:
                last_number = int(last_emp.customer_code.split('_')[1])
            else:
                last_number = 0  # Start with 10000 if no previous employee exists
            self.customer_code = 'KC_{:03d}'.format(last_number + 1)       
        super().save(*args,**kwargs)

class vendor(models.Model):
    gender =  models.CharField(max_length=200, blank=True, null=True)
    contact_person = models.CharField(max_length=200)
    vendor_email = models.EmailField()
    company_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=255)
    display_name = models.CharField(max_length=200,blank=True, null=True)
    website = models.URLField(max_length=200, blank=True, null=True)
    mobile  = models.CharField(max_length=20,null=True)
    receive_amount = models.FloatField(default=0.00)
   
    gst_treatment = models.CharField(max_length=200,null=True)
    gst_number = models.CharField(max_length=15, null=True,blank=True)
    state = models.CharField(max_length=200,null=True)
    balance = models.CharField(max_length=255, default=0.00,null=True)
    pan_number = models.CharField(max_length=10,null=True)    
    
    delivery_company_name = models.CharField(max_length=255, blank=True, null=True)
    street = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    delivery_state = models.CharField(max_length=50, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    gst_uin = models.CharField(max_length=15, blank=True, null=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True)

    vendor_company_name = models.CharField(max_length=255, blank=True, null=True)
    vendor_street = models.CharField(max_length=255, blank=True, null=True)
    vendor_city = models.CharField(max_length=50, blank=True, null=True)
    vendor_state = models.CharField(max_length=50, blank=True, null=True)
    vendor_pincode = models.CharField(max_length=10, blank=True, null=True)
    vendor_gst_uin = models.CharField(max_length=15, blank=True, null=True)
    vendor_contact_number = models.CharField(max_length=15, blank=True, null=True)   
   
    bank_name = models.CharField(max_length=255,null=True)
    account_number = models.CharField(max_length=20,null=True)
    branch_name = models.CharField(max_length=255,null=True)
    ifsc_code = models.CharField(max_length=11,null=True)
    due_date = models.DateField(null=True)
    vendor_code =models.CharField(max_length=256,verbose_name="Vendor Code",null=True,blank=True)
    licence_no = models.CharField(max_length=256,verbose_name="Licence No",null=True,blank=True)


    class Meta:
        db_table = 'vendor'

    def save(self,*args,**kwargs):

        if self._state.adding:
            last_emp = vendor.objects.order_by('-id').first()
            if last_emp and last_emp.vendor_code:
                last_number = int(last_emp.vendor_code.split('_')[1])
            else:
                last_number = 0  # Start with 10000 if no previous employee exists
            self.vendor_code = 'VC_{:03d}'.format(last_number + 1)       
        super().save(*args,**kwargs)

    def get_full_address(self):
        return f"{self.vendor_pincode}, {self.city}".strip(", ")

class transporter(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    gst_no = models.CharField(max_length=15, blank=True, null=True)
    bank_name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=20)
    branch_name = models.CharField(max_length=255)
    mobile  = models.CharField(max_length=20)
    vendor_email = models.EmailField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    ifsc_code = models.CharField(max_length=255)


    
    class Meta:
        db_table = 'transporter'

class godown(models.Model):
    # name = models.CharField(max_length=200)
    date = models.DateField(auto_now_add=True)
    city_name = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        db_table = 'godown'

class designation(models.Model):
    name = models.CharField(max_length=200)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'designation'

class department(models.Model):
    name = models.CharField(max_length=200)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'department'
class leave_type(models.Model):
    name = models.CharField(max_length=200, unique=True)
    count = models.IntegerField(null=True)
    date = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'leave_type'
class banking(models.Model):
    account_name = models.CharField(max_length=20)
    bank_name = models.CharField(max_length=255)
    ifsc_code = models.CharField(max_length=11)
    account_code = models.CharField(max_length=11)
    branch_name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    account_number = models.CharField(max_length=20)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    pending = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20)

    class Meta:
        db_table = 'banking'

class employee(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    joining_date = models.DateField()
    phone = models.CharField(max_length=20)
    department = models.ForeignKey(department,on_delete=models.CASCADE, null=True,blank=True)
    designation = models.ForeignKey(designation,on_delete=models.CASCADE, null=True,blank=True)   
    address = models.TextField()
    bank_name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=50)
    upload_photo = models.ImageField(upload_to='employee_photos/',null=True,blank=True)
    status = models.CharField(max_length=20, default='Active')
    earned_leaves = models.FloatField(null=True)
    casual_leaves = models.FloatField(null=True)
    ifsc_code = models.CharField(max_length=250,null=True,blank=True)
    leaves_allocated = models.FloatField(null=True, default=0.00)


    class Meta:
        db_table = 'employee'

class holiday(models.Model):
    holiday_name = models.CharField(max_length=255)
    from_date = models.DateField()
    to_date = models.DateField()
    no_days = models.IntegerField(null=True)
    
    class Meta:
        db_table = 'holiday'

class Hrleaves(models.Model):
    employee_name = models.ForeignKey(employee,on_delete=models.CASCADE, null=True,blank=True)
    leave_type = models.CharField(max_length=200,null=True)
    from_date = models.DateField()
    to_date = models.DateField()
    no_days = models.FloatField(null=True)
    remaining_days = models.FloatField(null=True)   
    leave_reason = models.CharField(max_length=200)

    class Meta:
        db_table = 'Hrleaves'

class employee_salary(models.Model):
    employee_name = models.ForeignKey(employee, on_delete=models.CASCADE, related_name='employee_salary')
    ctc = models.DecimalField(max_digits=10, decimal_places=2,null=True)
    hra = models.DecimalField(max_digits=10, decimal_places=2,null=True)
    esic = models.DecimalField(max_digits=10, decimal_places=2,null=True)
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2,null=True)
    conveyance_allowance = models.DecimalField(max_digits=10, decimal_places=2,null=True)
    flexible_component = models.DecimalField(max_digits=10, decimal_places=2,null=True)
    variable_component = models.DecimalField(max_digits=10, decimal_places=2)
    provident_fund = models.DecimalField(max_digits=10, decimal_places=2)
    professional_tax = models.DecimalField(max_digits=10, decimal_places=2)
    income_tax = models.DecimalField(max_digits=10, decimal_places=2,default='00')
    other_deductions = models.DecimalField(max_digits=10, decimal_places=2)
    gross_salary = models.DecimalField(max_digits=10, decimal_places=2)
    total_deductions = models.DecimalField(max_digits=10, decimal_places=2)
    net_salary = models.DecimalField(max_digits=10, decimal_places=2)
    other_allowns = models.DecimalField(max_digits=10,decimal_places=2,default='00')
    lwf = models.DecimalField(max_digits=10,decimal_places=2,default='00')
    days_payable = models.IntegerField()
    days_paid = models.IntegerField(null=True)
    month = models.CharField(max_length=30,null=True)

    class Meta:
        db_table = 'employee_salary'


class Settings(models.Model):
    profile_photo = models.ImageField(upload_to='Company_profile/',null=True,blank=True)
    company_name = models.CharField(max_length=255,null=True)
    organization_type = models.CharField(max_length=255,null=True)
    fiscal_year = models.CharField(max_length=255,null=True)
    industry = models.CharField(max_length=255,null=True)
    currency = models.CharField(max_length=255,null=True)
    address1 = models.CharField(max_length=255,null=True)
    address2 = models.CharField(max_length=255,null=True)
    pincode = models.CharField(max_length=255,null=True)
    email = models.EmailField()
    phone = models.CharField(max_length=200,null=True)
    com_website = models.URLField(max_length=200, blank=True, null=True)
    upload_sign = models.ImageField(upload_to='Upload_sign/',null=True,blank=True)
    upload_QR_code = models.ImageField(upload_to='Upload_OR_Code/',null=True,blank=True)
    status = models.CharField(max_length=200, default='Active')
    gst_number = models.CharField(max_length=150, null=True)
    pan_number = models.CharField(max_length=255, null=True)    
    tan_number = models.CharField(max_length=255, null=True)    
    cin_number = models.CharField(max_length=21, null=True)

    class Meta:
        db_table = 'Settings'


class cash_voucher(models.Model):
    voucher_number = models.CharField(max_length=255, null=True)
    date = models.DateField(null=True)
    amount = models.IntegerField(null=True)
    pay_to = models.CharField(max_length=255, null=True)
    particular = models.CharField(max_length=255, null=True)
    cost_centre = models.CharField(max_length=255, null=True)
    bill_no = models.CharField(max_length=255, null=True)
    bill_date = models.DateField(null=True)
    remark = models.CharField(max_length=255, null=True)
    balance = models.IntegerField(null=True)

    class Meta:
        db_table = 'cash_voucher'
        ordering = ['-id']

class expense_vendor(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    ex_vendor_name = models.ForeignKey(vendor,on_delete=models.CASCADE, null=True)
    ex_invoice_date = models.DateField(null=True)
    ex_gst_number = models.CharField(max_length=255, null=True,blank=True)
    ex_freight = models.DecimalField(max_digits=10, decimal_places=2, null=True,blank=True)
    all_total = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    terms_condition = models.CharField(max_length=25, null=True)

    class Meta:
        db_table = 'expense_vendor'


class expense_item(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    ex_item_code = models.CharField(max_length=256)
    ex_description_goods = models.CharField(max_length=256)
    ex_hsn = models.CharField(max_length=256)
    ex_qantity = models.CharField(max_length=256)
    ex_uom = models.CharField(max_length=256)
    ex_unit_price = models.CharField(max_length=256)
    ex_discount = models.CharField(max_length=256)
    ex_tax_rate = models.CharField(max_length=125)
    ex_tax_amount = models.CharField(max_length=125)
    ex_total = models.CharField(max_length=255)
    ex_expense_id = models.CharField(max_length=255)

    class Meta:
        db_table = 'expense_item'



class expense_advice(models.Model):
    ea_deposit = models.ForeignKey(vendor, on_delete=models.CASCADE, null=True, related_name='expenses')
    ea_vendor = models.ForeignKey(vendor,on_delete=models.CASCADE, null=True)
    ea_date = models.DateField(null=True)
    ea_payment_mode = models.CharField(max_length=50, null=True)
    ea_mobile = models.CharField(max_length=20, null=True)
    ea_balance = models.CharField(max_length=50, null=True)
    ea_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    ea_expense_advice_no = models.CharField(max_length=50, null=True)
    ea_bank_charges = models.CharField(max_length=10,  null=True, blank=True)
    ea_cheque_no = models.CharField(max_length=50, null=True, blank=True)
    ea_cheque_date = models.DateField(null=True, blank=True)
    ea_reference = models.CharField(max_length=100, null=True, blank=True)
    ea_po_no = models.CharField(max_length=50, null=True, blank=True)
    ea_note = models.TextField(null=True, blank=True)
    ea_payment = models.CharField(max_length=10,  null=True)
    ea_due_amount = models.CharField(max_length=10,  null=True)
    ea_total = models.CharField(max_length=10, null=True)
    ea_amount_received = models.CharField(max_length=10, null=True)
    ea_amount_used = models.CharField(max_length=10, null=True)
    ea_amount_excess = models.CharField(max_length=10, null=True)
    ea_advice_no = models.CharField(max_length=10, null=True)



    class Meta:
        db_table = 'expense_advice'

class expense_advice_item(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    ea_date = models.DateField(null=True)
    vendor = models.CharField(max_length=50, null=True, blank=True)
    ea_invoice_no = models.CharField(max_length=50, null=True, blank=True)
    ea_invoice_amt = models.CharField(max_length=50, null=True, blank=True)
    ea_payment_receive = models.CharField(max_length=50, null=True, blank=True)
    ea_due_amount = models.CharField(max_length=50, null=True, blank=True)
    ea_payment = models.CharField(max_length=50, null=True, blank=True)
    ex_expense_adv_id = models.CharField(max_length=100)

    class Meta:
        db_table = 'expense_advice_item'






class credit_note(models.Model):
    date = models.DateField(null=True)
    creditnote = models.CharField(max_length=50, null=True, blank=True)
    voucher_type = models.CharField(max_length=50, null=True, blank=True)
    voucher_no = models.CharField(max_length=50, null=True, blank=True)
    credit = models.FloatField(null=True)
    debit = models.FloatField(null=True)

    class Meta:
        db_table = 'credit_note'

class payment_made(models.Model):
    date = models.DateField(null=True)
    perticularnote = models.CharField(max_length=50, null=True, blank=True)
    voucher_type = models.CharField(max_length=50, null=True, blank=True)
    voucher_no = models.CharField(max_length=50, null=True, blank=True)
    credit = models.FloatField(null=True)
    debit = models.FloatField(null=True)

    class Meta:
        db_table = 'payment_made'



class quotation(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    q_date = models.DateField()
    q_payment_terms = models.CharField(max_length=256, blank=True)
    q_customer_name = models.ForeignKey(customer, on_delete=models.CASCADE, null=True, blank=True)
    q_expiry_date = models.DateField(blank=True)
    q_supply_place = models.CharField(max_length=256,blank=True)
    q_destination = models.CharField(max_length=256,blank=True)
    q_delivery = models.CharField(max_length=256,blank=True)    
    q_contact_person_name = models.CharField(max_length=256,blank=True)
    q_contact_person_email = models.EmailField(blank=True)
    q_reference = models.CharField(max_length=256,blank=True)
    q_packing = models.CharField(max_length=256,blank=True)
    q_dispatch = models.ForeignKey(transporter, on_delete=models.CASCADE, null=True, blank=True)
    q_sub_total = models.CharField(max_length=255,blank=True)
    q_cgstper = models.CharField(max_length=255,blank=True)
    q_cgstval = models.CharField(max_length=255,blank=True)
    q_sgstper = models.CharField(max_length=255,blank=True)
    q_sgstval = models.CharField(max_length=255,blank=True)
    q_igstper = models.CharField(max_length=255,blank=True)
    q_igstval = models.CharField(max_length=255,blank=True)
    q_adjustment = models.CharField(max_length=255,blank=True)
    q_sale_of_good = models.CharField(max_length=255,blank=True)
    q_note = models.TextField(blank=True)
    q_total = models.CharField(max_length=255,blank=True)
    # q_packaging_forwording_amount = models.CharField(max_length=512,blank=True)
    # q_packaging_forwording_percentage = models.CharField(max_length=512,blank=True)
    # q_freight_amount = models.CharField(max_length=255,blank=True)
    q_packaging_forwording_amount = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True
    )
    q_packaging_forwording_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True
    )
    q_freight_amount = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True
    )
    q_freight_percentage = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    gst_option= models.CharField(null=True,max_length=255)
    q_packaging_forwording_percentage_amt = models.CharField(max_length=512,blank=True)
    q_freight_percentage_amt = models.CharField(max_length=255,blank=True)
    q_total_amt_word = models.CharField(max_length=250,blank=True)
    q_quotation_number = models.CharField(max_length=250,blank=True)
    q_packaging_forwording_amt_amt = models.CharField(max_length=512,blank=True)
    q_freight_percentage_amt_amt = models.CharField(max_length=255,blank=True)
    q_customer_code = models.CharField(max_length=255,blank=True)





class quotation_items(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    q_item_code = models.CharField(max_length=256)
    q_description_goods = models.CharField(max_length=256, null=True)
    q_hsn = models.CharField(max_length=256)
    q_qantity = models.CharField(max_length=256)
    q_uom = models.CharField(max_length=256)
    q_unit_price = models.CharField(max_length=256)
    q_discount = models.CharField(max_length=256)
    q_tax_rate = models.CharField(max_length=125)
    q_tax_amount = models.CharField(max_length=125)
    q_total = models.CharField(max_length=255)
    q_quotation_id = models.CharField(max_length=255)


class inventory(models.Model):
    inventory_name = models.CharField(max_length=500)
    item_code = models.CharField(max_length=255)
    units = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    tax_type = models.CharField(max_length=255)
    # intrastate_gst = models.CharField(max_length=255)
    # interstate_gst = models.CharField(max_length=255)
    hsn = models.CharField(max_length=255)
    sku = models.CharField(max_length=255)
    default_discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    division_no = models.CharField(max_length=255,null=True,blank=True)
    sales_checkbox = models.BooleanField(default=True)
    sales_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    sales = models.CharField(max_length=255)
    sales_information_description = models.CharField(max_length=512)
    purchase_information = models.CharField(max_length=12)
    purchase_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    purchase = models.CharField(max_length=255)
    purchase_information_description = models.CharField(max_length=512)
    opening_stock_quantity = models.CharField(max_length=512, default=0)
    opening_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    unit_per_case = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    stock_account = models.CharField(max_length=512, default=0,null=True,blank=True)
    date = models.DateField(null=True)
    # gst_option= models.CharField(null=True,max_length=255)
    godown_name_old = models.CharField(max_length=512, null=True,blank=True)
    # Tax_rate = models.CharField(max_length=255, null=True,blank=True)
    inventory_godown = models.ForeignKey(godown, on_delete=models.CASCADE, null=True, blank=True)
    vendor_name = models.ForeignKey(vendor, on_delete=models.CASCADE, null=True, blank=True)


    class Meta:
        db_table = "inventory"



class sales_order(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    so_date = models.DateField()
    so_payment_terms = models.CharField(max_length=256, blank=True)
    so_customer_name = models.ForeignKey(customer, on_delete=models.CASCADE, null=True, blank=True)
    # so_expiry_date = models.DateField(blank=True)
    so_due_date = models.DateField(blank=True)
    # so_packaging_forwording = models.CharField(max_length=512,blank=True)
    so_supply_place = models.CharField(max_length=256,blank=True)
    so_destination = models.CharField(max_length=256,blank=True)
    so_customer_code = models.CharField(max_length=256,blank=True)
    so_dispatch = models.ForeignKey(transporter, on_delete=models.CASCADE, null=True, blank=True)
    so_sales_person = models.CharField(max_length=256,blank=True)
    so_invoice_type = models.CharField(max_length=256,blank=True)
    so_delivery_type = models.CharField(max_length=256,blank=True)
    # so_reference = models.CharField(max_length=256,blank=True)
    so_buyer_order_no = models.CharField(max_length=256,blank=True)
    so_buyer_order_date = models.CharField(max_length=256,blank=True)
    so_shipping_address = models.CharField(max_length=256,blank=True,null=True)
    # so_freight = models.CharField(max_length=255,blank=True)
    so_total = models.CharField(max_length=255,blank=True)
    so_dc_no_1 = models.CharField(max_length=255,blank = True)
    so_dc_date_1 = models.CharField(max_length=255,blank = True)
    so_dc_no_2 = models.CharField(max_length=255,blank = True)
    so_dc_date_2 = models.CharField(max_length=255,blank = True)
    so_dc_no_3 = models.CharField(max_length=255,blank = True)
    so_dc_date_3 = models.CharField(max_length=255,blank = True)
    so_dc_no_4 = models.CharField(max_length=255,blank = True)
    so_dc_date_4 = models.CharField(max_length=255,blank = True)
    so_invoce_no_1 = models.CharField(max_length=255,blank = True)
    so_invoce_date_1 = models.CharField(max_length=255,blank = True)
    so_invoce_no_2 = models.CharField(max_length=255,blank = True)
    so_invoce_date_2 = models.CharField(max_length=255,blank = True)
    so_invoce_no_3 = models.CharField(max_length=255,blank = True)
    so_invoce_date_3 = models.CharField(max_length=255,blank = True)
    so_invoce_no_4 = models.CharField(max_length=255,blank = True)
    so_invoce_date_4 = models.CharField(max_length=255,blank = True)
    so_ewaybill_no_1 = models.CharField(max_length=255,blank = True)
    so_ewaybill_no_2 = models.CharField(max_length=255,blank = True)
    so_ewaybill_no_3 = models.CharField(max_length=255,blank = True)
    so_ewaybill_no_4 = models.CharField(max_length=255,blank = True)
    so_sub_total = models.CharField(max_length=255,blank=True)
    so_cgstper = models.CharField(max_length=255,blank=True)
    so_cgstval = models.CharField(max_length=255,blank=True)
    so_sgstper = models.CharField(max_length=255,blank=True)
    so_sgstval = models.CharField(max_length=255,blank=True)
    so_igstper = models.CharField(max_length=255,blank=True)
    so_igstval = models.CharField(max_length=255,blank=True)
    so_adjustment = models.CharField(max_length=255,blank=True)
    so_sale_of_good = models.CharField(max_length=255,blank=True)
    so_note = models.TextField(blank=True)
    gst_option = models.CharField(max_length=255,blank=True)
    # so_packaging_forwording_amount = models.CharField(max_length=512,blank=True)
    # so_packaging_forwording_percentage = models.CharField(max_length=512,blank=True)
    # so_freight_amount = models.CharField(max_length=255,blank=True)
    # so_freight_percentage = models.CharField(max_length=255,blank=True)
    so_packaging_forwording_amount = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True
    )
    so_packaging_forwording_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True
    )
    so_freight_amount = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True
    )
    so_freight_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True
    )
    so_packaging_forwording_percentage_amt = models.CharField(max_length=512,blank=True)
    so_freight_percentage_amt = models.CharField(max_length=255,blank=True)
    so_total_amt_word = models.CharField(max_length=250,blank=True)
    so_number = models.CharField(max_length=250,blank=True)
    so_packaging_forwording_amt_amt = models.CharField(max_length=512,blank=True,null=True)
    so_freight_amt_amt = models.CharField(max_length=255,blank=True,null=True)
    so_order_confirmation_no = models.CharField(max_length=255,blank=True,null=True)

    



class sales_order_items(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    so_item_code = models.CharField(max_length=256)
    so_description_goods = models.CharField(max_length=256)
    so_godown = models.CharField(max_length=256,null=True,blank=True)
    so_hsn = models.CharField(max_length=256)
    so_qantity = models.CharField(max_length=256)
    so_uom = models.CharField(max_length=256)
    so_unit_price = models.CharField(max_length=256)
    so_discount = models.CharField(max_length=256)
    so_tax_rate = models.CharField(max_length=125)
    so_tax_amount = models.CharField(max_length=125)
    so_total = models.CharField(max_length=255)
    so_sales_order_id = models.CharField(max_length=255)
    date = models.DateField(null=True)



class delivery_challan(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    dc_date = models.DateField()
    dc_payment_terms = models.CharField(max_length=256, blank=True)
    dc_customer_name = models.ForeignKey(customer, on_delete=models.CASCADE, null=True, blank=True)
    dc_type = models.CharField(max_length=256, blank=True)
    # dc_expiry_date = models.DateField(blank=True)
    dc_supply_place = models.CharField(max_length=256,blank=True)
    dc_dispatch = models.ForeignKey(transporter, on_delete=models.CASCADE, null=True, blank=True)
    dc_sales_order_no = models.CharField(max_length=256,blank=True)
    dc_delivery_type = models.CharField(max_length=256,blank=True)
    dc_customer_code = models.CharField(max_length=256,blank=True)
    dc_buyer_order_no = models.CharField(max_length=256,blank=True)
    dc_buyer_order_date = models.DateField()
    dc_shipping_address = models.CharField(max_length=256,blank=True)
    dc_destination = models.CharField(max_length=256,blank=True)
    dc_sales_person = models.CharField(max_length=256,blank=True)
    dc_landing_LR_RR_No = models.CharField(max_length=255,blank=True)
    dc_sub_total = models.CharField(max_length=255,blank=True)
    dc_cgstper = models.CharField(max_length=255,blank=True)
    dc_cgstval = models.CharField(max_length=255,blank=True)
    dc_sgstper = models.CharField(max_length=255,blank=True)
    dc_sgstval = models.CharField(max_length=255,blank=True)
    dc_igstper = models.CharField(max_length=255,blank=True)
    dc_igstval = models.CharField(max_length=255,blank=True)
    dc_adjustment = models.CharField(max_length=255,blank=True)
    dc_sale_of_good = models.CharField(max_length=255,blank=True)
    dc_note = models.TextField(blank=True)
    dc_total = models.CharField(max_length=255,blank=True)
    gst_option = models.CharField(max_length=255,blank=True)
    # dc_packaging_forwording_amount = models.CharField(max_length=512,blank=True)
    # dc_packaging_forwording_percentage = models.CharField(max_length=512,blank=True)
    # dc_freight_amount = models.CharField(max_length=255,blank=True)
    # dc_freight_percentage = models.CharField(max_length=255,blank=True)
    dc_packaging_forwording_amount = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True    
    )
    dc_packaging_forwording_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True
    )
    dc_freight_amount = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True
    )    
    dc_freight_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True   
    )
    totalamt_word = models.CharField(max_length=250,blank=True)
    dc_packaging_forwording_percentage_amt = models.CharField(max_length=512,blank=True)
    dc_freight_percentage_amt = models.CharField(max_length=255,blank=True)
    dc_number = models.CharField(max_length=255,blank=True)
    dc_packaging_forwording_amt_amt = models.CharField(max_length=512,blank=True,null=True)
    dc_freight_amt_amt = models.CharField(max_length=255,blank=True,null=True)


class delivery_challan_items(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    dc_item_code = models.CharField(max_length=256)
    dc_description_goods = models.CharField(max_length=256)
    dc_hsn = models.CharField(max_length=256)
    dc_qantity = models.CharField(max_length=256)
    dc_uom = models.CharField(max_length=256)
    dc_unit_price = models.CharField(max_length=256)
    dc_discount = models.CharField(max_length=256)
    dc_tax_rate = models.CharField(max_length=125)
    dc_tax_amount = models.CharField(max_length=125)
    dc_total = models.CharField(max_length=255)
    delivery_challan_id = models.CharField(max_length=255)




class Invoice(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    invoice_date = models.DateField(blank=True)
    invoice_payment_terms = models.CharField(max_length=256, blank=True)
    invoice_customer_name = models.ForeignKey(delivery_challan, on_delete=models.CASCADE, null=True, blank=True)
    invoice_customer_name_customer = models.ForeignKey(customer, on_delete=models.CASCADE, null=True, blank=True)
    invoice_due_date = models.DateField(blank=True)
    invoice_eway_bill_no = models.CharField(max_length=256, blank=True)
    invoice_supply_place = models.CharField(max_length=256,blank=True)
    invoice_delivery_no = models.CharField(max_length=256,blank=True)
    in_customer_code = models.CharField(max_length=256,blank=True)
    invoice_destination = models.CharField(max_length=256,blank=True)
    invoice_landing_LR_RR_No = models.CharField(max_length=255,blank=True)
    invoice_dispatch = models.ForeignKey(transporter, on_delete=models.CASCADE, null=True, blank=True)
    invoice_sales_person = models.CharField(max_length=256,blank=True)
    invoice_format_type = models.CharField(max_length=256,blank=True)
    invoice_vehicle_no = models.CharField(max_length=256,blank=True)
    invoice_gst_no = models.CharField(max_length=256,blank=True)
    invoice_term_of_delivery = models.CharField(max_length=256,blank=True)
    invoice_buyer_order_no = models.CharField(max_length=256,blank=True)
    invoice_buyer_order_date = models.DateField(blank=True)
    invoice_shipping_address = models.CharField(max_length=256,blank=True)
    # invoice_freight = models.CharField(max_length=255,blank=True)
    invoice_sub_total = models.CharField(max_length=255,blank=True)
    invoice_cgstper = models.CharField(max_length=255,blank=True)
    invoice_cgstval = models.CharField(max_length=255,blank=True)
    invoice_sgstper = models.CharField(max_length=255,blank=True)
    invoice_sgstval = models.CharField(max_length=255,blank=True)
    invoice_igstper = models.CharField(max_length=255,blank=True)
    invoice_igstval = models.CharField(max_length=255,blank=True)
    invoice_adjustment = models.CharField(max_length=255,blank=True)
    invoice_sale_of_good = models.CharField(max_length=255,blank=True)
    invoice_note = models.TextField(blank=True)
    invoice_total = models.CharField(max_length=255,blank=True)
    invoice_due = models.CharField(max_length=255,blank=True)
    gst_option = models.CharField(max_length=255,blank=True)
    # inv_packaging_forwording_amount = models.CharField(max_length=512,blank=True)
    # inv_packaging_forwording_percentage = models.CharField(max_length=512,blank=True)
    # inv_freight_amount = models.CharField(max_length=255,blank=True)
    # inv_freight_percentage = models.CharField(max_length=255,blank=True)
    inv_packaging_forwording_amount = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True
    )
    inv_packaging_forwording_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True   
    )
    inv_freight_amount = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True
    )
    inv_freight_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True
    )
    inv_packaging_forwording_percentage_amt = models.CharField(max_length=512,blank=True)
    inv_freight_percentage_amt = models.CharField(max_length=255,blank=True)
    inv_total_amt_word = models.CharField(max_length=250,blank=True)
    inv_number = models.CharField(max_length=250,blank=True)
    inv_packaging_forwording_amt_amt = models.CharField(max_length=512,blank=True,null=True)
    inv_freight_amt_amt = models.CharField(max_length=255,blank=True,null=True)




class invoice_items(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    invoice_item_code = models.CharField(max_length=256)
    invoice_description_goods = models.CharField(max_length=256)
    invoice_hsn = models.CharField(max_length=256)
    invoice_godown = models.CharField(max_length=256,null=True,blank=True)
    invoice_qantity = models.CharField(max_length=256)
    invoice_uom = models.CharField(max_length=256)
    invoice_unit_price = models.CharField(max_length=256)
    invoice_discount = models.CharField(max_length=256)
    invoice_tax_rate = models.CharField(max_length=125)
    invoice_tax_amount = models.CharField(max_length=125)
    invoice_total = models.CharField(max_length=255)
    invoice_id = models.CharField(max_length=255)
    date = models.DateField(null=True)




class Credit_Notes(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    # custom_id = models.CharField(max_length=20, null=True,blank=True)

    cn_date = models.DateField()
    cn_invoice_no = models.CharField(max_length=256, blank=True)
    cn_customer_name = models.ForeignKey(customer, on_delete=models.CASCADE, null=True, blank=True)
    # cn_type = models.CharField(max_length=256, blank=True)
    # cn_expiry_date = models.DateField(blank=True)
    cn_supply_place = models.CharField(max_length=256,blank=True)
    cn_destination_supply = models.CharField(max_length=256,blank=True)
    cn_buyer_order_no = models.CharField(max_length=256,blank=True)
    cn_buyer_order_date = models.DateField()
    cn_dispatch = models.ForeignKey(transporter, on_delete=models.CASCADE, null=True, blank=True)
    cn_dispatch_date = models.DateField(blank=True)
    # cn_sales_order_no = models.CharField(max_length=256,blank=True)
    cn_delivery_term = models.CharField(max_length=256,blank=True)
    cn_landing_LR_RR_No = models.CharField(max_length=255,blank=True)
    cn_shipping_address = models.CharField(max_length=256,blank=True)
    # cn_freight = models.CharField(max_length=255,blank=True)
    # cn_sales_person = models.CharField(max_length=256,blank=True)
    cn_sub_total = models.CharField(max_length=255,blank=True)
    cn_cgstper = models.CharField(max_length=255,blank=True)
    cn_cgstval = models.CharField(max_length=255,blank=True)
    cn_sgstper = models.CharField(max_length=255,blank=True)
    cn_sgstval = models.CharField(max_length=255,blank=True)
    cn_igstper = models.CharField(max_length=255,blank=True)
    cn_igstval = models.CharField(max_length=255,blank=True)
    cn_adjustment = models.CharField(max_length=255,blank=True)
    # cn_sale_of_good = models.CharField(max_length=255,blank=True)
    cn_note = models.TextField(blank=True)
    cn_total = models.CharField(max_length=255,blank=True)
    cn_ser_type = models.CharField(max_length=255,blank=True)
    gst_option = models.CharField(max_length=255,blank=True)
    # cn_packaging_forwording_amount = models.CharField(max_length=512,blank=True)
    # cn_packaging_forwording_percentage = models.CharField(max_length=512,blank=True)
    # cn_freight_amount = models.CharField(max_length=255,blank=True)
    # cn_freight_percentage = models.CharField(max_length=255,blank=True)
    cn_packaging_forwording_amount = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True      
    )
    cn_packaging_forwording_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True
    )
    cn_freight_amount = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True
    )
    cn_freight_percentage = models.DecimalField(    
        max_digits=5, decimal_places=2, blank=True, null=True
    )
    cn_packaging_forwording_percentage_amt = models.CharField(max_length=512,blank=True)
    cn_freight_percentage_amt = models.CharField(max_length=255,blank=True)
    cn_total_amt_word = models.CharField(max_length=250,blank=True)
    cn_packaging_forwording_amt_amt = models.CharField(max_length=512,blank=True,null=True)
    cn_freight_amt_amt = models.CharField(max_length=255,blank=True,null=True)


    # def save(self, *args, **kwargs):
    #     if not self.custom_id:
    #         if self.cn_ser_type == 'Manufacturing':
    #             prefix = 'M'
    #         else:
    #             prefix = 'L'
    #         latest_id = Credit_Notes.objects.filter(cn_ser_type=self.cn_ser_type).order_by('-id').first()
    #         if latest_id:
    #             latest_number = int(latest_id.custom_id.split('-')[1])
    #         else:
    #             latest_number = 0            
    #         new_id = f"{prefix}-{latest_number + 1}"
    #         self.custom_id = new_id
    #     super().save(*args, **kwargs)




class credit_notes_items(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    cn_item_code = models.CharField(max_length=256)
    cn_description_goods = models.CharField(max_length=256)
    cn_godown = models.CharField(max_length=256,null=True,blank=True)
    cn_hsn = models.CharField(max_length=256)
    cn_qantity = models.CharField(max_length=256)
    cn_uom = models.CharField(max_length=256)
    cn_unit_price = models.CharField(max_length=256)
    cn_discount = models.CharField(max_length=256)
    cn_tax_rate = models.CharField(max_length=125)
    cn_tax_amount = models.CharField(max_length=125)
    cn_total = models.CharField(max_length=255)
    credit_notes_id = models.CharField(max_length=255)



class Purchase_order(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    po_date = models.DateField()
    po_vendor_code = models.CharField(max_length=256, blank=True)
    po_vendor_name = models.ForeignKey(vendor, on_delete=models.CASCADE, null=True, blank=True)
    po_payment_terms = models.CharField(max_length=256, blank=True)
    po_delivery_date = models.DateField(blank=True)
    po_delivery_type = models.CharField(max_length=256,blank=True)
    po_source_supply = models.CharField(max_length=256,blank=True)
    po_destination= models.CharField(max_length=256,blank=True)
    po_dispatch = models.ForeignKey(transporter, on_delete=models.CASCADE, null=True, blank=True)
    # po_dispatch_date = models.DateField(blank=True)
    # po_freight = models.CharField(max_length=255,blank=True)
    # po_sales_person = models.CharField(max_length=256,blank=True)
    po_sub_total = models.CharField(max_length=255,blank=True)
    po_cgstper = models.CharField(max_length=255,blank=True)
    po_cgstval = models.CharField(max_length=255,blank=True)
    po_sgstper = models.CharField(max_length=255,blank=True)
    po_sgstval = models.CharField(max_length=255,blank=True)
    po_igstper = models.CharField(max_length=255,blank=True)
    po_igstval = models.CharField(max_length=255,blank=True)
    po_adjustment = models.CharField(max_length=255,blank=True)
    # po_sale_of_good = models.CharField(max_length=255,blank=True)
    po_note = models.TextField(blank=True)
    po_total = models.CharField(max_length=255,blank=True)
    gst_option = models.CharField(max_length=255,blank=True)
    # po_packaging_forwording_amount = models.CharField(max_length=512,blank=True)
    # po_packaging_forwording_percentage = models.CharField(max_length=512,blank=True)
    # po_freight_amount = models.CharField(max_length=255,blank=True)
    # po_freight_percentage = models.CharField(max_length=255,blank=True)
    po_packaging_forwording_amount = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True
    )   
    po_packaging_forwording_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True       
    )
    po_freight_amount = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True
    )
    po_freight_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True
    )
    po_packaging_forwording_percentage_amt = models.CharField(max_length=512,blank=True)
    po_freight_percentage_amt = models.CharField(max_length=255,blank=True)
    po_total_amt_word = models.CharField(max_length=250,blank=True)
    po_packaging_forwording_amt_amt = models.CharField(max_length=512,blank=True,null=True)
    po_freight_amt_amt = models.CharField(max_length=255,blank=True,null=True)

    po_price = models.CharField(max_length=250,blank=True,null=True)
    po_test_certificate = models.CharField(max_length=250,blank=True,null=True)
    po_warranty_certificate = models.CharField(max_length=250,blank=True,null=True)
    po_coc = models.CharField(max_length=250,blank=True,null=True)
    po_delivery = models.CharField(max_length=250,blank=True,null=True)
    po_payment = models.CharField(max_length=250,blank=True,null=True)
    po_quotation = models.CharField(max_length=250,blank=True,null=True)
    po_quo_date = models.CharField(max_length=250,blank=True,null=True)
    po_no = models.CharField(max_length=250,blank=True,null=True)








class purchase_order_items(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    po_item_code = models.CharField(max_length=256)
    po_description_goods = models.CharField(max_length=256)
    po_godown = models.CharField(max_length=256)
    po_hsn = models.CharField(max_length=256)
    po_qantity = models.CharField(max_length=256)
    po_uom = models.CharField(max_length=256)   
    po_unit_price = models.CharField(max_length=256)
    po_discount = models.CharField(max_length=256)
    po_tax_rate = models.CharField(max_length=125)
    po_tax_amount = models.CharField(max_length=125)
    po_total = models.CharField(max_length=255)
    purchase_order_id = models.CharField(max_length=255)




class Goods_received_notes(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    grn_date = models.DateField()
    grn_vendor_name = models.ForeignKey(vendor, on_delete=models.CASCADE, null=True, blank=True)
    grn_vehicle_number = models.CharField(max_length=256, blank=True)
    grn_purchase_order_no = models.CharField(max_length=256, blank=True)
    grn_purchase_order_date = models.DateField(blank=True)
    grn_invoice_no = models.CharField(max_length=256,blank=True)
    grn_invoice_date = models.DateField(blank=True)
    grn_source_supply = models.CharField(max_length=256,blank=True)
    grn_destination_of_supply= models.CharField(max_length=256,blank=True)
    grn_transporter = models.ForeignKey(transporter, on_delete=models.CASCADE, null=True, blank=True)
    # grn_dispatch_date = models.DateField(blank=True)
    grn_freight = models.CharField(max_length=255,blank=True)
    # grn_sales_person = models.CharField(max_length=256,blank=True)
    grn_sub_total = models.CharField(max_length=255,blank=True)
    grn_cgstper = models.CharField(max_length=255,blank=True)
    grn_cgstval = models.CharField(max_length=255,blank=True)
    grn_sgstper = models.CharField(max_length=255,blank=True)
    grn_sgstval = models.CharField(max_length=255,blank=True)
    grn_igstper = models.CharField(max_length=255,blank=True)
    grn_igstval = models.CharField(max_length=255,blank=True)
    grn_adjustment = models.CharField(max_length=255,blank=True)
    # grn_sale_of_good = models.CharField(max_length=255,blank=True)
    grn_note = models.TextField(blank=True)
    grn_total = models.CharField(max_length=255,blank=True)
    gst_option = models.CharField(max_length=255,blank=True)
    # grn_packaging_forwording_amount = models.CharField(max_length=512,blank=True)
    # grn_packaging_forwording_percentage = models.CharField(max_length=512,blank=True)
    # grn_freight_amount = models.CharField(max_length=255,blank=True)
    # grn_freight_percentage = models.CharField(max_length=255,blank=True)
    grn_packaging_forwording_amount = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True      
    )   
    grn_packaging_forwording_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True
    )
    grn_freight_amount = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True  
    )
    grn_freight_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True
    )
    totalamt_word = models.CharField(max_length=250,blank=True)
    grn_packaging_forwording_percentage_amt = models.CharField(max_length=512,blank=True)
    grn_freight_percentage_amt = models.CharField(max_length=255,blank=True)
    grn_packaging_forwording_amt_amt = models.CharField(max_length=512,blank=True)
    grn_freight_percentage_amt_amt = models.CharField(max_length=255,blank=True)




class good_received_note_items(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    grn_item_code = models.CharField(max_length=256)
    grn_description_goods = models.CharField(max_length=256)
    grn_hsn = models.CharField(max_length=256)
    grn_qantity = models.CharField(max_length=256)
    grn_uom = models.CharField(max_length=256)   
    grn_unit_price = models.CharField(max_length=256)
    grn_discount = models.CharField(max_length=256)
    grn_tax_rate = models.CharField(max_length=125)
    grn_tax_amount = models.CharField(max_length=125)
    grn_total = models.CharField(max_length=255)
    good_received_note_id = models.CharField(max_length=255)


class payment_received(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    payment_received_deposite = models.ForeignKey(vendor, on_delete=models.CASCADE, null=True, related_name='payment_deposite')
    payment_received_customer = models.ForeignKey(customer,on_delete=models.CASCADE, null=True)
    payment_received_date = models.DateField(null=True)
    payment_received_payment_mode = models.CharField(max_length=50, null=True)
    payment_received_mobile = models.CharField(max_length=20, null=True)
    payment_received_balance = models.CharField(max_length=50, null=True)
    payment_received_bank_charges = models.CharField(max_length=50, null=True)
    payment_received_cheque_no = models.CharField(max_length=50, null=True)
    payment_received_cheque_date = models.DateField(null=True, blank = True)
    payment_received_reference = models.CharField(max_length=50, null=True)
    payment_received_amount = models.CharField(max_length=50, null=True)
    payment_received_payment_receipt_no = models.CharField(max_length=50, null=True)
    payment_received_bank_charges = models.CharField(max_length=50, null=True)
    payment_received_note = models.TextField(null=True, blank=True)
    payment_received_payment = models.CharField(max_length=50, null=True)
    payment_received_due_amount = models.CharField(max_length=50, null=True)
    payment_received_total = models.CharField(max_length=50, null=True)
    payment_received_amount_received = models.CharField(max_length=50, null=True)
    payment_received_amount_used = models.CharField(max_length=50, null=True)
    payment_received_amount_excess = models.CharField(max_length=50, null=True)
    payment_received_bank_name = models.CharField(max_length=250, null=True)



class Account_Expense(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    ae_deposit_to = models.ForeignKey(vendor,on_delete=models.CASCADE, null=True, related_name='deposit_to')
    ae_vendor_name = models.ForeignKey(vendor,on_delete=models.CASCADE, null=True)
    ae_invoice_date = models.DateField(null=True)
    ae_gst_number = models.CharField(max_length=100, null=True)
    ae_freight = models.DecimalField(max_digits=10, decimal_places=2)
    ae_sub_total = models.CharField(max_length=100,blank=True)
    ae_cgstper = models.CharField(max_length=100,blank=True)
    ae_cgstval = models.CharField(max_length=100,blank=True)
    ae_sgstper = models.CharField(max_length=100,blank=True)
    ae_sgstval = models.CharField(max_length=100,blank=True)
    ae_igstper = models.CharField(max_length=100,blank=True)
    ae_igstval = models.CharField(max_length=100,blank=True)
    ae_adjustment = models.CharField(max_length=100,blank=True)
    ae_sale_of_good = models.CharField(max_length=100,blank=True)
    ae_note = models.TextField(blank=True)
    all_total = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    ae_invoice_no = models.CharField(max_length=256, blank=True)
    ae_cost_center = models.CharField(max_length=256, blank=True)
    ae_upload_file = models.ImageField(upload_to='acc_expence/',null=True,blank=True)
    ae_due_amount = models.CharField(max_length=125,null=True,blank=True)


class Account_Expense_Item(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    ae_item_code = models.CharField(max_length=256)
    ae_description_goods = models.CharField(max_length=256, null=True)
    ae_hsn = models.CharField(max_length=256)
    ae_sac = models.CharField(max_length=256, null=True)
    ae_qantity = models.CharField(max_length=256)
    ae_uom = models.CharField(max_length=256)
    ae_unit_price = models.CharField(max_length=256)
    ae_discount = models.CharField(max_length=256)
    ae_tax_rate = models.CharField(max_length=125)
    ae_tax_amount = models.CharField(max_length=125)
    ae_total = models.CharField(max_length=100)
    ae_quotation_id = models.CharField(max_length=100)



#######dummy expense
class acc_expense(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    ac_vendor = models.ForeignKey(vendor,on_delete=models.CASCADE, null=True)
    acc_date = models.DateField()
    acc_gst = models.CharField(max_length=255,blank=True)
    acc_freight = models.CharField(max_length=255,blank=True)
    acc_total = models.CharField(max_length=255, blank = True)
    class Meta:
        db_table = "acc_expense"


##dumy ecpense adv
class acc_expense_items(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    expense_item_code = models.CharField(max_length=256)
    expense_description_goods = models.CharField(max_length=256)
    expense_hsn = models.CharField(max_length=256)
    expense_qantity = models.CharField(max_length=256)
    expense_uom = models.CharField(max_length=256)
    expense_unit_price = models.CharField(max_length=256)
    expense_discount = models.CharField(max_length=256)
    expense_tax_rate = models.CharField(max_length=125)
    expense_tax_amount = models.CharField(max_length=125)
    expense_total = models.CharField(max_length=255)
    expense_id = models.CharField(max_length=255)

    class Meta:
        db_table = "acc_expense_items"

class payment_received_item(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    invoicedate = models.CharField(max_length=50, null = True)
    customer_name = models.ForeignKey(customer,on_delete=models.CASCADE, null=True)
    invoicenumber = models.CharField(max_length=50, null = True)
    invoiceamount = models.CharField(max_length=50, null = True)
    paymentreceivedno = models.CharField(max_length=50, null = True)
    dueamount = models.CharField(max_length=50, null = True)    
    payment = models.CharField(max_length=50, null = True)
    payment_received_id = models.CharField(max_length=50, null = True)


class Purchase_Invoice(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    purchase_invoice_date = models.DateField()
    purchase_invoice_vendor_name = models.ForeignKey(vendor, on_delete=models.CASCADE, null=True, blank=True)
    purchase_due_date = models.DateField(blank = True)
    purchase_invoice_source_supply = models.CharField(max_length=256,blank=True)
    purchase_invoice_destination_of_supply= models.CharField(max_length=256,blank=True)
    purchase_invoice_PO_no = models.CharField(max_length=256,blank=True)
    purchase_invoice_PO_date = models.DateField(blank=True)
    purchase_invoice_grn_no = models.CharField(max_length=256, blank=True)
    purchase_invoice_grn_date = models.DateField(blank=True)    
    purchase_invoice_gst_no = models.CharField(max_length=256, blank=True)
    # purchase_invoice_freight = models.CharField(max_length=255,blank=True)
    purchase_invoice_sub_total = models.CharField(max_length=255,blank=True)
    purchase_invoice_cgstper = models.CharField(max_length=255,blank=True)
    purchase_invoice_cgstval = models.CharField(max_length=255,blank=True)
    purchase_invoice_sgstper = models.CharField(max_length=255,blank=True)
    purchase_invoice_sgstval = models.CharField(max_length=255,blank=True)
    purchase_invoice_igstper = models.CharField(max_length=255,blank=True)
    purchase_invoice_igstval = models.CharField(max_length=255,blank=True)
    purchase_invoice_adjustment = models.CharField(max_length=255,blank=True)
    purchase_invoice_note = models.TextField(blank=True)
    purchase_invoice_total = models.CharField(max_length=255,blank=True)
    purchase_dispatch = models.ForeignKey(transporter, on_delete=models.CASCADE, null=True, blank=True)
    # purchase_packaging_forwording_amount = models.CharField(max_length=512,blank=True)
    # purchase_packaging_forwording_percentage = models.CharField(max_length=512,blank=True)
    # purchase_freight_amount = models.CharField(max_length=255,blank=True)
    # purchase_freight_percentage = models.CharField(max_length=255,blank=True)
    purchase_packaging_forwording_amount = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True      
    )
    purchase_packaging_forwording_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True
    )   
    purchase_freight_amount = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True
    )   
    purchase_freight_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True
    )
    gst_option= models.CharField(null=True,max_length=255)
    cn_packaging_forwording_percentage_amt = models.CharField(max_length=255,blank=True)
    cn_freight_percentage_amt = models.CharField(max_length=255,blank=True)
    cn_total_amt_word = models.CharField(max_length=255,blank=True)
    cn_packaging_forwording_amt_amt = models.CharField(max_length=255,blank=True)
    cn_freight_percentage_amt_amt = models.CharField(max_length=255,blank=True)
    pi_vendor_code = models.CharField(max_length=256, blank=True)
    purchase_invoice_no = models.CharField(max_length=256, blank=True)

    def save(self,*args,**kwargs):

        if self._state.adding:
            last_emp = Purchase_Invoice.objects.order_by('-id').first()
            if last_emp and last_emp.purchase_invoice_no:
                last_number = int(last_emp.purchase_invoice_no.split('_')[1])
            else:
                last_number = 0  # Start with 10000 if no previous employee exists
            self.purchase_invoice_no = 'PI_{:03d}'.format(last_number + 1)       
        super().save(*args,**kwargs)





class Purchase_Invoice_items(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    purchase_invoice_item_code = models.CharField(max_length=256)
    purchase_invoice_description_goods = models.CharField(max_length=256)
    purchase_invoice_hsn = models.CharField(max_length=256)
    purchase_invoice_qantity = models.CharField(max_length=256)
    purchase_invoice_uom = models.CharField(max_length=256)   
    purchase_invoice_unit_price = models.CharField(max_length=256)
    purchase_invoice_discount = models.CharField(max_length=256)
    purchase_invoice_tax_rate = models.CharField(max_length=125)
    purchase_invoice_tax_amount = models.CharField(max_length=125)
    purchase_invoice_total = models.CharField(max_length=255)
    purchase_invoice_id = models.CharField(max_length=255)
    

class Login_User(models.Model):
    username = models.CharField(max_length=256)
    email = models.EmailField(unique = True)
    password = models.CharField(max_length=256)
    is_authenticate = models.BooleanField(default=False)


class Performa_Invoice(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    custom_id = models.CharField(max_length=20, unique=True)
    invoice_date = models.DateField(blank=True)
    invoice_payment_terms = models.CharField(max_length=256, blank=True)
    invoice_customer_name = models.ForeignKey(delivery_challan, on_delete=models.CASCADE, null=True, blank=True)
    invoice_due_date = models.DateField(blank=True)
    invoice_eway_bill_no = models.CharField(max_length=256, blank=True)
    invoice_supply_place = models.CharField(max_length=256,blank=True)
    invoice_delivery_no = models.CharField(max_length=256,blank=True)
    invoice_destination = models.CharField(max_length=256,blank=True)
    invoice_landing_LR_RR_No = models.CharField(max_length=255,blank=True)
    invoice_dispatch = models.ForeignKey(transporter, on_delete=models.CASCADE, null=True, blank=True)
    invoice_sales_person = models.CharField(max_length=256,blank=True)
    invoice_format_type = models.CharField(max_length=256,blank=True)
    invoice_vehicle_no = models.CharField(max_length=256,blank=True)
    invoice_gst_no = models.CharField(max_length=256,blank=True)
    invoice_bank_name = models.CharField(max_length=256,blank=True)
    invoice_term_of_delivery = models.CharField(max_length=256,blank=True)
    invoice_buyer_order_no = models.CharField(max_length=256,blank=True)
    invoice_buyer_order_date = models.DateField(blank=True)
    invoice_shipping_address = models.CharField(max_length=256,blank=True,null=True)
    invoice_freight = models.CharField(max_length=255,blank=True)
    invoice_sub_total = models.CharField(max_length=255,blank=True)
    invoice_cgstper = models.CharField(max_length=255,blank=True)
    invoice_cgstval = models.CharField(max_length=255,blank=True)
    invoice_sgstper = models.CharField(max_length=255,blank=True)
    invoice_sgstval = models.CharField(max_length=255,blank=True)
    invoice_igstper = models.CharField(max_length=255,blank=True)
    invoice_igstval = models.CharField(max_length=255,blank=True)
    invoice_adjustment = models.CharField(max_length=255,blank=True)
    invoice_sale_of_good = models.CharField(max_length=255,blank=True)
    invoice_note = models.TextField(blank=True)
    invoice_total = models.CharField(max_length=255,blank=True)
    invoice_ser_type = models.CharField(max_length=255,blank=True)
    invoice_status = models.CharField(max_length=255, default='Received')
    invoice_due = models.CharField(max_length=255,blank=True)
    gst_option = models.CharField(max_length=255,blank=True)
    # cn_packaging_forwording_amount = models.CharField(max_length=512,blank=True)
    # cn_packaging_forwording_percentage = models.CharField(max_length=512,blank=True)
    # cn_freight_amount = models.CharField(max_length=255,blank=True)
    # cn_freight_percentage = models.CharField(max_length=255,blank=True)
    cn_packaging_forwording_amount = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True
    )
    cn_packaging_forwording_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True
    )
    cn_freight_amount = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True
    )
    cn_freight_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True
    )
    pi_number = models.CharField(max_length=255,blank=True)
    cn_packaging_forwording_percentage_amt = models.CharField(max_length=255,blank=True)
    cn_freight_percentage_amt = models.CharField(max_length=255,blank=True)
    cn_total_amt_word = models.CharField(max_length=255,blank=True)
    cn_packaging_forwording_amt_amt = models.CharField(max_length=255,blank=True)
    cn_freight_percentage_amt_amt = models.CharField(max_length=255,blank=True)
    inv_Dispatch_document_no = models.CharField(max_length=255,blank=True,null=True)
    invoice_customer = models.ForeignKey(customer, on_delete=models.CASCADE, null=True, blank=True)
    

    class Meta:
        db_table = "Performa_Invoice"


    def save(self, *args, **kwargs):
        if not self.custom_id:
            if self.invoice_ser_type == 'Manufacturing':
                prefix = 'M'
            else:
                prefix = 'L'
            latest_id = Performa_Invoice.objects.filter(custom_id__startswith=prefix).order_by('-id').first()
            # print(latest_id)
            if latest_id:
                latest_number = int(latest_id.custom_id.split('-')[1])
            else:
                latest_number = 0
            # print(latest_number)
            new_id = f"{prefix}-{latest_number + 1}"
            self.custom_id = new_id
        super().save(*args, **kwargs)



class performa_invoice_items(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    invoice_item_code = models.CharField(max_length=256)
    invoice_description_goods = models.CharField(max_length=256)
    invoice_hsn = models.CharField(max_length=256)
    invoice_sac = models.CharField(max_length=256, null=True)
    invoice_godown = models.CharField(max_length=256,null=True,blank=True)
    invoice_qantity = models.CharField(max_length=256)
    invoice_uom = models.CharField(max_length=256)
    invoice_unit_price = models.CharField(max_length=256)
    invoice_discount = models.CharField(max_length=256)
    invoice_tax_rate = models.CharField(max_length=125)
    invoice_tax_amount = models.CharField(max_length=125)
    invoice_total = models.CharField(max_length=255)
    invoice_id = models.CharField(max_length=255)
    date = models.DateField(null=True)



class Debit_Notes(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    # custom_id = models.CharField(max_length=20, unique=True)

    cn_date = models.DateField()
    cn_invoice_no = models.CharField(max_length=256, blank=True)
    cn_customer_name = models.ForeignKey(customer, on_delete=models.CASCADE, null=True, blank=True)
    # cn_type = models.CharField(max_length=256, blank=True)                                                                                                                                                                                                                                                                                                                                                                                                                
    # cn_expiry_date = models.DateField(blank=True)
    cn_supply_place = models.CharField(max_length=256,blank=True)
    cn_destination_supply = models.CharField(max_length=256,blank=True)
    cn_buyer_order_no = models.CharField(max_length=256,blank=True)
    cn_buyer_order_date = models.CharField(max_length=256,blank=True)
    cn_dispatch = models.ForeignKey(transporter, on_delete=models.CASCADE, null=True, blank=True)
    cn_dispatch_date = models.DateField(blank=True)
    # cn_sales_order_no = models.CharField(max_length=256,blank=True)
    cn_delivery_term = models.CharField(max_length=256,blank=True)
    cn_landing_LR_RR_No = models.CharField(max_length=255,blank=True)
    cn_shipping_address = models.CharField(max_length=256,blank=True)
    # cn_freight = models.CharField(max_length=255,blank=True)
    # cn_sales_person = models.CharField(max_length=256,blank=True)
    cn_sub_total = models.CharField(max_length=255,blank=True)
    cn_cgstper = models.CharField(max_length=255,blank=True)
    cn_cgstval = models.CharField(max_length=255,blank=True)
    cn_sgstper = models.CharField(max_length=255,blank=True)
    cn_sgstval = models.CharField(max_length=255,blank=True)
    cn_igstper = models.CharField(max_length=255,blank=True)
    cn_igstval = models.CharField(max_length=255,blank=True)
    cn_adjustment = models.CharField(max_length=255,blank=True)
    # cn_sale_of_good = models.CharField(max_length=255,blank=True)
    cn_note = models.TextField(blank=True)
    cn_total = models.CharField(max_length=255,blank=True)
    cn_ser_type = models.CharField(max_length=255,blank=True)
    gst_option = models.CharField(max_length=255,blank=True)
    # cn_packaging_forwording_amount = models.CharField(max_length=512,blank=True)
    # cn_packaging_forwording_percentage = models.CharField(max_length=512,blank=True)
    # cn_freight_amount = models.CharField(max_length=255,blank=True)
    # cn_freight_percentage = models.CharField(max_length=255,blank=True)
    cn_packaging_forwording_amount = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True  
    )
    cn_packaging_forwording_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True    
    )   
    cn_freight_amount = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True
    )
    cn_freight_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True    
    )
    cn_packaging_forwording_percentage_amt = models.CharField(max_length=512,blank=True)
    cn_freight_percentage_amt = models.CharField(max_length=255,blank=True)
    cn_total_amt_word = models.CharField(max_length=250,blank=True)
    cn_packaging_forwording_amt_amt = models.CharField(max_length=512,blank=True,null=True)
    cn_freight_amt_amt = models.CharField(max_length=255,blank=True,null=True)


    # def save(self, *args, **kwargs):
    #     if not self.custom_id:
    #         if self.cn_ser_type == 'Manufacturing':
    #             prefix = 'M'
    #         else:
    #             prefix = 'L'
    #         latest_id = Debit_Notes.objects.filter(cn_ser_type=self.cn_ser_type).order_by('-id').first()
    #         if latest_id:
    #             latest_number = int(latest_id.custom_id.split('-')[1])
    #         else:
    #             latest_number = 0            
    #         new_id = f"{prefix}-{latest_number + 1}"
    #         self.custom_id = new_id
    #     super().save(*args, **kwargs)




class debit_notes_items(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    cn_item_code = models.CharField(max_length=256)
    cn_description_goods = models.CharField(max_length=256)
    cn_godown = models.CharField(max_length=256,null=True,blank=True)
    cn_hsn = models.CharField(max_length=256)
    cn_qantity = models.CharField(max_length=256)
    cn_uom = models.CharField(max_length=256)
    cn_unit_price = models.CharField(max_length=256)
    cn_discount = models.CharField(max_length=256)
    cn_tax_rate = models.CharField(max_length=125)
    cn_tax_amount = models.CharField(max_length=125)
    cn_total = models.CharField(max_length=255)
    credit_notes_id = models.CharField(max_length=255)



class Leads(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    l_LS_NO = models.CharField(max_length=255, null=True,blank=True)  
    l_Lid_No =models.IntegerField(unique=True,null=True)
    company_name = models.CharField(max_length=256)
    contact_person = models.CharField(max_length=256, null=True)
    contact_number = models.CharField(max_length=256, null=True)
    email = models.EmailField(blank=True, null=True)
    status = models.CharField(max_length=256, null=True,blank=True)
    website = models.CharField(max_length=200, blank=True, null=True)
    source = models.URLField(max_length=200, blank=True, null=True)
    website_email = models.CharField(max_length=125, null=True)
    mobile  = models.CharField(max_length=20)
    old = models.CharField(max_length=255, null=True)
    inquiry = models.TextField(null=True)
    social_media = models.CharField(max_length=255, null=True)
    leads_ser_type = models.CharField(max_length=255,blank=True,null=True)
    date = models.DateField(null=True)


    class Meta:
        db_table = "Leads"



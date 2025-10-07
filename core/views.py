from django.shortcuts import render


from core.modules.Contact.customers import *
from core.modules.Dashboard.dashboard import *
from core.modules.Contact.vendor import *
from core.modules.Contact.transporter import *
from core.modules.Inventory.godown import *
from core.modules.Inventory.inventory import *
from core.modules.Masters.designation import *
from core.modules.Masters.department import *
from core.modules.Masters.leave_type import *
from core.modules.Banking.banking import *
from core.modules.HR.employee import *
from core.modules.HR.holiday import *
from core.modules.HR.employee_leaves import *
from core.modules.HR.employee_salary import *
from core.modules.Settings.company_profile import *
from core.modules.Account.voucher import *
from core.modules.Account.expense import *
from core.modules.Account.expense_advice import *
from core.modules.Account.customer_ledger import *
from core.modules.Reports.report import *



from core.modules.Sales.quotation import *
from core.modules.Sales.sales_order import *
from core.modules.Sales.payment_received import *
from core.modules.Sales.delivery_challan import *
from core.modules.Sales.invoice  import *
from core.modules.Sales.credit_notes  import *
from core.modules.Sales.debit_notes  import *

from core.modules.Purchase.Purchase.purchase_order  import *
from core.modules.Purchase.Purchase.good_received_notes  import *
from core.modules.Purchase.Purchase.purchase_invoice  import *
from core.modules.Purchase.performa_invoice  import *

from core.modules.Documents.vendor_doc import *
from core.modules.Documents.inventory_doc import *
from core.modules.Documents.customer_doc import *

from core.modules.Account.new_expense import *
from core.modules.Account.account_expense import *
from core.modules.Account.acc_expense_advice import *
from django.contrib.auth.decorators import user_passes_test

from core.modules.Leads.leads import *


from core.modules.Sales.payment_received import payment_pdf









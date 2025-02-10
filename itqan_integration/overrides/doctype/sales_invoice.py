import frappe
from frappe import _
from frappe.utils import flt, cint

import erpnext
from erpnext import get_default_company
from erpnext.accounts.utils import get_account_currency
from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice, update_linked_doc
from erpnext.setup.doctype.company.company import update_company_current_month_sales

class CustomSalesInvoice(SalesInvoice):
    def validate(self):
        super(CustomSalesInvoice, self).validate()
        self.validate_cash()
        self.calculate_outstanding_amount()

    def on_submit(self):
        self.validate_pos_paid_amount()

        if not self.auto_repeat:
            frappe.get_doc("Authorization Control").validate_approving_authority(
                self.doctype, self.company, self.base_grand_total, self
            )

        self.check_prev_docstatus()

        if self.is_return and not self.update_billed_amount_in_sales_order:
            # NOTE status updating bypassed for is_return
            self.status_updater = []

        self.update_status_updater_args()
        self.update_prevdoc_status()
        self.update_billing_status_in_dn()
        self.clear_unallocated_mode_of_payments()

        # Updating stock ledger should always be called after updating prevdoc status,
        # because updating reserved qty in bin depends upon updated delivered qty in SO
        if self.update_stock == 1:
            self.update_stock_ledger()
        if self.is_return and self.update_stock:
            update_serial_nos_after_submit(self, "items")

        # this sequence because outstanding may get -ve
        self.make_gl_entries() ### Update

        if self.update_stock == 1:
            self.repost_future_sle_and_gle()

        if not self.is_return:
            self.update_billing_status_for_zero_amount_refdoc("Delivery Note")
            self.update_billing_status_for_zero_amount_refdoc("Sales Order")
            self.check_credit_limit()

        self.update_serial_no()

        if not cint(self.is_pos) == 1 and not self.is_return:
            self.update_against_document_in_jv()

        self.update_time_sheet(self.name)

        if (
            frappe.db.get_single_value("Selling Settings", "sales_update_frequency") == "Each Transaction"
        ):
            update_company_current_month_sales(self.company)
            self.update_project()
        update_linked_doc(self.doctype, self.name, self.inter_company_invoice_reference)

        # create the loyalty point ledger entry if the customer is enrolled in any loyalty program
        if not self.is_return and not self.is_consolidated and self.loyalty_program:
            self.make_loyalty_point_entry()
        elif (
            self.is_return and self.return_against and not self.is_consolidated and self.loyalty_program
        ):
            against_si_doc = frappe.get_doc("Sales Invoice", self.return_against)
            against_si_doc.delete_loyalty_point_entry()
            against_si_doc.make_loyalty_point_entry()
        if self.redeem_loyalty_points and not self.is_consolidated and self.loyalty_points:
            self.apply_loyalty_points()

        self.process_common_party_accounting()
        self.set_status()

    def validate_cash(self):
        if not self.custom_cash_bank_account and flt(self.custom_paid_amount):
            frappe.throw(_("Cash or Bank Account is mandatory for making payment entry"))

        if self.is_return and self.custom_is_paid:
            if flt(self.custom_paid_amount) + flt(self.write_off_amount) - flt(
                self.get("rounded_total") or self.grand_total
            ) > 1 / (10 ** (self.precision("base_grand_total") + 1)):

                frappe.throw(_("""Paid amount + Write Off Amount can not be greater than Grand Total"""))

        # If the invoice is paid but the paid amount is zero then paid amount is equal grand total
        if self.custom_is_paid and not self.custom_paid_amount:
            self.custom_paid_amount = self.grand_total

        if self.custom_paid_amount:
            self.custom_base_paid_amount = flt(
                self.custom_paid_amount * self.conversion_rate, self.precision("custom_base_paid_amount")
            )

    def calculate_outstanding_amount(self):
        grand_total = self.rounded_total or self.grand_total
        base_grand_total = self.base_rounded_total or self.base_grand_total

        if(self.party_account_currency == self.currency):
            total_amount_to_pay = flt((grand_total - self.total_advance \
                - self.write_off_amount), self.precision("grand_total"))
        else:
            total_amount_to_pay = flt(
                (flt(base_grand_total, self.precision("base_grand_total")) \
                    - self.total_advance - self.base_write_off_amount),
                self.precision("base_grand_total")
            )

        if self.party_account_currency == self.currency:
            paid_amount = self.custom_paid_amount
        else: paid_amount = self.custom_base_paid_amount

        self.outstanding_amount =  flt(total_amount_to_pay - flt(paid_amount) + \
            flt(self.change_amount * self.conversion_rate), self.precision("outstanding_amount"))
    
    def make_gl_entries(self, gl_entries=None, from_repost=False):
        from erpnext.accounts.general_ledger import make_gl_entries, make_reverse_gl_entries

        auto_accounting_for_stock = erpnext.is_perpetual_inventory_enabled(self.company)
        if not gl_entries:
            gl_entries = self.get_gl_entries()

        if gl_entries:
            # if POS and amount is written off, updating outstanding amt after posting all gl entries
            update_outstanding = (
                "No"
                if (cint(self.is_pos) or cint(self.custom_is_paid) or self.write_off_account or cint(self.redeem_loyalty_points))
                else "Yes"
            )

            if self.docstatus == 1:
                make_gl_entries(
                    gl_entries,
                    update_outstanding=update_outstanding,
                    merge_entries=False,
                    from_repost=from_repost,
                )
            elif self.docstatus == 2:
                make_reverse_gl_entries(voucher_type=self.doctype, voucher_no=self.name)

            if update_outstanding == "No":
                from erpnext.accounts.doctype.gl_entry.gl_entry import update_outstanding_amt

                update_outstanding_amt(
                    self.debit_to,
                    "Customer",
                    self.customer,
                    self.doctype,
                    self.return_against if cint(self.is_return) and self.return_against else self.name,
                )

        elif self.docstatus == 2 and cint(self.update_stock) and cint(auto_accounting_for_stock):
            make_reverse_gl_entries(voucher_type=self.doctype, voucher_no=self.name)

    def get_gl_entries(self, warehouse_account=None):
        gl_entries = super(CustomSalesInvoice, self).get_gl_entries(warehouse_account)

        self.make_payment_gl_entries(gl_entries)

        return gl_entries


    def make_payment_gl_entries(self, gl_entries):
        # Make Cash GL Entries
        if cint(self.custom_is_paid) and self.custom_cash_bank_account and self.custom_paid_amount:
            bank_account_currency = get_account_currency(self.custom_cash_bank_account)
            # CASH, make payment entries
            gl_entries.append(
                self.get_gl_dict(
                    {
                        "account": self.debit_to,
                        "party_type": "Customer",
                        "party": self.customer,
                        "against": self.custom_cash_bank_account,
                        "credit": self.custom_base_paid_amount,
                        "credit_in_account_currency": self.custom_base_paid_amount
                        if self.party_account_currency == self.company_currency
                        else self.custom_paid_amount,
                        "against_voucher": self.return_against
                        if cint(self.is_return) and self.return_against
                        else self.name,
                        "against_voucher_type": self.doctype,
                        "cost_center": self.cost_center,
                        "project": self.project,
                    },
                    self.party_account_currency,
                    item=self,
                )
            )

            gl_entries.append(
                self.get_gl_dict(
                    {
                        "account": self.custom_cash_bank_account,
                        "against": self.customer,
                        "debit": self.custom_base_paid_amount,
                        "debit_in_account_currency": self.custom_base_paid_amount
                        if bank_account_currency == self.company_currency
                        else self.custom_paid_amount,
                        "cost_center": self.cost_center,
                    },
                    bank_account_currency,
                    item=self,
                )
            )


@frappe.whitelist()
def get_payment_account(mode_of_payment, company = None):
    if not company:
        company = get_default_company()

    return frappe.db.get_value("Mode of Payment Account", {
        "parent": mode_of_payment,
        "company": company
    }, "default_account")

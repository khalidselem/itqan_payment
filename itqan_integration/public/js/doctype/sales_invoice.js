{% include 'erpnext/accounts/doctype/sales_invoice/sales_invoice.js' %};
frappe.provide("itqan.accounts");


itqan.accounts.CustomSalesInvoiceController = class CustomSalesInvoiceController extends erpnext.accounts.SalesInvoiceController {
    setup() {
		super.setup();
        frappe.ui.form.on(this.frm.cscript.tax_table, "included_in_print_rate", function(frm, cdt, cdn) {
			cur_frm.cscript.set_dynamic_labels();
            cur_frm.cscript.set_dynamic_label();
			cur_frm.cscript.calculate_taxes_and_totals();
		});
        frappe.ui.form.on(this.frm.doctype, "discount_amount", function(frm) {
			frm.cscript.set_dynamic_labels();
            frm.cscript.set_dynamic_label();

			if (!frm.via_discount_percentage) {
				frm.doc.additional_discount_percentage = 0;
			}

			frm.cscript.calculate_taxes_and_totals();
		});
    }
    refresh(doc, dt, dn) {
		super.refresh(doc, dt, dn);
		this.set_dynamic_label();
	}
    currency() {
        super.currency()
		this.set_dynamic_label();
    }
    custom_is_paid() {
		this.frm.events.hide_fields(this.frm);
		if(cint(this.frm.doc.custom_is_paid)) {
			this.frm.set_value("allocate_advances_automatically", 0);
			if(!this.frm.doc.company) {
				this.frm.set_value("custom_is_paid", 0)
				frappe.msgprint(__("Please specify Company to proceed"));
			}
            if (this.frm.doc.rounded_total)
                this.frm.doc.custom_paid_amount = this.frm.doc.rounded_total 
            else this.frm.doc.custom_paid_amount = this.frm.doc.grand_total
		}
        else {
            this.frm.doc.custom_paid_amount = 0;
        }
		this.custom_calculate_outstanding_amount();
		this.frm.refresh_fields();
	}
    custom_paid_amount() {
		this.set_in_company_currency(this.frm.doc, ["custom_paid_amount"]);
		this.write_off_amount();
        this.custom_calculate_outstanding_amount();
		this.frm.refresh_fields();
	}
    custom_calculate_outstanding_amount(update_paid_amount) {
        this.calculate_paid_amount();
		if (this.frm.doc.is_return || (this.frm.doc.docstatus > 0) || this.is_internal_invoice()) return;

		frappe.model.round_floats_in(this.frm.doc, ["grand_total", "total_advance", "write_off_amount"]);
        let grand_total = this.frm.doc.rounded_total || this.frm.doc.grand_total;
        let base_grand_total = this.frm.doc.base_rounded_total || this.frm.doc.base_grand_total;

        if(this.frm.doc.party_account_currency == this.frm.doc.currency) {
            var total_amount_to_pay = flt((grand_total - this.frm.doc.total_advance
                - this.frm.doc.write_off_amount), precision("grand_total"));
        } else {
            var total_amount_to_pay = flt(
                (flt(base_grand_total, precision("base_grand_total"))
                    - this.frm.doc.total_advance - this.frm.doc.base_write_off_amount),
                precision("base_grand_total")
            );
        }

        frappe.model.round_floats_in(this.frm.doc, ["custom_paid_amount"]);
        this.set_in_company_currency(this.frm.doc, ["custom_paid_amount"]);

        if(this.frm.refresh_field){
            this.frm.refresh_field("custom_paid_amount");
            this.frm.refresh_field("custom_base_paid_amount");
        }

        let total_amount_for_payment = (this.frm.doc.redeem_loyalty_points && this.frm.doc.loyalty_amount)
            ? flt(total_amount_to_pay - this.frm.doc.loyalty_amount, precision("base_grand_total"))
            : total_amount_to_pay;
        this.set_default_payment(total_amount_for_payment, update_paid_amount);
        this.calculate_paid_amount();
        this.calculate_change_amount();

        var paid_amount = (this.frm.doc.party_account_currency == this.frm.doc.currency) ?
            this.frm.doc.custom_paid_amount : this.frm.doc.custom_base_paid_amount;

        this.frm.doc.outstanding_amount =  flt(total_amount_to_pay - flt(paid_amount) +
            flt(this.frm.doc.change_amount * this.frm.doc.conversion_rate), precision("outstanding_amount"));
    
	}
    price_list_currency() {
		super.price_list_currency()
		this.set_dynamic_label();
    }
    set_dynamic_label() {
		var company_currency = this.get_company_currency();
		this.change_form_label(company_currency);
		this.frm.refresh_fields();
	}
    change_form_label(company_currency){
        this.frm.set_currency_labels(["custom_base_paid_amount"], company_currency);

		this.frm.set_currency_labels(["custom_paid_amount"], this.frm.doc.currency);

    }
    mode_of_payment(){
        let me = this;
        if (me.frm.doc.mode_of_payment){
            frappe.call({
                "method": "itqan_integration.overrides.doctype.sales_invoice.get_payment_account",
                "args": {
                    "mode_of_payment": me.frm.doc.mode_of_payment,
                    "company": me.frm.doc.company
                },
                callback: function(r){
                    if (r.message) me.frm.set_value("custom_cash_bank_account", r.message);
                }
            })
        }
    }
}

// for backward compatibility: combine new and previous states
extend_cscript(cur_frm.cscript, new itqan.accounts.CustomSalesInvoiceController({frm: cur_frm}));

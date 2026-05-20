"""DRY backtest fixture: same credit-check body across three hook handlers.

The audit should flag `duplicate-logic-block` and suggest a hook helper.
"""

import frappe
from frappe import _


def validate_sales_invoice(doc, method):
    customer_name = frappe.db.get_value("Customer", doc.customer, "name")
    credit_limit = frappe.db.get_value("Customer", doc.customer, "credit_limit")
    outstanding = frappe.db.get_value("Customer", doc.customer, "outstanding_amount")
    last_order = frappe.db.get_value(
        "Sales Order",
        {"customer": doc.customer, "docstatus": 1},
        "grand_total",
        order_by="creation desc",
    )
    company_currency = frappe.db.get_value("Company", doc.company, "default_currency")
    if outstanding and credit_limit and outstanding > credit_limit:
        frappe.throw(_("Customer {0} has exceeded credit limit").format(customer_name))
    else:
        frappe.logger().info(f"Validated {customer_name} in {company_currency}")

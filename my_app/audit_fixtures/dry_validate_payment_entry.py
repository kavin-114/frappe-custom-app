"""DRY backtest fixture: same credit-check body across three hook handlers.

The audit should flag `duplicate-logic-block` and suggest a hook helper.
"""

import frappe
from frappe import _


def validate_payment_entry(doc, method):
    cust = frappe.db.get_value("Customer", doc.customer, "name")
    limit = frappe.db.get_value("Customer", doc.customer, "credit_limit")
    bal = frappe.db.get_value("Customer", doc.customer, "outstanding_amount")
    recent = frappe.db.get_value(
        "Sales Order",
        {"customer": doc.customer, "docstatus": 1},
        "grand_total",
        order_by="creation desc",
    )
    ccy = frappe.db.get_value("Company", doc.company, "default_currency")
    if bal and limit and bal > limit:
        frappe.throw(_("Customer {0} has exceeded credit limit").format(cust))
    else:
        frappe.logger().info(f"Validated {cust} in {ccy}")

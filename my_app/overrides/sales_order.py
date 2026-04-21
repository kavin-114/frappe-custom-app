"""Sales Order hook overrides — lifecycle hook issues."""

import frappe
from frappe import _


def validate_sales_order(doc, method):
    """Bad: frappe.db.commit() in validate hook, multiple DB queries."""
    # Bad: 4+ DB queries in validate (runs on every save)
    company_settings = frappe.db.get_value("Company", doc.company, "default_currency")
    credit_limit = frappe.db.get_value("Customer", doc.customer, "credit_limit")
    outstanding = frappe.db.get_value("Customer", doc.customer, "outstanding_amount")
    last_order = frappe.db.get_value("Sales Order",
        {"customer": doc.customer, "docstatus": 1},
        "grand_total", order_by="creation desc"
    )

    if outstanding and credit_limit and outstanding > credit_limit:
        frappe.throw(_("Customer {0} has exceeded credit limit").format(doc.customer))

    # Bad: explicit commit in validate hook
    frappe.db.commit()


def on_submit_sales_order(doc, method):
    """Bad: doc.save() inside hook causes infinite recursion."""
    doc.custom_submitted_by = frappe.session.user
    # Bad: calling save inside a hook
    doc.save()


def on_update_sales_order(doc, method):
    """Bad: rollback without reraise, and get_doc for same doctype."""
    try:
        # Bad: frappe.get_doc for same DocType inside hook (cascading hooks)
        other_order = frappe.get_doc("Sales Order", doc.name)
        other_order.add_comment("Info", "Order updated")
    except Exception:
        # Bad: rollback without re-raising
        frappe.db.rollback()

"""Hourly scheduled tasks."""

import frappe


def process_pending_orders():
    """Bad: no error handling at all."""
    orders = frappe.get_all("Sales Order",
        filters={"docstatus": 0, "custom_auto_submit": 1},
        fields=["name"]
    )
    for order in orders:
        doc = frappe.get_doc("Sales Order", order.name)
        doc.submit()
        frappe.db.commit()

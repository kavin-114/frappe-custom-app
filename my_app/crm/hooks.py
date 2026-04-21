"""CRM hooks — bad pattern: using doc_events for own custom DocType."""

import frappe
from frappe import _


def validate_custom_lead(doc, method):
    """This is a custom DocType — should use controller methods, not hooks."""
    if not doc.lead_name:
        frappe.throw(_("Lead Name is required"))

    # Bad: get_doc in hook (loads full doc on every save)
    if doc.company:
        company = frappe.get_doc("Company", doc.company)
        doc.custom_currency = company.default_currency


def on_update_custom_lead(doc, method):
    """Bad: commit in lifecycle hook."""
    frappe.db.set_value("Custom Lead", doc.name, "custom_last_updated", frappe.utils.now())
    frappe.db.commit()

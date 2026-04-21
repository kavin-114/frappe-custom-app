"""Purchase Order hook overrides — more lifecycle issues."""

import frappe
from frappe import _


def validate_purchase_order(doc, method):
    """Bad: frappe.throw() as the only statement — blocks all POs."""
    frappe.throw(_("Purchase Orders are temporarily disabled"))

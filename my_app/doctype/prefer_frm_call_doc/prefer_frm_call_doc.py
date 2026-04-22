"""Controller with a whitelisted method on the same DocType."""

import frappe
from frappe.model.document import Document


class PreferFrmCallDoc(Document):
    @frappe.whitelist()
    def compute_total(self):
        return 42

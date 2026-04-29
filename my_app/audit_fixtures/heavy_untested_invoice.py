"""Heavy DocType controller with no test file — exercises the test-coverage rule."""
from __future__ import annotations

import frappe
from frappe.model.document import Document


class HeavyUntestedInvoice(Document):
    def validate(self):
        if self.amount is None or self.amount < 0:
            frappe.throw("Amount must be non-negative")

    def before_save(self):
        self.last_modified_by = frappe.session.user

    def on_submit(self):
        frappe.db.set_value(
            "Heavy Untested Invoice", self.name, "submitted_at", frappe.utils.now()
        )

    def on_cancel(self):
        frappe.db.set_value(
            "Heavy Untested Invoice", self.name, "cancelled_at", frappe.utils.now()
        )

    @frappe.whitelist()
    def recalculate_total(self):
        return (self.amount or 0) * (1 + (self.tax_rate or 0))

    @frappe.whitelist()
    def fetch_summary(self):
        return {"name": self.name, "amount": self.amount}

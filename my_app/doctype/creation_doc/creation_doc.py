"""Phase 2 test: doc-creation-in-validate + doc-creation-in-lifecycle-without-flag-guard."""

import frappe
from frappe.model.document import Document


class CreationDoc(Document):
    def validate(self):
        # Bad: creates and inserts a separate doc on every save.
        frappe.get_doc({
            "doctype": "Activity Log",
            "subject": "Creation Doc validated",
            "content": self.name,
        }).insert()

    def on_update(self):
        # Bad: ungated creation in lifecycle hook.
        frappe.new_doc("Sync Log").insert()

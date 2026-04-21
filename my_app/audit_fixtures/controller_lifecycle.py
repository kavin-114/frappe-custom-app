"""Document subclass with a real critical issue inside a lifecycle method."""
from __future__ import annotations

import frappe
from frappe.model.document import Document


class FixtureLifecycleDoc(Document):
    def validate(self):
        """live_lifecycle_validate — critical: frappe.db.commit() in lifecycle hook."""
        # Bad: commit inside validate() breaks transaction isolation.
        frappe.db.commit()

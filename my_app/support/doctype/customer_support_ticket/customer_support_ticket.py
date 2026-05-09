"""Controller with real lifecycle hooks — used by audit fixtures that
specifically need a DocType *with* doc events (so the
get-doc-in-loop escalator does NOT escalate save-in-loop findings on
Customer Support Ticket to critical)."""
import frappe
from frappe.model.document import Document


class CustomerSupportTicket(Document):
    def validate(self):
        if self.priority is None:
            self.priority = 3
        if not self.status_label:
            self.status_label = "Open"

    def before_save(self):
        if self.status_label == "Resolved" and not self.resolved_at:
            self.resolved_at = frappe.utils.now_datetime()

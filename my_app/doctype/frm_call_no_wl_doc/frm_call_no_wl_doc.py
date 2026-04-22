"""Controller with a method that exists but has no @frappe.whitelist()."""

from frappe.model.document import Document


class FrmCallNoWLDoc(Document):
    # Phase 4 test: frm-call-not-whitelisted
    # Method exists but lacks decorator -> runtime "Not permitted" on click.
    def process_row(self, row_name):
        return {"ok": True, "row": row_name}

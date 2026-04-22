"""Minimal controller — intentionally does NOT define the method the JS calls."""

from frappe.model.document import Document


class FrmCallBadDoc(Document):
    # Phase 4 test: frm-call-unknown-method
    # The JS calls frm.call("do_missing_thing") but no such method exists.
    pass

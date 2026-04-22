"""Custom override for GL Entry — dangerous ledger-level override."""

import frappe


# Phase 1 test: core-ledger-override (critical)
# Overriding GL Entry risks silent financial-integrity corruption when
# ERPNext's own postings run.
class CustomGLEntry:
    def validate(self):
        # Would normally route to the real GL Entry's validate, but this class
        # replaces it entirely.
        if not self.account:
            frappe.throw("Account is required")

    def on_submit(self):
        self.apply_custom_posting_rules()

    def apply_custom_posting_rules(self):
        pass

"""Permission query targets registered via hooks.py."""

# Phase 1 test: hook-permission-query-wrong-sig
# Frappe calls permission_query_conditions targets with a SINGLE `user` arg.
# This target takes `(doc, user)` and raises TypeError at runtime.
def sales_invoice_query(doc, user):
    return ""

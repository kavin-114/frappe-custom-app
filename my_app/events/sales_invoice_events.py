"""doc_events handler for Sales Invoice — exercises Phase 2 perf rules."""

import frappe


# Phase 2 test: core-doctype-doc-event-commit + core-doc-event-perf-bottleneck
# Sales Invoice is a high-traffic DocType (in seed YAML), so:
#   - frappe.db.commit() inside the handler is a critical finding
#   - DB-call-in-loop on items is a critical perf escalation
def on_submit(doc, method):
    for row in doc.items:
        # Bad: N+1 query, amplified on every submit of every Sales Invoice
        item_doc = frappe.get_doc("Item", row.item_code)
        row.custom_item_group = item_doc.item_group

    # Bad: explicit commit in a lifecycle event on a core ledger-touching DocType
    frappe.db.commit()

"""Unreachable functions with critical-looking issues — must be SUPPRESSED."""
from __future__ import annotations

import frappe


def dead_nested_loop_query(item_codes):
    """Same shape as live_nested_loop_query, but never called or referenced anywhere."""
    for code in item_codes:
        for warehouse in frappe.get_all("Warehouse", pluck="name"):
            qty = frappe.db.get_value("Bin", {"item_code": code, "warehouse": warehouse}, "actual_qty")
            if qty:
                frappe.db.set_value("Bin", {"item_code": code, "warehouse": warehouse}, "last_seen", frappe.utils.now())


def dead_with_get_doc_loop(items):
    """Has a warning-level get-doc-in-loop. Critical-perf is suppressed; warnings stay."""
    for it in items:
        doc = frappe.get_doc("Item", it)
        doc.last_touched = frappe.utils.now()
        doc.save()

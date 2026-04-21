"""Function reachable only via frappe.call(string) — must be classified reachable_dynamic."""
from __future__ import annotations

import frappe


def live_dynamic_target(item_codes):
    """Critical issue inside a function reachable only via dynamic dispatch."""
    for code in item_codes:
        for warehouse in frappe.get_all("Warehouse", pluck="name"):
            qty = frappe.db.get_value("Bin", {"item_code": code, "warehouse": warehouse}, "actual_qty")
            if qty:
                frappe.db.set_value("Bin", {"item_code": code, "warehouse": warehouse}, "last_seen", frappe.utils.now())

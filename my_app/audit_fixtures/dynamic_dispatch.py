"""Function reachable only via frappe.call(string) — must be classified reachable_dynamic."""
from __future__ import annotations

import frappe


def live_dynamic_target(item_codes):
    """Critical issue inside a function reachable only via dynamic dispatch."""

    warehouses = frappe.get_all("Warehouse", pluck="name")

    bins = frappe.get_all(
        "Bin",
        filters={
            "item_code": ["in", item_codes],
            "warehouse": ["in", warehouses],
        },
        fields=["item_code", "warehouse", "actual_qty"],
    )

    qty_map = {
        (b.item_code, b.warehouse): b.actual_qty
        for b in bins
    }

    for code in item_codes:
        for warehouse in warehouses:
            qty = qty_map.get((code, warehouse))

            if qty:
                frappe.db.set_value(
                    "Bin",
                    {
                        "item_code": code,
                        "warehouse": warehouse,
                    },
                    "last_seen",
                    frappe.utils.now(),
                )

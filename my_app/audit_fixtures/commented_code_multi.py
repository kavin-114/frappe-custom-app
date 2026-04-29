"""Fixture for commented-code-line-multi (6+ scattered single-line code comments).

Each commented line sits adjacent to real code so the analyzer treats them as
singles, not as a block. Eight isolated singles trigger commented-code-line-multi.
"""
from __future__ import annotations

import frappe


def process_orders(orders):
    """Walks orders; interleaved with leftover commented-out single lines."""
    total = 0
    for order in orders:
        # frappe.db.commit()
        doc = frappe.get_doc("Sales Order", order)
        # frappe.log_error("touched", doc.name)
        total += doc.grand_total or 0
        # cache_key = "order:" + doc.name
        if doc.docstatus == 0:
            # frappe.publish_realtime("order_pending", doc.name)
            doc.run_method("on_update")
        # debug_payload = {"name": doc.name, "total": doc.grand_total}
        if doc.is_return:
            # frappe.db.set_value("Sales Order", doc.name, "custom_flag", 1)
            doc.add_comment("Comment", "Return processed")
        # legacy_total = doc.grand_total * 1.0
        if doc.customer == "Internal":
            # frappe.db.sql("UPDATE `tabSales Order` SET custom_audit = 1")
            pass
    return total

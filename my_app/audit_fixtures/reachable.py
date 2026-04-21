"""Reachable functions with real critical issues — must stay in the report."""
from __future__ import annotations

import frappe


def live_nested_loop_query(item_codes):
    """Real nested-loop DB query. Reachable via process_queue() in tasks/queue_processor.py."""
    for code in item_codes:
        for warehouse in frappe.get_all("Warehouse", pluck="name"):
            # Body DB call inside nested loop — genuine O(n²)
            qty = frappe.db.get_value("Bin", {"item_code": code, "warehouse": warehouse}, "actual_qty")
            if qty:
                frappe.db.set_value("Bin", {"item_code": code, "warehouse": warehouse}, "last_seen", frappe.utils.now())


def iterator_only_db_call():
    """DB call appears only in the for-loop iterator — must NOT trigger nested-loop-query."""
    for inv in frappe.get_all("Sales Invoice", filters={"status": "Paid"}, fields=["name"]):
        # Loop body has no DB calls
        pass


def get_doc_dict_constructor_in_loop(rows):
    """frappe.get_doc({dict}) creates a new document — not a lookup.
    Must NOT be flagged by get-doc-in-loop or nested-loop-query.
    Regression guard for the batch_rename.py:158 FP pattern."""
    for r in rows:
        if not frappe.db.exists("Batch", r["batch_id"]):
            frappe.get_doc({
                "doctype": "Batch",
                "batch_id": r["batch_id"],
                "item": r["item"],
            }).insert()


def assign_then_cancel_chained_in_loop(names):
    """get_doc().cancel() chained pattern — already exempted, kept as a
    regression guard alongside the new assign-then-call variant below."""
    for n in names:
        frappe.get_doc("Stock Reservation Entry", n).cancel()


def assign_then_conditional_cancel_in_loop(names):
    """Common cleanup pattern: load, check docstatus, cancel.
    Must NOT be flagged — Frappe has no bulk cancel.
    Regression guard for the department_ir.py:257 FP pattern."""
    for n in names:
        se_doc = frappe.get_doc("Stock Entry", n)
        if se_doc.docstatus == 1:
            se_doc.cancel()


def nested_loop_with_assign_then_cancel(parent_names):
    """Same assign-then-cancel pattern but in a nested loop.
    Must NOT be flagged by nested-loop-query either.
    Regression guard for jewellery_erpnext/employee_ir.py:363."""
    for pname in parent_names:
        for sre in frappe.db.get_list(
            "Stock Reservation Entry",
            {"voucher_no": pname},
            pluck="name",
        ):
            frappe.get_doc("Stock Reservation Entry", sre).cancel()

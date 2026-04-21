"""Commented-out code patterns — block + single-line + prose."""
from __future__ import annotations

import frappe


def block_commented_function():
    """Caller — the real code."""
    # def old_thing(item_code):
    #     doc = frappe.get_doc("Item", item_code)
    #     doc.disabled = 1
    #     doc.save()
    #     frappe.db.commit()
    #     return doc.name
    return None


def single_line_commits_disabled(items):
    """Caller — has interspersed commented-out frappe calls."""
    for it in items:
        # frappe.db.commit()
        doc = frappe.get_doc("Item", it)
        # frappe.log_error("touched", doc.name)
        doc.save()


def prose_comment_demo():
    """Prose comments — must NOT be flagged."""
    # this loops over invoices to compute totals for the dashboard widget
    return 1

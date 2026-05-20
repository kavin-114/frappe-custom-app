"""Real implementation of a scheduled task, re-exported through tasks/__init__.py.

See tasks/__init__.py for the re-export, and hooks.py for the shortened
dotted path that hits the FP path in the resolver.
"""
from __future__ import annotations

import frappe


def reexported_scheduled_task() -> None:
    """Genuine scheduler target — resolver must follow tasks/__init__.py's
    re-export back to this file.

    Wired as `my_app.tasks.reexported_scheduled_task` (short form) in
    hooks.py. The current resolver lands on __init__.py, finds only an
    ImportFrom, and (incorrectly) reports scheduler-missing-function.
    """
    try:
        items = frappe.get_all("Item", filters={"disabled": 0}, pluck="name", limit=50)
        for name in items:
            frappe.db.set_value("Item", name, "custom_last_touched", frappe.utils.now())
    except Exception:
        frappe.log_error("reexported_scheduled_task failed")

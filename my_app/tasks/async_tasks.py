"""Regression fixture: scheduler-missing-function MUST NOT fire on
async def functions.

The current resolver (engine/hook_analyzer.py::analyze_scheduler) walks
the target module's AST and matches only `ast.FunctionDef` against the
dotted-path tail. `ast.AsyncFunctionDef` is invisible to it, so any
async scheduler task is reported as missing.

Wired in hooks.py: scheduler_events["hourly"] → my_app.tasks.async_tasks.refresh_async_index
"""
from __future__ import annotations

import frappe


async def refresh_async_index() -> None:
    """Real async scheduler task — must be discoverable by the resolver."""
    items = frappe.get_all("Item", filters={"is_stock_item": 1}, pluck="name")
    for name in items:
        frappe.db.set_value("Item", name, "custom_last_indexed", frappe.utils.now())

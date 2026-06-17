"""Audit fixture: Script Report helper reachability (no dead-code false positive).

Frappe imports a Script Report's ``<name>/<name>.py`` module and calls
``execute(filters)`` by name when the report runs, so there is no user-code
reference for static analysis to follow. The helper functions reached only
via direct calls from ``execute()`` must therefore be treated as reachable:
the reachability index seeds ``execute`` as an entry point so the call graph
rooted there (``execute -> get_hierarchical_scores -> get_employee_list ->
_fetch_employees_active``) is walked.

Modelled on the taskstream ``work_item_score_board`` report (UAT 2026-06-17),
where ``get_employee_list`` was wrongly flagged "Unused function".

Rule IDs exercised / expected verdict:
- unused-function (code-quality, info) — MUST NOT fire on
  ``get_hierarchical_scores``, ``get_employee_list``, or
  ``_fetch_employees_active``. They are reachable from the ``execute()``
  Script Report entry point even though their bare names appear nowhere as
  an import or string literal.

This file is intentionally clean of critical findings (no string-interpolated
SQL, no query inside a loop) so it does not perturb the critical-section
golden — its whole purpose is the negative on ``unused-function``.
"""
from __future__ import annotations

import frappe


def execute(filters: dict | None = None) -> tuple[list, list]:
    filters = filters or {}
    columns = [
        {"label": "Employee", "fieldname": "employee", "fieldtype": "Link", "options": "Employee"},
        {"label": "Manager", "fieldname": "reports_to", "fieldtype": "Link", "options": "Employee"},
        {"label": "Score", "fieldname": "total_score", "fieldtype": "Int"},
    ]
    rows = get_hierarchical_scores([], [], filters.get("user"))
    return columns, rows


def get_hierarchical_scores(base_rows, cycle_dates, user):
    """Reached only via a direct call from execute() — never imported."""
    stats_by_user: dict = {}
    employee_to_user, display_by_name, reports_to_by_employee, _children = get_employee_list(stats_by_user)
    rows = []
    for employee, uid in employee_to_user.items():
        rows.append(
            {
                "employee": display_by_name.get(employee, employee),
                "reports_to": reports_to_by_employee.get(employee),
                "total_score": stats_by_user.get(uid, {}).get("total_score", 0),
            }
        )
    return rows


def get_employee_list(stats_by_user=None):
    """Reached only via a direct call from get_hierarchical_scores()."""
    employee_to_user, display_by_name, reports_to_by_employee, children_by_manager = _fetch_employees_active()
    if stats_by_user is not None:
        for uid in employee_to_user.values():
            stats_by_user.setdefault(uid, {"total_score": 0, "work_item_count": 0})
    return employee_to_user, display_by_name, reports_to_by_employee, children_by_manager


def _fetch_employees_active():
    """Reached only via a direct call from get_employee_list()."""
    employees = frappe.get_list(
        "Employee",
        filters={"status": "Active"},
        fields=["name", "employee_name", "user_id", "reports_to"],
    )
    employee_to_user = {e["name"]: e.get("user_id") for e in employees}
    display_by_name = {e["name"]: e.get("employee_name") for e in employees}
    reports_to_by_employee = {e["name"]: e.get("reports_to") for e in employees}
    children_by_manager: dict = {}
    for emp in employees:
        children_by_manager.setdefault(emp.get("reports_to"), []).append(emp["name"])
    return employee_to_user, display_by_name, reports_to_by_employee, children_by_manager

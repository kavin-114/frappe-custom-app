"""Audit fixture: Script Report anti-patterns.

Frappe calls `execute(filters)` on every Script Report. The filters dict
is user-controlled — anything that lands in SQL must be parameterised.

Proposed rule IDs:
- report-sql-injection-in-filters    (critical) — values from `filters` are
  concatenated into the SQL string instead of passed as %s parameters.
- report-no-permission-check         (warning) — `execute()` has no
  `has_permission` check on the underlying DocType, allowing users who
  can run reports to read rows they cannot read individually.
- report-get-all-bypass              (warning) — `frappe.get_all` (which
  bypasses doctype-level perms) used to fetch report rows; should be
  `frappe.get_list`.
"""
from __future__ import annotations

import frappe


def execute(filters: dict | None = None) -> tuple[list, list]:
    """Bad: SQL-injection via f-string, no permission check."""
    filters = filters or {}
    company = filters.get("company", "")
    status = filters.get("status", "Unpaid")

    columns = [
        {"label": "Invoice", "fieldname": "name", "fieldtype": "Link", "options": "Sales Invoice"},
        {"label": "Customer", "fieldname": "customer", "fieldtype": "Link", "options": "Customer"},
        {"label": "Outstanding", "fieldname": "outstanding_amount", "fieldtype": "Currency"},
    ]

    # Bad: company + status interpolated into the SQL string.
    rows = frappe.db.sql(
        f"""
        SELECT name, customer, outstanding_amount
        FROM `tabSales Invoice`
        WHERE company = '{company}'
          AND status = '{status}'
        ORDER BY outstanding_amount DESC
        """,
        as_dict=True,
    )

    # Bad: get_all bypasses Sales Invoice doctype permissions.
    overdue = frappe.get_all(
        "Sales Invoice",
        filters={"status": "Overdue"},
        fields=["name"],
        pluck="name",
    )
    for r in rows:
        r["overdue_flag"] = r["name"] in overdue

    return columns, rows


def execute_safe(filters: dict | None = None) -> tuple[list, list]:
    """Counter-example: parameterised SQL + permission gate + get_list."""
    filters = filters or {}
    frappe.has_permission("Sales Invoice", throw=True)

    columns = [
        {"label": "Invoice", "fieldname": "name", "fieldtype": "Link", "options": "Sales Invoice"},
        {"label": "Customer", "fieldname": "customer", "fieldtype": "Link", "options": "Customer"},
        {"label": "Outstanding", "fieldname": "outstanding_amount", "fieldtype": "Currency"},
    ]
    rows = frappe.db.sql(
        """
        SELECT name, customer, outstanding_amount
        FROM `tabSales Invoice`
        WHERE company = %(company)s
          AND status = %(status)s
        ORDER BY outstanding_amount DESC
        """,
        {"company": filters.get("company", ""), "status": filters.get("status", "Unpaid")},
        as_dict=True,
    )
    return columns, rows
